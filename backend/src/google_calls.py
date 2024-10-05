import os
import base64
import requests
import google.auth
import google.auth.transport.requests
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account
from google.auth import default

# Constants
PROJECT_ID = "selfcareassistant" #This needs to be defined in .env as GCP_PROJECT_ID
LOCATION = "us-central1" #Change to GCP_LOCATION
ENDPOINT = "us-central1-aiplatform.googleapis.com" #Construct this from location
MODEL_ID = "meta/llama-3.2-90b-vision-instruct-maas" #This is ok

def get_access_token():
    """Get and refresh the access token."""
    try:
        # Set the path to your service account JSON file
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'selfcareassistant-99a02733eae9.json'
        
        creds, _ = default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        
        return creds.token
    except DefaultCredentialsError as e:
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
    Captions an image using Google Cloud AI Platform.
    
    Args:
    image_path (str): Path to the image file.
    custom_prompt (str, optional): Custom prompt for the model. If None, a default prompt is used.
    
    Returns:
    str: The generated caption for the image.
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
    image_path = "mystery.jpeg"
    caption = caption_image(image_path)
    print(f"Image Caption: {caption}")