# Generated by Django 5.0.8 on 2024-09-12 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dojo', '0219_system_settings_enforce_verified_status_jira_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='system_settings',
            old_name='disclaimer',
            new_name='disclaimer_notifications',
        ),
        migrations.AlterField(
            model_name='system_settings',
            name='disclaimer_notifications',
            field=models.TextField(blank=True, default='', help_text='Include this custom disclaimer on all notifications', max_length=3000, verbose_name='Custom Disclaimer for Notifications'),
        ),
        migrations.AddField(
            model_name='system_settings',
            name='disclaimer_reports',
            field=models.TextField(blank=True, default='', help_text='Include this custom disclaimer on generated reports', max_length=5000, verbose_name='Custom Disclaimer for Reports'),
        ),
        migrations.AddField(
            model_name='system_settings',
            name='disclaimer_notes',
            field=models.TextField(blank=True, default='', help_text='Include this custom disclaimer next to input form for notes', max_length=3000, verbose_name='Custom Disclaimer for Notes'),
        ),
        migrations.AddField(
            model_name='system_settings',
            name='disclaimer_reports_forced',
            field=models.BooleanField(default=False, help_text="Disclaimer will be added to all reports even if user didn't selected 'Include disclaimer'.", verbose_name='Force to add disclaimer reports'),
        ),
    ]
