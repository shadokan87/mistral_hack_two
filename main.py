# to test script and pipelines

from pipelines.models_api import mistral_call
from pipelines.product_data import nutrients_api_call, extract_product_data, openfood_api
from pipelines.prompts import PROMPTS
from utils import encode_image
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logging.debug("Script started")

data = os.listdir("./data/")

for img in data:
    image_path = f"./data/{img}"
    print(img)
    if "milka" in img:
        
        # encoding image to make it work
        encoded_image = encode_image(image_path=image_path)

        # Model to detect type of product 
        detection_response = mistral_call(text_input=PROMPTS.user_prompt_detection,
                                          message_prompts=PROMPTS.detection_message_prompts,
                                        base64_image=encoded_image,
                                        output_type="json")
        print(detection_response)
        # Model to detect if it is a natural nutrient
        identification_user_prompt = PROMPTS.user_prompt_identification + "\n" + detection_response
        identified_response = mistral_call(text_input=identification_user_prompt,
                                           message_prompts=PROMPTS.identification_message_prompts,
                                           output_type="json")

        identified_json = json.loads(identified_response)

        logging.info(identified_json)

        if identified_json["is_natural"]:
            product_name = identified_json["name"]
            nutrients_json = nutrients_api_call(product_name, type="natural")
        else:
            product_name = identified_json["brand"]+" "+identified_json["brand_name_item_name"]
            nutrients_json = openfood_api(product_name=product_name)
            nutrients_json = extract_product_data(nutrients_json)

        logging.info(nutrients_json)

        if isinstance(nutrients_json, dict):
            nutrients_json = f"""Content of the product:
                                ----------------------
                                {nutrients_json}"""

        user_prompt_generation = product_name + "\n\n" + nutrients_json + "\n\n"
        
        # MUST ADD THIS DATA USING API FROM FRONTEND
        # part to add user_data from formlare
        # if user_data:
        #   user_data = get_request(json)
        # add to prompt
        # user_data =     
        
        generated_response = mistral_call(text_input=user_prompt_generation,
                                           message_prompts=PROMPTS.generation_report_message_prompts)

        logging.info(generated_response)
    



