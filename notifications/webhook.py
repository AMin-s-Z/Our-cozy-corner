import requests
import json
import logging
from django.conf import settings

# Setup logger
logger = logging.getLogger(__name__)

def send_telegram_notification(user_id, message, link=None):
    """
    Send notification to Telegram via webhook and n8n
    
    Args:
        user_id: ID of the recipient user
        message: Notification message
        link: Optional link to redirect the user
        
    Returns:
        Success or failure of sending
    """
    try:
        # Get webhook URL from project settings
        webhook_url = getattr(settings, 'N8N_WEBHOOK_URL', None)
        
        if not webhook_url:
            logger.warning("N8N_WEBHOOK_URL is not set in settings, skipping Telegram notification")
            return False
            
        # Prepare data for sending
        payload = {
            'user_id': user_id,
            'message': message,
            'link': link,
            'platform': 'telegram'
        }
        
        # Send request to webhook
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully sent notification to Telegram for user {user_id}")
            return True
        else:
            logger.error(f"Failed to send notification to Telegram. Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        logger.exception(f"Error sending notification to Telegram: {str(e)}")
        return False