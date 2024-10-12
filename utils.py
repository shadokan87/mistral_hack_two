import base64
import json

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None
    
def bytes_to_json(response):
    "Transform bytes response to json"
    print(response)
    my_json = response.content.decode('utf8').replace("'", '"')
    print(my_json)
    data = json.loads(my_json)
    tf_data = json.dumps(data, indent=4, sort_keys=True)

    return tf_data

def load_json(file_path):
    with open(file_path, 'r') as json_file:
        json_object = json.load(json_file)
        return (json_object)