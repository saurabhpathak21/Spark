import vertexai
from vertexai.generative_models import GenerativeModel, Part

project_id = "gcp project id"
location = "europe-west2"
bucket_prefix = "Enter you bucket details"


vertexai.init(project=project_id, location=location)
model = GenerativeModel("gemini-1.5-flash-001")


def process_uploaded_images(image_names, prompt_text_template):
    image_uris = [bucket_prefix + name for name in image_names]
    image_parts = [Part.from_uri(uri, "image/jpeg") for uri in image_uris]
    image_count = len(image_names)
    prompt_text = prompt_text_template.format(image_count=image_count)
    response = model.generate_content(image_parts + [prompt_text])
    return response.text

def simulate_image_uploads():
    image_names = []

    while True:
        name = input("Enter the image file name (or type 'done' to finish): ")
        
        if name.lower() == 'done':
            break
        
        image_names.append(name)
    
    return image_names

image_names = simulate_image_uploads()

# Elaborate the archiecture 

prompt_text_template_general = "Explain these {image_count} general architecture designs individually in response?"

# comparison prompt template
prompt_text_template_compare = "Compare these {image_count} architecture designs for performance, network connectivity, security, and scalability. Assess all in detail and suggest which one is better and why?"

#set context
prompt_text_template_context = '''Evaulate these {image_count} architecture on three basic creteria
1. The traffic should be encrypted at rest and in transit
2. The traffic can be contorlled using the network
3. No unauthorised access
'''
prompt_text_template = prompt_text_template_general + prompt_text_template_compare + prompt_text_template_context
                                    
# Process the uploaded images and get the response
if image_names:
    response_text = process_uploaded_images(image_names, prompt_text_template)
    with open("conclusion.txt", "w") as file:
        file.write(response_text)
    print("Response can be accessed, http://127.0.0.1:9090")
else:
    print("No images were uploaded.")
