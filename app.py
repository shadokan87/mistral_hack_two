from fastapi import FastAPI, File, UploadFile
# to test script and pipelines

from pipelines.models_api import (mistral_call, simple_chat_call)
from pipelines.product_data import (nutrients_api_call, extract_product_data,
                                    openfood_api, return_alternatives)
from pipelines.prompts import PROMPTS
from utils import encode_image
import os
import json
import logging

app = FastAPI()

async def product_detection(image_path: str):

    encoded_image = encode_image(image_path=image_path)
    logging.info("#############################")
    logging.info("initial detection of the product")

    # Model to detect type of product 
    detection_response = mistral_call(text_input=PROMPTS.user_prompt_detection,
                                      message_prompts=PROMPTS.detection_message_prompts,
                                      base64_image=encoded_image,
                                      output_type="json")
    detection_json = json.loads(detection_response)

    return detection_json

async def product_identification(detection_json: dict):
    logging.info("#############################")
    logging.info("enrichement of product info")
    identification_user_prompt = PROMPTS.user_prompt_identification + "\n" + f"{detection_json}"
    identified_response = mistral_call(text_input=identification_user_prompt,
                                        message_prompts=PROMPTS.identification_message_prompts,
                                        output_type="json")
    if isinstance(identified_response, str):
        identified_json = json.loads(identified_response)
    else:
        identified_json = identified_response
    return identified_json

async def extract_product_info(identified_json: dict):
    logging.info("#############################")
    logging.info("calling food api")
    if identified_json["is_natural"]:
        # natural food like banana
        product_name = identified_json["name"]
        nutrients_str = nutrients_api_call(product_name, type="natural")
        nutrients_json = {"nutrients_json": nutrients_str, "product_name": product_name}
    else:
        # artificial product like nutella
        product_name = identified_json["brand"]+" "+identified_json["brand_name_item_name"]
        nutrients_json = openfood_api(product_name=product_name)
        nutrients_json = extract_product_data(nutrients_json)
        nutrients_json["product_name"] = product_name

    return nutrients_json

async def get_report(nutrients_json):
    if isinstance(nutrients_json, dict):
        nutrients_prompt = f"""Content of the product:
                                ----------------------
                                {nutrients_json}"""
    print("OKK", nutrients_json)
    user_prompt_generation = nutrients_json["product_name"] + "\n\n" + nutrients_prompt + "\n\n"
    logging.info("#############################")
    logging.info("generating report analysis")
    generated_response = mistral_call(text_input=user_prompt_generation,
                                        message_prompts=PROMPTS.generation_report_message_prompts,
                                        output_type="json")

    return generated_response

@app.post("/verify_food/")
async def verify_food(image: UploadFile = File(...)):
    file_location = f"uploads/{image.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(image.file.read())
    
    detection_json = await product_detection(file_location)
    identified_json = await product_identification(detection_json)
    nutrients_json = await extract_product_info(identified_json)
    generated_response = await get_report(nutrients_json)
    if isinstance(identified_json, str):
        generated_response["identified_json"] = identified_json
    else:
        generated_response["identified_json"] = f"{identified_json}"

    return generated_response

@app.post("/alternatives/")
async def get_alternatives(generated_response: str):
    identified_json = generated_response["identified_json"]
    alternative = await return_alternatives(product_type=identified_json["type"])
    alternative["generated_response"] = generated_response
    return alternative

@app.post("/simple_chat/")
async def simple_chat(generated_response,
                      text_input: str,
                      alternative=None):
    if alternative is None:
        history_chat = generated_response["generated_response"]
    else:
        history_chat = generated_response["generated_response"]+f"{alternative}"
    messages = [{"role": "system",
                 "content": PROMPTS.simple_assistant_prompt},
                {"role": "assistant","content": history_chat},
                {"role": "user"}]
    messages[-1]["content"] = text_input
    output = {}
    output_text = await simple_chat_call(messages)
    output["generated_response"] = output_text

    return output

@app.post("/ocr/")
async def extract_analysis_data(image: UploadFile = File(...),
                                text_input=None):
    file_location = f"analysis/{image.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(image.file.read())
    if text_input is None:
        text_input = """Extract all biological and available info from this image relating to diabetes."""
    # structure your input
    extracted_analysis = mistral_call(text_input=text_input,
                                        message_prompts=PROMPTS.ocr_message_prompts,
                                        output_type="json")
    if isinstance(extracted_analysis, str):
        # Turn str to dict/json object
        extracted_analysis_json = json.loads(extracted_analysis)

    return extracted_analysis_json
