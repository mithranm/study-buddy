import os
import base64
import requests
import google.auth
import google.auth.transport.requests
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account
from google.auth import default
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from PIL import Image
import io
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Constants
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")
ENDPOINT = f"{LOCATION}-aiplatform.googleapis.com"
MODEL_ID = "meta/llama-3.2-90b-vision-instruct-maas"
SECRETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'secrets'))

# Validate environment variables
if not PROJECT_ID:
    raise ValueError("GCP_PROJECT_ID environment variable is not set")
if not LOCATION:
    raise ValueError("GCP_LOCATION environment variable is not set")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_access_token():
    """Get and refresh the access token with retry logic."""
    try:
        secret_filename = os.getenv("GCP_SECRET_PATH")
        if not secret_filename:
            raise ValueError("GCP_SECRET_PATH environment variable is not set")
        
        secret_path = os.path.join(SECRETS_DIR, secret_filename)
        
        if not os.path.exists(secret_path):
            raise FileNotFoundError(f"GCP secret file not found at {secret_path}")
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = secret_path
        
        creds, _ = default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        
        return creds.token
    except (DefaultCredentialsError, ValueError, FileNotFoundError) as e:
        logger.error(f"Error with credentials: {e}")
        raise

def encode_image(image_path):
    """Encode the image to base64 with size optimization."""
    try:
        with Image.open(image_path) as img:
            # Resize image if it's too large (adjust dimensions as needed)
            if img.width > 1000 or img.height > 1000:
                img.thumbnail((1000, 1000))
            
            # Convert to RGB if it's not
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save to bytes
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image: {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def process_image(image_path: str, prompt: str) -> str:
    """Processes an image using Google Cloud AI Platform with retry logic."""
    try:
        access_token = get_access_token()
        if not access_token:
            raise ValueError("Failed to obtain access token.")
        
        url = f"https://{ENDPOINT}/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/openapi/chat/completions"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        base64_image = encode_image(image_path)

        data = {
            "model": MODEL_ID,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}, "type": "image_url"},
                        {"text": prompt, "type": "text"}
                    ]
                }
            ],
            "max_tokens": 256,
            "temperature": 0.2,
            "top_k": 40,
            "top_p": 0.95,
            "n": 1
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)  # Added timeout
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        response_json = response.json()

        if 'choices' in response_json:
            return response_json['choices'][0]['message']['content']
        else:
            logger.error(f"Unexpected response format: {response_json}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error processing image: {e}")
        raise

def caption_image(image_path: str, custom_prompt: str = None) -> str:
    """
    Captions an image using LLama 3.2 Vision MaaS from GCP

    Args:
        image_path: an absolute path to an image, probably only jpg and png
        prompt: prompt to use for captioning
    Returns:
        str - the caption you requested
    """
    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        return "Image file not found."
    logger.info(f"Llama Vision Got image {image_path}")
    # Prepare the prompt
    default_prompt = "Describe this image in detail. What do you see?"
    prompt = custom_prompt if custom_prompt else default_prompt

    try:
        # Process the image
        caption = process_image(image_path, prompt)
        logger.info(f"Llama Vision Saw {image_path} as:\n {caption}")
        return caption if caption else "Failed to generate a caption."
    except Exception as e:
        logger.error(f"Error in caption_image: {e}")
        return f"An error occurred while processing the image: {str(e)}"

# Example usage
if __name__ == "__main__":
    image_path = "/Users/mithranmohanraj/Documents/study-buddy/backend/test_images/mystery.jpeg"
    caption = caption_image(image_path)
    print(f"Image Caption: {caption}")