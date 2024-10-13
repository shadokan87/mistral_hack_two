from fastapi import FastAPI, File, UploadFile
# to test script and pipelines

from pipelines.models_api import mistral_call
from pipelines.product_data import (nutrients_api_call, extract_product_data,
                                    openfood_api, return_alternatives)
from pipelines.prompts import PROMPTS
from utils import encode_image
import os
import json
import logging
# app.py
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse


app = FastAPI()


@app.post("/files/")
async def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}


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
    print("HERE", type(identified_response))
    identified_json = json.loads(identified_response)
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

class ImageURL(BaseModel):
    url: str

async def process_image_url(image: ImageURL):
    # Here you can process the image from the URL
    # For demonstration, we'll just return the URL
    print(image.url)
    return {"url": image.url}


class ImagePayload(BaseModel):
    url: str = Field(..., alias='image_path')  # Accept 'image_path' as an alias for 'url'

class Config:
    allow_population_by_field_name = True  # Allow accessing via 'url'

# @app.post("/upload_image/")
# async def upload_image(image: UploadFile = File(...)):
#     # Save the uploaded image
#     file_location = f"uploads/{image.filename}"
#     with open(file_location, "wb+") as file_object:
#         file_object.write(image.file.read())
#     return {"info": f"file '{image.filename}' saved at '{file_location}'"}

@app.post("/verify_food/")
async def verify_food(image: UploadFile = File(...)):
    file_location = f"uploads/{image.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(image.file.read())
    
    detection_json = await product_detection(file_location)
    identified_json = await product_identification(detection_json)
    nutrients_json = await extract_product_info(identified_json)
    generated_response = await get_report(nutrients_json)
    return generated_response