from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import JsonResponse, Http404, HttpResponseForbidden
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from .models import Note, NoteCategory, Tag, NoteAttachment
from .forms import (
    NoteForm, NoteAttachmentForm, 
    NoteCategoryForm, TagForm, NoteFilterForm
)
from notifications.models import create_partner_notification

def get_partner(user):
    """Helper function to get the partner of a user"""
    from core.models import User
    users = User.objects.all()
    if users.count() == 2:
        if user == users[0]:
            return users[1]
        return users[0]
    return None

@login_required
def note_list(request):
    """Display list of notes with filtering and sorting."""
    notes = Note.objects.filter(user=request.user)
    
    # Initialize filter form
    form = NoteFilterForm(request.GET, user=request.user)
    
    # Apply filters if form is valid
    if form.is_valid():
        data = form.cleaned_data
        
        if data.get('search'):
            search_query = data['search']
            notes = notes.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(snippet__icontains=search_query)
            )
            
        if data.get('category'):
            notes = notes.filter(category=data['category'])
            
        if data.get('status'):
            notes = notes.filter(status=data['status'])
            
        if data.get('priority'):
            notes = notes.filter(priority=data['priority'])
            
        if data.get('has_reminder'):
            notes = notes.filter(reminder_date__isnull=False)
            
        if data.get('is_pinned'):
            notes = notes.filter(is_pinned=True)
            
        if data.get('tags'):
            notes = notes.filter(tags__in=data['tags']).distinct()
            
        sort_by = data.get('sort_by') or '-created_at'
        notes = notes.order_by(sort_by)
    else:
        # Default sorting
        notes = notes.order_by('-is_pinned', '-created_at')
    
    # Statistics for sidebar
    stats = {
        'total_notes': notes.count(),
        'categories': NoteCategory.objects.filter(user=request.user).annotate(note_count=Count('notes')),
        'tags': Tag.objects.filter(user=request.user).annotate(note_count=Count('notes')),
        'pinned_notes': notes.filter(is_pinned=True).count(),
        'with_reminders': notes.filter(reminder_date__isnull=False).count(),
        'overdue': notes.filter(
            reminder_date__lt=timezone.now(), 
            is_reminded=False
        ).count(),
    }
    
    # Paginate results
    paginator = Paginator(notes, 10)
    page_number = request.GET.get('page', 1)
    notes_page = paginator.get_page(page_number)
    
    return render(request, 'notes/note_list.html', {
        'notes': notes_page,
        'form': form,
        'stats': stats,
        'title': _('یادداشت‌های من')
    })

@login_required
def note_create(request):
    """Create a new note."""
    if request.method == 'POST':
        form = NoteForm(request.POST, user=request.user)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Handle file attachments
            files = request.FILES.getlist('attachments')
            for uploaded_file in files:
                attachment = NoteAttachment(
                    note=note,
                    file=uploaded_file,
                    name=uploaded_file.name
                )
                attachment.save()
            
            # Send notification to partner if this note has a reminder
            if note.reminder_date:
                partner = get_partner(request.user)
                if partner:
                    message = f"{request.user.get_full_name() or request.user.username} یادداشت جدیدی با یادآوری ایجاد کرد: '{note.title}'"
                    link = note.get_absolute_url()
                    create_partner_notification(request.user, message, link)
            
            messages.success(request, _('یادداشت با موفقیت ایجاد شد.'))
            return redirect('notes:detail', slug=note.slug)
    else:
        form = NoteForm(user=request.user)
    
    return render(request, 'notes/note_form.html', {
        'form': form,
        'attachment_form': NoteAttachmentForm(),
        'title': _('ایجاد یادداشت جدید')
    })

@login_required
def note_detail(request, slug):
    """Display a single note with all details."""
    note = get_object_or_404(Note, slug=slug)
    
    # Check permissions
    if note.user != request.user:
        partner = get_partner(request.user)
        if not partner or note.user != partner:
            return HttpResponseForbidden(_('شما اجازه دسترسی به این یادداشت را ندارید.'))
    
    related_notes = Note.objects.filter(
        user=note.user
    ).exclude(id=note.id)
    
    # Get related notes by category
    if note.category:
        related_by_category = related_notes.filter(category=note.category)[:3]
    else:
        related_by_category = []
    
    # Get related notes by tags
    if note.tags.exists():
        related_by_tags = related_notes.filter(tags__in=note.tags.all()).distinct()[:3]
    else:
        related_by_tags = []
    
    return render(request, 'notes/note_detail.html', {
        'note': note,
        'attachments': note.attachments.all(),
        'related_by_category': related_by_category,
        'related_by_tags': related_by_tags,
        'title': note.title
    })

