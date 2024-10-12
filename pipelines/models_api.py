# code functions to call mistrala and other apis
from mistralai import Mistral
from load_dotenv import load_dotenv
import os

load_dotenv()

class PROMPTS:
    system_prompt_detection="""You are a helpful assistant that enables us to extract brand names using entity identification.
     Only return the brand name and the specific descriptor of the product type.
     
     <instructions>
     Must return the following: 
     - brand: brand name.
     - descriptor: description of the subname/type of the product. Add it only if you detect it in the image provided else fill it with None.
     Example:
     Name detected: Coca-cola zero
     {"brand": "coca-cola",
     "descriptor": "zero"}
     In proper JSON format.
     </instructions>
     
     OBLIGATORY:
     YOU MUST RESPECT THE OUTPUT FORMAT. If the output does not have the format provided the examples as a json it will be an error.
     """
    user_prompt_detection="Extract the name of the brand."



def mistral_call(text_input,
                 base64_image=None,
                 output_type=None):
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

    # Get the chat response
    args_call = {
        "model": model,
        "messages": messages}

    if output_type=="json":
        args_call["response_format"] = {"type": "json_object"}
    try:
        chat_response = client.chat.complete(**args_call)
        return chat_response.choices[0].message.content, messages

    except Exception as e:
        return (e,)
