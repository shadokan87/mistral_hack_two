# code functions to call mistrala and other apis
from mistralai import Mistral
from load_dotenv import load_dotenv
import os
import requests
from utils import bytes_to_json

load_dotenv()



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
        return e



