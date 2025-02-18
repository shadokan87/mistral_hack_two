# code functions to call mistrala and other apis
from mistralai import Mistral
from load_dotenv import load_dotenv
import os

load_dotenv()

#[{"role": "user", "content": systerm_prompt+example1},
 #{"role": "assitant", "content": answer},
 #{"role": final_prompt}]

def mistral_call(text_input,
                       message_prompts,
                       base64_image=None,
                       output_type=None):
    
    model = "mistral-large-latest"

    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    # Define the messages for the chat
    text_data = [{"type": "text",
                  "text": text_input}
                 ]
    message_prompts[-1]["content"] = text_data
    messages = message_prompts

    # add image if given
    if base64_image is not None:
        image_url = f"data:image/jpeg;base64,{base64_image}"
        image_message = {"type": "image_url",
                         "image_url": image_url}

        messages[-1]["content"].append(image_message)
        model = "pixtral-12b-2409"

    # Get the chat response
    args_call = {
        "model": model,
        "messages": messages}
    print("#############")
    print(messages)
    if output_type=="json":
        args_call["response_format"] = {"type": "json_object"}
    try:
        chat_response = client.chat.complete(**args_call)
        return chat_response.choices[0].message.content

    except Exception as e:
        return e



def simple_chat_call(text_input,
                           output_type=None):
    
    model = "mistral-large-latest"

    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    # Define the messages for the chat
    #text_data = [{"type": "text",
    #              "text": text_input}
    #             ]
    simple_assistant = """You are a HELPFUL assitant, expert in answering questions and requests very accurately and based on real facts.
    Reduce your hallucinations to the max, if you do not know the answer to a question, you can reply with I do not have the information necessary to answer this question, please provide more context."""
    messages = [{"role": "system", "content": simple_assistant}, {"role": "user"}]
    messages[-1]["content"] = text_input

    # Get the chat response
    args_call = {
        "model": model,
        "messages": messages}

    if output_type=="json":
        args_call["response_format"] = {"type": "json_object"}

    try:
        chat_response = client.chat.complete(**args_call)
        return chat_response.choices[0].message.content

    except Exception as e:
        return e