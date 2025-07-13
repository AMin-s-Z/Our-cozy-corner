from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import requests
import logging

from .models import Notification, create_partner_notification
from .webhook import send_telegram_notification

# Setup logger
logger = logging.getLogger(__name__)


@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})


@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # Redirect to the link if it exists, otherwise to the notification list
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:notification_list')


@login_required
def mark_all_as_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications:notification_list')


@login_required
def test_webhook(request):
    """Test view to manually trigger a webhook notification"""
    webhook_url = getattr(settings, 'N8N_WEBHOOK_URL', 'Not configured')
    
    if request.method == 'POST':
        try:
            # Send a test notification to the partner
            result = create_partner_notification(
                user=request.user,
                message="This is a test notification from the webhook test page",
                link="/notifications/"
            )
            
            if result:
                return JsonResponse({
                    'success': True,
                    'message': 'Test notification sent successfully'
                })
            else:
                logger.error("Failed to create partner notification")
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to send test notification - no partner found'
                }, status=400)
                
        except Exception as e:
            logger.exception(f"Error in test_webhook view: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error sending test notification: {str(e)}'
            }, status=500)
    
    return render(request, 'notifications/test_webhook.html', {
        'webhook_url': webhook_url
    })


@login_required
def check_webhook_status(request):
    """API endpoint to check if webhook is accessible"""
    webhook_url = getattr(settings, 'N8N_WEBHOOK_URL', None)
    
    if not webhook_url:
        return JsonResponse({
            'status': 'error',
            'message': 'Webhook URL not configured',
            'is_available': False
        })
    
    try:
        # Try a simple GET request to see if the service is up
        # We'll get a 404 for the webhook URL, but that's expected since we're not POSTing data
        response = requests.get(webhook_url, timeout=3)
        
        # Check if we got a response from the n8n service
        if 'n8n' in response.text.lower() or 'workflow' in response.text.lower():
            # We got a response from n8n, but the workflow might not be active
            try:
                response_data = response.json()
                if 'workflow must be active' in response_data.get('hint', '').lower():
                    return JsonResponse({
                        'status': 'warning',
                        'message': 'n8n service is up, but the workflow is not active. Please activate it in the n8n dashboard.',
                        'is_available': False
                    })
            except Exception:
                pass
            
            return JsonResponse({
                'status': 'success',
                'message': 'n8n service is responding',
                'is_available': True
            })
        
        # If we got here, the service responded but it might not be n8n
        return JsonResponse({
            'status': 'warning',
            'message': f'Service responded with status {response.status_code}, but it might not be n8n',
            'is_available': True
        })
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking webhook status: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Could not connect to webhook service: {str(e)}',
            'is_available': False
        })