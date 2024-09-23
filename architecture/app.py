import os
import json
import bcrypt
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from google.cloud import storage
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from vertexai.generative_models import GenerativeModel, Part
import vertexai
import logging
from flask_cors import CORS
from urllib.parse import urlparse
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')


CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'session1')  # Set a secret key for sessions

# Google Cloud Storage setup
bucket_name = os.getenv("GOOGLE_CLOUD_BUCKET_NAME")
project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")

storage_client = storage.Client(project=project_id)
bucket = storage_client.bucket(bucket_name)

# Path to users.json file to store user data
USERS_FILE = 'users.json'

# Helper functions to read and write user data
def read_users_file():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def write_users_file(data):
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# User authentication
def authenticate_user(email, password):
    users = read_users_file()
    user = next((u for u in users if u['email'] == email), None)
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user
    return None

# Dictionary to store user uploaded images
user_uploaded_images = {}
print(f"Current uploaded images: {user_uploaded_images}")

def get_images_for_user(user_name):
    return user_uploaded_images.get(user_name, [])

@app.post('/upload')
def upload_file():
    user_name = request.form.get('userName')
    files = request.files.getlist('file1[]') + request.files.getlist('file2[]')

    if not user_name:
        return jsonify(success=False, message='Missing userName'), 400

    # If no new files are uploaded but files exist in the session, use those
    if not files and 'uploaded_files' in session:
        uploaded_file_urls = session['uploaded_files']
        return jsonify(success=True, message='Files already uploaded', fileURLs=uploaded_file_urls), 200

    # If no files are uploaded and nothing is in the session, return an error
    if not files:
        return jsonify(success=False, message='No files uploaded'), 400

    uploaded_file_urls = []

    for file in files:
        if file:
            # Upload file to the user's folder
            user_blob_path = f'{user_name}/{file.filename}'
            blob = bucket.blob(user_blob_path)
            blob.upload_from_file(file.stream, content_type=file.content_type)

            # Generate the public URL for the uploaded file
            public_url = f'https://storage.googleapis.com/{bucket_name}/{blob.name}'
            uploaded_file_urls.append(public_url)

            # Move the file from the user's folder to the root directory of the bucket
            root_blob_path = f'{file.filename}'
            bucket.copy_blob(blob, bucket, root_blob_path)

            # Delete the file from the user's folder after copying it to the root
            blob.delete()

            # Add the uploaded image to the user's list
            if user_name not in user_uploaded_images:
                user_uploaded_images[user_name] = []
            user_uploaded_images[user_name].append(file.filename)

    # Store the uploaded file URLs in the session
    session['uploaded_files'] = uploaded_file_urls

    return jsonify(success=True, message='Files uploaded successfully', fileURLs=uploaded_file_urls), 200

@app.route('/get-uploaded-images', methods=['GET'])
def get_uploaded_images():
    user_name = request.args.get('userName')
    print(f"Received request for user: {user_name}")  # Debugging print

    if not user_name:
        return jsonify({'success': False, 'message': 'Username is required'}), 400

    uploaded_images = get_images_for_user(user_name)
    if not uploaded_images:
        return jsonify({'success': False, 'message': 'No images found for user'}), 404
    
    return jsonify({'success': True, 'imageNames': uploaded_images}), 200


# Sign-Up Route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify(success=False, message='Username, email, and password are required'), 400

    users = read_users_file()
    if any(u['username'] == username or u['email'] == email for u in users):
        return jsonify(success=False, message='Username or Email already exists'), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = {'username': username, 'email': email, 'password': hashed_password}
    users.append(new_user)
    write_users_file(users)

    return jsonify(success=True, message='User registered successfully!'), 201

# Sign-In Route
@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = authenticate_user(email, password)
    if not user:
        return jsonify(success=False, message='Invalid email or password'), 400

    return jsonify(success=True, message='Sign-in successful', username=user['username']), 200

# Logout and delete user files from GCS
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear the session when the user logs out\
    # Reset the uploaded images for the user
    user_uploaded_images.clear()  # Clear the dictionary holding uploaded images

    try:
        # Delete all files and folders in the GCS bucket
        blobs = bucket.list_blobs()
        deleted_files = []

        for blob in blobs:
            blob.delete()  # Delete each blob
            deleted_files.append(blob.name)  # Keep track of deleted files

        print(f"Deleted all files in the bucket: {deleted_files}")  # Log deleted files

        return jsonify(success=True, message='Logged out and all files in the bucket deleted successfully.'), 200

    except Exception as e:
        print(f'Error deleting files in bucket: {e}')
        return jsonify(success=False, message='Failed to delete files in the bucket.'), 500
    


# Design
from flask import Flask, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize Vertex AI settings
project_id = "et-proposition-sapient-186848"
location = "europe-west2"  # Ensure this matches your model's location

