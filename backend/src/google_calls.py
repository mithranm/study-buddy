import os
import base64
import requests
import google.auth
import google.auth.transport.requests
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account
from google.auth import default
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
if not PROJECT_ID:
    raise ValueError("GCP_PROJECT_ID environment variable is not set")
LOCATION = os.getenv("GCP_LOCATION")
if not LOCATION:
    raise ValueError("GCP_LOCATION environment variable is not set")
ENDPOINT = f"{LOCATION}-aiplatform.googleapis.com"
MODEL_ID = "meta/llama-3.2-90b-vision-instruct-maas"

# Construct the path to the secrets directory
SECRETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'secrets'))

def get_access_token():
    """Get and refresh the access token."""
    try:
        # Get the filename of the service account JSON file from environment variable
        secret_filename = os.getenv("GCP_SECRET_PATH")
        if not secret_filename:
            raise ValueError("GCP_SECRET_PATH environment variable is not set")
        
        # Construct the full path to the secret file
        secret_path = os.path.join(SECRETS_DIR, secret_filename)
        
        if not os.path.exists(secret_path):
            raise FileNotFoundError(f"GCP secret file not found at {secret_path}")
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = secret_path
        
        creds, _ = default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        
        return creds.token
    except (DefaultCredentialsError, ValueError, FileNotFoundError) as e:
        print(f"Error with credentials: {e}")
        return None

def encode_image(image_path):
    """Encode the image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_image(image_path: str, prompt: str) -> str:
    """Processes an image using Google Cloud AI Platform."""
    try:
        access_token = get_access_token()
        if not access_token:
            return "Failed to obtain access token."
        
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

        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()

        if response.status_code == 200 and 'choices' in response_json:
            return response_json['choices'][0]['message']['content']
        else:
            print(f"Error: {response.status_code}, {response_json}")
            return None

    except Exception as e:
        print(f"Error processing image: {e}")
        return None

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
        return "Image file not found."

    # Prepare the prompt
    default_prompt = "Describe this image in detail. What do you see?"
    prompt = custom_prompt if custom_prompt else default_prompt

    # Process the image
    caption = process_image(image_path, prompt)
    return caption if caption else "Failed to generate a caption."

# Example usage
if __name__ == "__main__":
    image_path = "/Users/mithranmohanraj/Documents/study-buddy/backend/test_images/mystery.jpeg"
    caption = caption_image(image_path)
    print(f"Image Caption: {caption}")