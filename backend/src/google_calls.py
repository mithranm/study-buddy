import os
import uuid
import json
import requests
from google.cloud import storage
import google.auth
import google.auth.transport.requests

# Constants
BUCKET_NAME = "your-bucket-name"  # Replace with your actual bucket name
PROJECT_ID = "selfcareassistant"
LOCATION = "us-central1"
ENDPOINT = "us-central1-aiplatform.googleapis.com"
MODEL_ID = "meta/llama-3.2-90b-vision-instruct-maas"

def get_access_token():
    """Get and refresh the access token."""
    creds, project = google.auth.default()
    
    # Set the path to your service account JSON file
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'selfcareassistant-99a02733eae9.json'
    
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    return creds.token

def upload_image_to_bucket(image_path: str) -> str:
    """Uploads an image to a Google Cloud Storage bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)

        file_extension = image_path.split(".")[-1].lower()
        blob_name = f"image_{uuid.uuid4()}.{file_extension}"

        blob = bucket.blob(blob_name)
        blob.upload_from_filename(image_path)

        image_uri = f"gs://{BUCKET_NAME}/{blob_name}"
        return image_uri

    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

def process_image(image_uri: str, prompt: str) -> str:
    """Processes an image using Google Cloud AI Platform."""
    try:
        access_token = get_access_token()
        
        url = f"https://{ENDPOINT}/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/openapi/chat/completions"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "model": MODEL_ID,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"image_url": {"url": image_uri}, "type": "image_url"},
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
    # Upload the image
    image_uri = upload_image_to_bucket(image_path)
    if not image_uri:
        return "Failed to upload the image."

    # Prepare the prompt
    default_prompt = "Describe this image in detail. What do you see?"
    prompt = custom_prompt if custom_prompt else default_prompt

    # Process the image
    caption = process_image(image_uri, prompt)
    return caption if caption else "Failed to generate a caption."

# Example usage
if __name__ == "__main__":
    image_path = "path/to/your/image.jpg"
    caption = caption_image(image_path)
    print(f"Image Caption: {caption}")