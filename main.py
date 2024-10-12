# to test script and pipelines

from pipelines.models_api import PROMPTS, mistral_call, natural_nutrients
from utils import encode_image
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logging.debug("Script started")

data = os.listdir("./data/")

for img in data:
    image_path = f"./data/{img}"

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
        natural_nuts = natural_nutrients(identified_json["name"])
    logging.info(identified_json["is_natural"])