@login_required
def note_update(request, slug):
    """Update an existing note."""
    note = get_object_or_404(Note, slug=slug, user=request.user)
    old_reminder_date = note.reminder_date
    
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note, user=request.user)
        if form.is_valid():
            note = form.save()
            
            # Handle file attachments
            files = request.FILES.getlist('attachments')
            for uploaded_file in files:
                attachment = NoteAttachment(
                    note=note,
                    file=uploaded_file,
                    name=uploaded_file.name
                )
                attachment.save()
            
            # Send notification to partner if a reminder was added or changed
            if note.reminder_date and (not old_reminder_date or note.reminder_date != old_reminder_date):
                partner = get_partner(request.user)
                if partner:
                    message = f"{request.user.get_full_name() or request.user.username} یادآوری جدیدی برای یادداشت '{note.title}' تنظیم کرد."
                    link = note.get_absolute_url()
                    create_partner_notification(request.user, message, link)
            
            messages.success(request, _('یادداشت با موفقیت به‌روزرسانی شد.'))
            return redirect('notes:detail', slug=note.slug)
    else:
        form = NoteForm(instance=note, user=request.user)
    
    return render(request, 'notes/note_form.html', {
        'form': form,
        'note': note,
        'attachment_form': NoteAttachmentForm(),
        'attachments': note.attachments.all(),
        'title': _('ویرایش یادداشت')
    })

@login_required
def note_delete(request, slug):
    """Delete a note."""
    note = get_object_or_404(Note, slug=slug, user=request.user)
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, _('یادداشت با موفقیت حذف شد.'))
        return redirect('notes:list')
    
    return render(request, 'notes/note_confirm_delete.html', {
        'note': note,
        'title': _('حذف یادداشت')
    })

@login_required
@require_POST
def attachment_delete(request, pk):
    """Delete an attachment."""
    attachment = get_object_or_404(NoteAttachment, pk=pk, note__user=request.user)
    note_slug = attachment.note.slug
    attachment.delete()
    
    if request.is_ajax():
        return JsonResponse({'success': True})
    
    messages.success(request, _('فایل پیوست با موفقیت حذف شد.'))
    return redirect('notes:update', slug=note_slug)

@login_required
def category_list(request):
    """Display list of categories with counts."""
    categories = NoteCategory.objects.filter(user=request.user).annotate(note_count=Count('notes'))
    
    if request.method == 'POST':
        form = NoteCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, _('دسته‌بندی با موفقیت ایجاد شد.'))
            return redirect('notes:category_list')
    else:
        form = NoteCategoryForm()
    
    return render(request, 'notes/category_list.html', {
        'categories': categories,
        'form': form,
        'title': _('دسته‌بندی‌های یادداشت')
    })

@login_required
def category_update(request, slug):
    """Update a category."""
    category = get_object_or_404(NoteCategory, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = NoteCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _('دسته‌بندی با موفقیت به‌روزرسانی شد.'))
            return redirect('notes:category_list')
    else:
        form = NoteCategoryForm(instance=category)
    
    return render(request, 'notes/category_form.html', {
        'form': form,
        'category': category,
        'title': _('ویرایش دسته‌بندی')
    })

@login_required
def category_delete(request, slug):
    """Delete a category."""
    category = get_object_or_404(NoteCategory, slug=slug, user=request.user)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, _('دسته‌بندی با موفقیت حذف شد.'))
        return redirect('notes:category_list')
    
    return render(request, 'notes/category_confirm_delete.html', {
        'category': category,
        'title': _('حذف دسته‌بندی')
    })

@login_required
def tag_list(request):
    """Display list of tags with counts."""
    tags = Tag.objects.filter(user=request.user).annotate(note_count=Count('notes'))
    
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = request.user
            tag.save()
            messages.success(request, _('برچسب با موفقیت ایجاد شد.'))
            return redirect('notes:tag_list')
    else:
        form = TagForm()
    
    return render(request, 'notes/tag_list.html', {
        'tags': tags,
        'form': form,
        'title': _('برچسب‌های یادداشت')
    })

