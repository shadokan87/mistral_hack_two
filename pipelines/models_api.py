# code functions to call mistrala and other apis
from mistralai import Mistral
from load_dotenv import load_dotenv
import os

load_dotenv()

class PROMPTS:
    system_prompt_detection="""You are a helpful assistant that enables us to extract brand names using entity identification.
     Only return the brand name and with the type.
     output format must be respected in all calls:
     brand:descriptor
     descriptor is the definition description of the product which specific version of the product.
     """
    user_prompt_detection="Extract the name of the brand."



def mistral_call(text_input,
                 base64_image=None,
                 mode="detection"):
    model = "pixtral-12b-2409"
    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    # Define the messages for the chat
    messages = [{"role": "system",
                 "content": PROMPTS.system_prompt_detection},

                {"role": "user",
                 "content":[
                     {"type": "text",
                      "text": text_input}]
                     }
                ]
    # add image if given
    if base64_image is not None:
        image_url = f"data:image/jpeg;base64,{base64_image}"
        image_message = {"type": "image_url",
                         "image_url": image_url}

        messages[1]["content"].append(image_message)

    print(messages)

    # Get the chat response
    try:
        chat_response = client.chat.complete(
            model=model,
            messages=messages,
        )
        return chat_response.choices[0].message.content, messages

    except Exception as e:
        return e
