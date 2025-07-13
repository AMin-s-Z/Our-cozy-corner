import requests
import json
import logging
import traceback
from django.conf import settings
from requests.exceptions import RequestException, Timeout, ConnectionError

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
        
        logger.info(f"Attempting to send notification to webhook: {webhook_url[:30]}...")
        
        # Send request to webhook with timeout
        try:
            response = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=5  # 5 seconds timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully sent notification to Telegram for user {user_id}")
                return True
            else:
                error_message = f"Failed to send notification to Telegram. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_message)
                
                # Check for specific n8n error about inactive workflow
                try:
                    response_data = response.json()
                    if response.status_code == 404 and 'workflow must be active' in response_data.get('hint', '').lower():
                        logger.warning("n8n workflow is not active. Please activate it in the n8n dashboard.")
                except Exception:
                    # If we can't parse the JSON, just continue with the general error
                    pass
                
                return False
                
        except Timeout:
            logger.error("Webhook request timed out after 5 seconds")
            return False
        except ConnectionError:
            logger.error(f"Connection error when sending to webhook URL: {webhook_url[:30]}...")
            return False
        except RequestException as e:
            logger.error(f"Request exception when sending webhook: {str(e)}")
            return False
            
    except Exception as e:
        logger.exception(f"Unexpected error sending notification to Telegram: {str(e)}")
        logger.error(traceback.format_exc())
        return False