# Initialize Vertex AI
vertexai.init(project=project_id, location=location)
model = GenerativeModel("gemini-1.5-flash-001")
@app.route('/api/generate-architecture', methods=['POST'])
def generate_architecture():
    data = request.json
    provider = data.get('provider')
    category = data.get('category')
    details = data.get('details')

    try:
        # Create a prompt based on user input
        prompt = f"Generate a cloud architecture diagram for {provider} in the {category} category. Details: {details}"

        # Call the AI model API
        response = model.generate_content(prompt)

        # Extract the content from the response
        architecture_data = response.text  
        print("Raw Architecture Data:", architecture_data)  # Log the raw data

        # Return the architecture data in JSON format
        return jsonify({'architecture': architecture_data}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500
    

#############################
# exxpain archiecture code   #
#############################

# Configuration
project_id = "et-proposition-sapient-186848"
location = "europe-west2"  # Ensure this matches your model's location
bucket_prefix = "gs://demobucket878/"

# Initialize Vertex AI
vertexai.init(project=project_id, location=location)
model = GenerativeModel("gemini-1.5-flash-001")

logging.basicConfig(level=logging.INFO)

# Function to generate prompt text based on feature
def generate_prompt(image_count, feature):
    prompts = {
        'explainArchitecture': f"Explain these {image_count} general architecture designs individually in response.",
        'compareArchitecture': f"Compare these {image_count} architecture designs for performance, data (compute, latency, performance), network, security, and scalability and put in a table. Assess all in detail and choose which one is better and why.",
        'suggestImprovements': f"Share the architecture recommendations for security and performance for the implementation on the suggested architecture design.",
        'evaluateSecurity': f'''Evaluate these {image_count} architecture designs based on:
        1. Traffic encryption at rest and in transit.
        2. Consistency of data integrity.
        3. Scalability and performance as data volume, velocity, and variety grow.
        4. Compliance with relevant regulations, policies, and standards for data governance and security.
        5. Data access only from approved services such as BigQuery and Google Cloud Storage.'''
    }
    return prompts.get(feature, "No valid feature selected.")

# Function to process uploaded images
def process_uploaded_images(image_names, feature):
    image_parts = []

    for image_name in image_names:
        try:
            # Parse the URL to extract the path
            if image_name.startswith("https://storage.googleapis.com/"):
                # Extract the relevant path from the URL
                parsed_url = urlparse(image_name)
                image_name = parsed_url.path.lstrip("/")  # Remove leading slash

            # Construct the GCS URI using the correct path
            uri = f"gs://{image_name}" if image_name.startswith("demobucket878") else f"{bucket_prefix}{image_name}"
            logging.info(f"Processing Image URI: {uri}")

            # Detect MIME type based on file extension, default to "image/jpeg"
            mime_type = "image/jpeg" if uri.lower().endswith((".jpg", ".jpeg")) else "image/png"

            # Create a Part from the URI
            part = Part.from_uri(uri, mime_type)
            image_parts.append(part)
            logging.info(f"Created Part from URI: {uri}")

        except Exception as e:
            logging.error(f"Error creating Part from URI {uri}: {e}")
            return "Error with image URI"

    # Generate prompt text
    prompt_text = generate_prompt(len(image_parts), feature)
    logging.info(f"Generated Prompt Text: {prompt_text}")

    try:
        # Create a Part from the generated prompt text
        prompt_part = Part.from_text(prompt_text)
        logging.info("Created prompt Part")
    except Exception as e:
        logging.error(f"Error creating text Part: {e}")
        return "Error creating prompt text part"

    # Combine image parts and prompt part
    final_parts = image_parts + [prompt_part]
    logging.info(f"Final Parts List: {final_parts}")

    try:
        # Query the model
        response = model.generate_content(final_parts)
        logging.info(f"Model Response: {response}")
        return response.text if response else "No response received"
    except Exception as e:
        logging.error(f"Error during model prediction: {e}")
        return "Error generating content"
    image_parts = []

    for image_name in image_names:
        try:
            # Check if the image name is a full URL and extract the relevant path
            if image_name.startswith("https://storage.googleapis.com/"):
                # Extract the path from the URL
                image_name = image_name.split("storage.googleapis.com/")[-1]

            # Construct the GCS URI
            uri = f"gs://{image_name}" if not image_name.startswith("gs://") else image_name
            logging.info(f"Processing Image URI: {uri}")

            # Detect MIME type based on file extension, default to "image/jpeg"
            mime_type = "image/jpeg" if uri.lower().endswith(".jpg") or uri.lower().endswith(".jpeg") else "image/png"

            # Create a Part from the URI
            part = Part.from_uri(uri, mime_type)
            image_parts.append(part)
            logging.info(f"Created Part from URI: {uri}")

        except Exception as e:
            logging.error(f"Error creating Part from URI {uri}: {e}")
            return "Error with image URI"

    # Generate prompt text
    prompt_text = generate_prompt(len(image_parts), feature)
    logging.info(f"Generated Prompt Text: {prompt_text}")

    try:
        # Create a Part from the generated prompt text
        prompt_part = Part.from_text(prompt_text)
        logging.info("Created prompt Part")
    except Exception as e:
        logging.error(f"Error creating text Part: {e}")
        return "Error creating prompt text part"

    # Combine image parts and prompt part
    final_parts = image_parts + [prompt_part]
    logging.info(f"Final Parts List: {final_parts}")

    try:
        # Query the model
        response = model.generate_content(final_parts)
        logging.info(f"Model Response: {response}")
        return response.text if response else "No response received"
    except Exception as e:
        logging.error(f"Error during model prediction: {e}")
        return "Error generating content"


@app.route('/process-images', methods=['POST'])
def process_images():
    data = request.json
    logging.info(f'Received data: {data}')  # Log the entire data
    image_names = data.get('imageNames')
    feature = data.get('feature')

    logging.info(f'Received image names: {image_names}')
    logging.info(f'Received feature: {feature}')

    # Validate input data
    if not image_names or not isinstance(image_names, list):
        return jsonify({'success': False, 'message': 'Invalid image names'}), 400
    if not feature:
        return jsonify({'success': False, 'message': 'Feature not specified'}), 400

    # Process images using the defined function
    response_text = process_uploaded_images(image_names, feature)

    return jsonify({'success': True, 'response': response_text})


#############################
# Front end routes           #
#############################

# Serve the frontend
@app.route('/analyze')
def index():
    return render_template('index.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/draw')
def draw():
    return render_template('draw.html')



# Start the Flask application
if __name__ == '__main__':
    app.run(port=int(os.getenv("PORT", 3000)), debug=True)