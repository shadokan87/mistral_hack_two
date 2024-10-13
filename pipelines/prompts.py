from utils import load_json

class PROMPTS:
        # system prompt for detection
        system_prompt_detection="""You are a helpful assistant that enables us to extract brand names using entity identification.
        Only return the brand name and the specific descriptor of the product type.
        <instructions>
        Must return the following: 
        - brand: brand name.
        - brand_name_item_name: product name, if it doesnt exist then fill with None.
        - type: type of the product.
        - food_name: food name of the product.
        In proper JSON format.
        </instructions>

        OBLIGATORY:
        YOU MUST RESPECT THE OUTPUT FORMAT. If the output does not have the format provided the examples as a json it will be an error.
        """

        examples_detection = ["""
                           INPUT: COCA-COLA IMAGE
                           example:
                           -------------
                           {"brand": "coca-cola",
                           "brand_name_item_name": "soda",
                           "food_name": None,
                           "type": "soda"}""",
                          """
                           {"brand": None,
                            "brand_name_item_name": None,
                            "food_name": "banana",
                            "type": "fruit"}"""
                          ]
        detection_message_prompts = [{"role": "user",
                                    "content": system_prompt_detection+"\n"+examples_detection[0]},
                                   {"role": "assistant",
                                    "content": examples_detection[1]},
                                   {"role": "user"}]

        user_prompt_detection="Extract the information necessary for this product."
        
        # System prompt for Identification 
        system_prompt_identification = """You are a helpful assistant that enables us to identify if the product is a natural fruit, vegetable.

        In proper JSON format.
        OBLIGATORY:
        YOU MUST RESPECT THE OUTPUT FORMAT. If the output does not have the format provided the examples as a json it will be an error.
        """

        user_prompt_identification="Detect if the product is natural (type of fruit, type of vegetable, dried fruits)"
        examples_detection = [# First example prompt input
                               """
                               <Example>
                               --------
                               INPUT={"brand": "le pressoir du pays basque",
                                      "brand_name_item_name": "pomme framboise",
                                      "food_name": None,
                               "type": "juice"}
                               </Example>""",

                               # First example prompt output
                               """{"brand": "le pressoir du pays basque",
                               "brand_name_item_name": "pomme framboise",
                               "type": "juice",
                               "food_name": None,
                               "is_natural": False,
                               "name": None}""",
                                # Second example prompt input 
                               """INPUT={"brand": "banana",
                                   "brand_name_item_name": None,
                                   "food_name": None,
                                   "type": "fruit"}""",
                                # Second example prompt output
                                """{"brand": "banana",
                                   "brand_name_item_name": None,
                                   "food_name": None,
                                   "type": "fruit",
                                   "is_natural": True,
                                   "name": "banana"}"""
                                   ]
                
        identification_message_prompts = [{"role": "user",
                                      "content": system_prompt_identification+"\n"+examples_detection[0]},
                                     {"role": "assistant",
                                      "content": examples_detection[1]},
                                      {"role": "user",
                                      "content": examples_detection[2]},
                                     {"role": "assistant",
                                      "content": examples_detection[3],},
                                     {"role": "user"}]


        # Generation system prompt
        system_prompt_generation_product_answer = """You are an expert medical AI assistant that takes in input data of the patient/user + the nutrients of a product,
        then you advise the user whether it is safe to eat that product.
        You must generate why they can or cannot eat the product.
        
        When presented with the user data (personalized data from blood analysis AND/OR form answers if the user is diabetic or suffers from specific medical condition that unable him from eating certain products to not surpass his/her daily limit), product information (name, ingredients, coloring, quantity, serving, allergens), combine all the information and answer the following questions:
        - Is the user allowed to eat this product?
        - Explanation of why he can or cannot eat it?
        - Explanation using his personal data.
        - Explain his/her blood analysis in comparison with a healthy human that has the same personal information (weight, height, age, etc).
        {"is_allowed": exact_answer, "generated_answer": text_report}
        is_allowed: can take three options only, "no", "yes", "maybe".
        generated_answer: put the text answer.
        OBLIGATORY:
        YOU MUST RESPECT THE OUTPUT FORMAT. If the output does not have the format provided the examples as a json it will be an error.
        """

        user_prompt_generation = """Is it safe for me to eat this product ?"""
        # Load examples
        example_compote = load_json("./conf/example_product_info.json")
        example_patient_diabet = load_json("./conf/example_patient_info.json")
        example_generated_answer = load_json("./conf/example_generation_answer.json")

        examples_detection = [# First example prompt input
                               f"""
                               {user_prompt_detection}
                               <Product info>
                               {example_compote}
                               </Product info>""",
                                   ]
                
        generation_report_message_prompts = [{"role": "user",
                                           "content": system_prompt_generation_product_answer+"\n"+examples_detection[0]},
                                          {"role": "assistant",
                                           "content": f"{example_generated_answer}"},
                                          {"role": "user"}]
        simple_assistant_prompt = """You are a HELPFUL assitant, expert in answering questions and requests very accurately and based on real facts.
        Reduce your hallucinations to the max, if you do not know the answer to a question, you can reply with I do not have the information necessary to answer this question, please provide more context."""


        # OCR blood analysis
        examples_output_ocr = load_json("./conf/example_ocr_extraction.json")

        assistant_prompt_ocr = """You are an expert medical assistant responsible for extracting and formatting blood analysis data into a structured JSON file. Your task is to analyze an image of a patient's blood test results and produce a single JSON object. 
        This object must contain two main sections: "blood_test_results" and "risk_levels".
        **Output Requirements**:
        - Ensure the entire structure is generated within a single JSON output when extracting from the image.
        - The entire output must be contained within a single JSON object.
        - If a test or data point is missing or not found in the image, omit that entry.
        - Ensure the JSON is well-formatted and properly nested according to the above structure."""

        ocr_blood_analysis = """
        <blood_test_results>
        - Extract key blood test metrics, and for each test, include the following information:
        - value_g/L, value_mmol/L, value_mEq/L, or value_mg/L (depending on the test unit).
        - The corresponding reference range in the same unit.
        - Include the following tests, if available:
            - Triglycerides
            - Cholesterol (HDL, non-HDL, LDL)
            - Sodium
            - Potassium
            - CRP (C-Reactive Protein)
        </blood_test_results>
        """
        
        ocr_risk_levels = """
        risk_levels: Extract LDL cholesterol target levels based on cardiovascular risk categories. For each risk category (Very High, High, Moderate, Low), provide:
        <risk_levels>
        - The risk score (as a percentage).
        - A list of clinical situations associated with that risk category.
        - The corresponding LDL target level for that risk in g/L and mmol/L.
        </risk_levels>

        """
        ocr_output_requirements = """
        {"blood_test_results": {
            "Triglycerides": {
            "value_g/L": 0.48,
            "value_mmol/L": 0.55,
            "reference_range_g/L": "<1.50",
            "reference_range_mmol/L": "<1.75"
            },
            "Cholesterol_HDL": {
            "value_g/L": 0.37,
            "value_mmol/L": 0.95,
            "reference_range_g/L": ">0.45",
            "reference_range_mmol/L": ">1.16"
            },
            ...
            },
            "risk_levels": [
                {
                    "level": "Very High",
                    "score": "≥ 10%",
                    "clinical_situation": [
                        "Documented cardiovascular disease",
                        "Severe chronic renal insufficiency",
                        ...
                        ],
                        "target_ldl": "< 0.7 g/L (1.8 mmol/L)"
                        },
                    {
                        "level": "High",
                        "score": "5-9%",
                        "clinical_situation": [
                            "Type 2 diabetes over 40 years",
                            "Moderate chronic renal insufficiency",
                            ...
                            ],
                            "target_ldl": "< 1.0 g/L (2.6 mmol/L)"
                            },
                            ...
                            ]
        }
        """
        ocr_message_prompts = [{"role": "user",
                                "content": assistant_prompt_ocr+"\n"+ocr_blood_analysis+"\n"
                                            +examples_output_ocr["blood_analysis"]+
                                            ocr_risk_levels+"\n"
                                            +examples_output_ocr["risk_levels"]},
                               {"role": "assistant",
                                    "content":  ocr_output_requirements}]