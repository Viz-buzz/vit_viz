import os
import logging
import requests
from rasa.core.channels.telegram import TelegramInput
from rasa.core.agent import Agent
from rasa.core.utils import EndpointConfig
from rasa.shared.constants import DEFAULT_ENDPOINTS_PATH
from rasa.shared.constants import DEFAULT_CREDENTIALS_PATH
from sanic import Sanic
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_model():
    """Download the model from Google Drive if not present"""
    if not os.path.exists("./models"):
        os.makedirs("./models")
    
    # Check if model already exists
    if not any(fname.endswith('.tar.gz') for fname in os.listdir("./models")):
        logger.info("Downloading model from Google Drive...")
        try:
            # Get direct download link for model
            model_url = os.environ.get("MODEL_URL")
            if not model_url:
                logger.error("MODEL_URL not provided. Cannot download model.")
                return False
                
            # Download the model
            model_path = os.path.join("./models", "model.tar.gz")
            
            # Download using requests
            response = requests.get(model_url, stream=True)
            if response.status_code == 200:
                with open(model_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logger.info(f"Model downloaded successfully to {model_path}")
                return True
            else:
                logger.error(f"Failed to download model. Status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            return False
    return True

# Alternative method using gdown if direct download doesn't work
def download_model_gdown():
    """Download the model from Google Drive using gdown if not present"""
    if not os.path.exists("./models"):
        os.makedirs("./models")
    
    if not any(fname.endswith('.tar.gz') for fname in os.listdir("./models")):
        logger.info("Downloading model from Google Drive using gdown...")
        try:
            drive_id = os.environ.get("GOOGLE_DRIVE_ID")
            if not drive_id:
                logger.error("GOOGLE_DRIVE_ID not provided. Cannot download model.")
                return False
            
            model_path = os.path.join("./models", "model.tar.gz")
            import gdown
            url = f"https://drive.google.com/uc?id={drive_id}"
            gdown.download(url, model_path, quiet=False)
            
            if os.path.exists(model_path):
                logger.info(f"Model downloaded successfully to {model_path}")
                return True
            else:
                logger.error("Failed to download model from Google Drive.")
                return False
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            return False
    return True

def load_agent():
    """Load the trained Rasa model"""
    model_path = os.environ.get("RASA_MODEL", "./models")
    endpoints = EndpointConfig.read_endpoint_config(DEFAULT_ENDPOINTS_PATH)
    
    # Load trained model
    agent = Agent.load(model_path, action_endpoint=endpoints.action)
    return agent

async def start_telegram_bot(agent):
    """Start the telegram bot with the loaded agent"""
    input_channel = TelegramInput(
        # Access token from environment variable
        access_token=os.environ.get("TELEGRAM_TOKEN"),
        # Verify: True if using a webhook, False otherwise
        verify=os.environ.get("TELEGRAM_BOT_NAME", "your_bot_username")
    )
    
    app = Sanic("telegram_bot")
    
    # Setup routes
    input_channel.blueprint(on_new_message=agent.handle_message)
    app.blueprint(input_channel.blueprint)
    
    # Start the server
    port = int(os.environ.get("PORT", 5005))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )

if __name__ == "__main__":
    # Choose which download method to use - standard requests or gdown
    # Uncomment the method you prefer
    
    # Method 1: Standard requests (requires MODEL_URL env var)
    if download_model():
        # Load the agent
        agent = load_agent()
        
        # Start the telegram bot
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_telegram_bot(agent))
    else:
        logger.error("Failed to download model. Exiting...")
    
    # Method 2: Using gdown (requires GOOGLE_DRIVE_ID env var)
    # if download_model_gdown():
    #     agent = load_agent()
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(start_telegram_bot(agent))
    # else:
    #     logger.error("Failed to download model using gdown. Exiting...")
