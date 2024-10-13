from utils import bytes_to_json
import openfoodfacts
import os
import requests
import pandas as pd

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
            product_data[data_tag] = information[data_tag]
        else:
            product_data[data_tag] = None

    return product_data


def select_subset(products):
    data = pd.DataFrame.from_dict(products[0]["nutriments"], orient="index").T
    for i in range(1, len(products)):
        new_data = pd.DataFrame.from_dict(products[i]["nutriments"], orient="index").T
        data = pd.concat((data, new_data), axis=0).reset_index(drop=True)
    return data.filter(like="100g")

def filter_products(dataset):
    dataset.dropna(axis=1, inplace=True)
    # data check
    columns_to_check = ["carbohydrates_100g",
                        "sugars_100g","fat_100g",
                        "saturated-fat_100g"]
    for col in columns_to_check:
        if col in list(dataset.columns):
            continue
        else:
            columns_to_check.remove(col)

    dataset.sort_values(columns_to_check,
                        ascending=True, inplace=True)
    return dataset

def return_alternatives(product_type):
    product_info = openfood_api(product_type)
    output_data = select_subset(product_info["products"])
    filtered_data = filter_products(output_data)
    alternatives = list(filtered_data.index[0:3])

    return {"alternative_products": [product_info["products"][alt] for alt in alternatives]}
    
    