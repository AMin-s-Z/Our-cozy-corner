# Generated by Django 5.2.4 on 2025-07-12 19:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rewards", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="reward",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "جایزه",
                "verbose_name_plural": "جوایز",
            },
        ),
        migrations.AlterModelOptions(
            name="rewardcategory",
            options={
                "ordering": ["name"],
                "verbose_name": "دسته\u200cبندی جایزه",
                "verbose_name_plural": "دسته\u200cبندی\u200cهای جوایز",
            },
        ),
        migrations.AlterField(
            model_name="reward",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="rewards",
                to="rewards.rewardcategory",
                verbose_name="دسته\u200cبندی",
            ),
        ),
        migrations.AlterField(
            model_name="reward",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد"),
        ),
        migrations.AlterField(
            model_name="reward",
            name="creator",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="created_rewards",
                to=settings.AUTH_USER_MODEL,
                verbose_name="ایجاد کننده",
            ),
        ),
        migrations.AlterField(
            model_name="reward",
            name="description",
            field=models.TextField(blank=True, verbose_name="توضیحات"),
        ),
        migrations.AlterField(
            model_name="reward",
            name="recipient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="received_rewards",
                to=settings.AUTH_USER_MODEL,
                verbose_name="برای",
            ),
        ),
        migrations.AlterField(
            model_name="reward",
            name="status",
            field=models.CharField(
                choices=[("available", "قابل استفاده"), ("used", "استفاده شده")],
                default="available",
                max_length=20,
                verbose_name="وضعیت",
            ),
        ),
        migrations.AlterField(
            model_name="reward",
            name="title",
            field=models.CharField(max_length=200, verbose_name="عنوان جایزه"),
        ),
        migrations.AlterField(
            model_name="reward",
            name="used_at",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="تاریخ استفاده"
            ),
        ),
        migrations.AlterField(
            model_name="rewardcategory",
            name="icon",
            field=models.CharField(
                help_text="نام کلاس آیکون بوت\u200cاسترپ (مثال: 'bi-heart')",
                max_length=50,
                verbose_name="کلاس آیکون",
            ),
        ),
        migrations.AlterField(
            model_name="rewardcategory",
            name="name",
            field=models.CharField(max_length=100, verbose_name="نام دسته\u200cبندی"),
        ),
    ]
