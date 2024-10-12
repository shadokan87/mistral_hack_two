# code functions to call mistrala and other apis
from mistralai import Mistral
from load_dotenv import load_dotenv
import os
import requests
from utils import bytes_to_json

load_dotenv()

class PROMPTS:
    system_prompt_detection="""You are a helpful assistant that enables us to extract brand names using entity identification.
     Only return the brand name and the specific descriptor of the product type.
     
     <instructions>
     Must return the following: 
     - brand: brand name.
     - product_name: product name, if it doesnt exist then fill with None.
     - type: type of the product.
     - is_natural: True if product natural or False.

     <examples>
     ---------
     Name detected: Coca-cola zero
     example_1: {
         "brand": "coca-cola",
         "product_name": "soda",
         "type": "soda"}
     
     example_2: {
         "brand": None,
         "product_name": "banana",
         "type": "fruit"}
     </examples>

     In proper JSON format.
     </instructions>
     
     OBLIGATORY:
     YOU MUST RESPECT THE OUTPUT FORMAT. If the output does not have the format provided the examples as a json it will be an error.
     """
    user_prompt_detection="Extract the name of the brand."
    
    system_prompt_identification = """You are a helpful assistant that enables us to identify if the product is a natural fruit, vegetable.
    <example>:
    input={"brand": "le pressoir du pays basque",
            "product_name": "pomme framboise",
            "type": "juice"}
    output={"brand": "le pressoir du pays basque",
            "product_name": "pomme framboise",
            "type": "juice",
            "is_natural": False,
            "name": None}

    input={"brand": "banana",
            "product_name": None,
            "type": "fruit"}

    output={"brand": "banana",
            "product_name": None,
            "type": "fruit",
            "is_natural": True,
            "name": "banana"}
    
    In proper JSON format.
    OBLIGATORY:
    YOU MUST RESPECT THE OUTPUT FORMAT. If the output does not have the format provided the examples as a json it will be an error.
    """
    user_prompt_identification="Detect if the product is natural (type of fruit, type of vegetable, dried fruits)"



def mistral_call(text_input,
                 system_prompt,
                 base64_image=None,
                 output_type=None):
    
    model = "mistral-large-latest"

    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    # Define the messages for the chat
    messages = [{"role": "system",
                 "content": system_prompt},

                {"role": "user",
                 "content":[
                     {"type": "text",
                      "text": text_input}
                     ]
                     }
                ]
    # add image if given
    if base64_image is not None:
        image_url = f"data:image/jpeg;base64,{base64_image}"
        image_message = {"type": "image_url",
                         "image_url": image_url}

        messages[1]["content"].append(image_message)
        model = "pixtral-12b-2409"

    # Get the chat response
    args_call = {
        "model": model,
        "messages": messages}

    if output_type=="json":
        args_call["response_format"] = {"type": "json_object"}
    try:
        chat_response = client.chat.complete(**args_call)
        return chat_response.choices[0].message.content

    except Exception as e:
        return (e,)



def nutrients_api_call(query: str, type="industrial"):
    api_key = os.environ["NUTRITION_API_KEY"]
    app_id = os.environ["NUTRITION_APP_ID"]
    if type == "natural":
        url = os.environ["NUTRITION_APP_URL"]
    else:
        url = os.environ["SEARCH_INSTANT_APP_URL"]

    headers = {
        'Content-Type': 'application/json',
        'x-app-id': app_id,
        'x-app-key': api_key
    }
    data = {'query': query}
    
    api_response = requests.post(url, json=data, headers=headers)
    response = bytes_to_json(api_response)

    return response