@login_required
def tag_update(request, slug):
    """Update a tag."""
    tag = get_object_or_404(Tag, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, _('برچسب با موفقیت به‌روزرسانی شد.'))
            return redirect('notes:tag_list')
    else:
        form = TagForm(instance=tag)
    
    return render(request, 'notes/tag_form.html', {
        'form': form,
        'tag': tag,
        'title': _('ویرایش برچسب')
    })

@login_required
def tag_delete(request, slug):
    """Delete a tag."""
    tag = get_object_or_404(Tag, slug=slug, user=request.user)
    
    if request.method == 'POST':
        tag.delete()
        messages.success(request, _('برچسب با موفقیت حذف شد.'))
        return redirect('notes:tag_list')
    
    return render(request, 'notes/tag_confirm_delete.html', {
        'tag': tag,
        'title': _('حذف برچسب')
    })

@login_required
def notes_by_category(request, slug):
    """Display notes filtered by category."""
    category = get_object_or_404(NoteCategory, slug=slug, user=request.user)
    notes = Note.objects.filter(user=request.user, category=category)
    
    # Apply basic sorting
    notes = notes.order_by('-is_pinned', '-created_at')
    
    # Paginate results
    paginator = Paginator(notes, 10)
    page_number = request.GET.get('page', 1)
    notes_page = paginator.get_page(page_number)
    
    return render(request, 'notes/notes_by_category.html', {
        'category': category,
        'notes': notes_page,
        'title': f"{_('یادداشت‌های دسته')} {category.name}"
    })

@login_required
def notes_by_tag(request, slug):
    """Display notes filtered by tag."""
    tag = get_object_or_404(Tag, slug=slug, user=request.user)
    notes = Note.objects.filter(user=request.user, tags=tag)
    
    # Apply basic sorting
    notes = notes.order_by('-is_pinned', '-created_at')
    
    # Paginate results
    paginator = Paginator(notes, 10)
    page_number = request.GET.get('page', 1)
    notes_page = paginator.get_page(page_number)
    
    return render(request, 'notes/notes_by_tag.html', {
        'tag': tag,
        'notes': notes_page,
        'title': f"{_('یادداشت‌های برچسب')} {tag.name}"
    })

@login_required
def reminders(request):
    """Display notes with reminders."""
    today = timezone.now().date()
    today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    today_end = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))
    
    # Get overdue reminders
    overdue = Note.objects.filter(
        user=request.user,
        reminder_date__lt=today_start,
        is_reminded=False
    ).order_by('reminder_date')
    
    # Get today's reminders
    today_reminders = Note.objects.filter(
        user=request.user,
        reminder_date__range=(today_start, today_end),
        is_reminded=False
    ).order_by('reminder_date')
    
    # Get upcoming reminders
    upcoming = Note.objects.filter(
        user=request.user,
        reminder_date__gt=today_end,
        is_reminded=False
    ).order_by('reminder_date')
    
    return render(request, 'notes/reminders.html', {
        'overdue': overdue,
        'today': today_reminders,
        'upcoming': upcoming,
        'title': _('یادآوری‌ها')
    })

@login_required
@require_POST
def mark_reminded(request, slug):
    """Mark a reminder as completed."""
    note = get_object_or_404(Note, slug=slug, user=request.user)
    note.is_reminded = True
    note.save()
    
    # Send notification to partner
    partner = get_partner(request.user)
    if partner:
        message = f"{request.user.get_full_name() or request.user.username} یادآوری '{note.title}' را انجام داد."
        link = note.get_absolute_url()
        create_partner_notification(request.user, message, link)
    
    if request.is_ajax():
        return JsonResponse({'success': True})
    
    messages.success(request, _('یادآوری با موفقیت انجام شد.'))
    return redirect('notes:reminders')

@login_required
def toggle_pin(request, slug):
    """Toggle pin status for a note."""
    note = get_object_or_404(Note, slug=slug, user=request.user)
    note.is_pinned = not note.is_pinned
    note.save()
    
    if request.is_ajax():
        return JsonResponse({'is_pinned': note.is_pinned})
    
    if note.is_pinned:
        messages.success(request, _('یادداشت با موفقیت سنجاق شد.'))
    else:
        messages.success(request, _('سنجاق یادداشت برداشته شد.'))
    
    return redirect('notes:detail', slug=note.slug)
