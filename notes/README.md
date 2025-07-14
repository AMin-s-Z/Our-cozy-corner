# Notes App

A comprehensive note-taking system with categories, tags, reminders, and notifications.

## Features

- Rich text editing with CKEditor
- Categories and tags for organization
- File attachments
- Reminders with notifications
- Priority levels
- Pinning important notes
- Search and filtering

## Reminder System

The notes app includes a reminder system that sends notifications when:

1. A new note with a reminder is created
2. A reminder is added or updated on an existing note
3. A reminder becomes due
4. A user marks a reminder as completed

### Setting Up Automated Reminder Checks

To automatically check for due reminders and send notifications, you need to set up a scheduled task:

#### On Linux/Unix (using cron)

Add the following line to your crontab (edit with `crontab -e`):

```
*/15 * * * * cd /path/to/your/project && python manage.py check_reminders
```

This will run the reminder check every 15 minutes.

#### On Windows (using Task Scheduler)

1. Open Task Scheduler
2. Create a new Basic Task
3. Name it "OUrLove Reminder Check"
4. Set the trigger to run daily, and recur every 15 minutes
5. Set the action to start a program
6. Program/script: `python`
7. Arguments: `manage.py check_reminders`
8. Start in: `C:\path\to\your\project`

## Notification System

The reminder system integrates with the app's notification system, which:

1. Stores notifications in the database
2. Displays them in the UI
3. Optionally sends them via Telegram using n8n webhooks

### Telegram Notifications Setup

To enable Telegram notifications:

1. Ensure the `N8N_WEBHOOK_URL` is set in your settings
2. Set up an n8n workflow that:
   - Receives webhook data
   - Formats the message
   - Sends it to Telegram
3. Activate the workflow in n8n

## Usage

1. Create notes with rich text content
2. Organize them with categories and tags
3. Set reminders for time-sensitive notes
4. Receive notifications when reminders are due
5. Mark reminders as completed when done 