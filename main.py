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
                                        system_prompt=PROMPTS.system_prompt_detection,
                                        base64_image=encoded_image,
                                        output_type="json")

        # Model to detect if it is a natural nutrient
        identification_user_prompt = PROMPTS.user_prompt_identification + "\n" + detection_response
        identified_response = mistral_call(text_input=identification_user_prompt,
                                        system_prompt=PROMPTS.system_prompt_identification,
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
            nutrients_json = f"""{nutrients_json}"""
        user_prompt_generation = product_name + "\n"+ PROMPTS.user_prompt_generation + "\n" + nutrients_json
        generated_response = mistral_call(text_input=user_prompt_generation,
                                           system_prompt=PROMPTS.system_prompt_generation)

        logging.info(generated_response)
    



