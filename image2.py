import vertexai
from vertexai.generative_models import GenerativeModel, Part
import logging

logging.basicConfig(level=logging.INFO)

project_id = "enter your projet id"
location = "europe-west2"
bucket_prefix = "gs://bucket_name/"

vertexai.init(project=project_id, location=location)
model = GenerativeModel("gemini-1.5-flash-001")

def simulate_image_uploads():
    """
    Simulates the process of uploading images by allowing users to input image names.
    Returns a list of image names entered by the user.
    """
    image_names = []

    while True:
        name = input("Enter the image file name (or type 'done' to finish): ")
        
        if name.lower() == 'done':
            break
        image_names.append(name)
    
    return image_names

def generate_prompt(image_count):
    """
    Generates a prompt based on the number of images.
    """
    prompt_text_template_general = "Explain these {image_count} general architecture designs individually in response."
    prompt_text_template_compare = " Compare these {image_count} architecture designs for performance, data (compute, latency, performance), network, security, and scalability and put in a table. Assess all in detail and choose which one is better and why."
    prompt_text_template_context = '''
    Evaluate these {image_count} architecture on three basic criteria:
    1. The traffic should be encrypted at rest and in transit.
    2. Data integrity is consistent.
    3. Architecture can scale and perform as the data volume, velocity, and variety grow.
    4. Architecture complies with the relevant regulations, policies, and standards for data governance and security.
    5. Data is stored and accessed only from approved services such as BigQuery and Google Cloud Storage.
    '''
    prompt_text_template_code = 'Share the Architecture recommendation for Security and Performance for the implementation on the suggested architecture design from {prompt_text_template_context}'
    return prompt_text_template_general + prompt_text_template_compare + prompt_text_template_context + prompt_text_template_code

def validate_image_names(image_names):
    """
    Validates that all image names end with a valid image file extension.
    """
    return all(name.endswith(('.jpg', '.jpeg', '.png')) for name in image_names)

def process_images(image_names, prompt_text_template):
    """
    Processes the images by sending them to the Vertex AI generative model.
    """
    try:
        image_uris = [bucket_prefix + name for name in image_names]
        image_parts = [Part.from_uri(uri, "image/jpeg") for uri in image_uris]
        response = model.generate_content(image_parts + [prompt_text_template])
        return response.text
    except Exception as e:
        logging.error(f"Error processing images: {e}")
        return None

def main():
    image_names = simulate_image_uploads()

    if image_names:
        if validate_image_names(image_names):
            prompt_text_template = generate_prompt(len(image_names))
            response_text = process_images(image_names, prompt_text_template)
            if response_text:
                with open("conclusion.txt", "w") as file:
                    file.write(response_text)
                logging.info("Response can be accessed, http://127.0.0.1:9090.")
            else:
                logging.warning("No response generated.")
        else:
            logging.error("Invalid image names provided.")
    else:
        logging.warning("No images were uploaded.")

if __name__ == "__main__":
    main()
