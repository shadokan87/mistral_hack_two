from utils import bytes_to_json
import openfoodfacts
import os
import requests

def openfood_api(product_name: str,
                 user_agent="MyAwesomeApp/1.0"):
    """API call for openfood database"""
    # User-Agent is mandatory
    api = openfoodfacts.API(user_agent=user_agent)
    api_json = api.product.text_search(product_name)

    return api_json

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

def extract_product_data(product_info):
    """Extract the exact data from product_info"""
    necessary_info = ["url", "product_name", "additives_tags",
    "allergens_from_ingredients", "categories",
    "conservation_conditions", "image_front_url",
    "ingredients_hierarchy", "ingredients_non_nutritive_sweeteners_n",
    "ingredients_text", "nutriments", "nutrient_levels", "nutriscore",
    "nutrition_grade_fr", "nutrition_grade_fr", "origins", "product_name_fr",
    "serving_quantity"]
    product_data = {}
    information = product_info["products"][0]
    for data_tag in necessary_info:
        if data_tag in list(information.keys()):
            if data_tag!="serving_quantity":
                product_data[data_tag] = information[data_tag]
            else:
                product_data[data_tag] = information[data_tag]+information["serving_quantity_unit"]
        else:
            product_data[data_tag] = None

    return product_data