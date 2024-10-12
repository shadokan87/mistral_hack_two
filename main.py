# to test script and pipelines

from pipelines.models_api import PROMPTS, mistral_call
from utils import encode_image
import os


data = os.listdir("./data/")

for img in data:
    image_path = f"./data/{img}"

    encoded_image = encode_image(image_path=image_path)

    chat_response = mistral_call(text_input=PROMPTS.user_prompt_detection,
                                           base64_image=encoded_image,
                                           output_type="json")
    print(chat_response[0])
