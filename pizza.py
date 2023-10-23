from cat.mad_hatter.decorators import hook, tool
from pydantic import BaseModel
from enum import Enum
from typing import Dict

from cat.log import log

import json


from cat.plugins.pizza_delivery.form import Form
KEY = "pizza_delivery"

"""
{
  "pizza_type": "Margherita",  # must be enum (3 different types)
  "cheese": True, #boolean
  "address": "street....", # free string
  "floor": 4, # int, address floor
}```

"""


EDIT_HISTORY = []

def format_edit_hystory(tunrs):
    formatted_history = ""
    for i, elem in enumerate(EDIT_HISTORY):
        if i > tunrs:
            return formatted_history
        
        formatted_history += elem
    
    return formatted_history

def extract_info(cat, model):

    edit_history = format_edit_hystory(3)

    user_message = cat.working_memory["user_message_json"]["text"]
    prompt = f"""Update the following JSON with information extracted from the Sentence:

    {edit_history}
    Sentence: {user_message}

    JSON: {model.model_dump_json()}

    Updated JSON:"""
    
    print(prompt)

    json_str = cat.llm(prompt)

    EDIT_HISTORY.append(
    f"""Sentence: {user_message}

    JSON: {model.model_dump_json()}

    Updated JSON: {json_str}
    
"""
    )

    return json.loads(json_str)

@tool(return_direct=True)
def order_pizza(details, cat):
    '''Use this tool to order one or more pizzas. User may provide some or all the information to fullfill the following json as Action Inputs:
    {
        "pizza_type": null # Can be any type of pizza ,
        "address": null # The address where delivery the pizza,
        "phone": null # The phone number of the customer,
    }'''

# try:
#     details = json.loads(details)
#     f = Form(**details)
# except Exception as e:
    # log.error("parsing error")
    # print(e)
    f = Form()

    # extract new info
    details = extract_info(cat, f)
    
    # update form
    new_details = f.model_dump() | details
    f = f.model_construct(**new_details)
    cat.working_memory[KEY] = f

    if f.is_complete():
        return f.completion_utterance()
    else:
        cat.working_memory[KEY] = f
        return f.ask_user_utterance(cat)


@hook
def agent_fast_reply(fast_reply: Dict, cat) -> Dict:

    if KEY not in cat.working_memory.keys():
        log.critical("NO KEY")
        return fast_reply
    
    log.critical(f"WORKING MEMORY: {KEY})")
    print(cat.working_memory[KEY])

    f = cat.working_memory[KEY]

    # extract new info
    details = extract_info(cat, f)
    
    # update form
    new_details = f.model_dump() | details
    f = f.model_construct(**new_details)
    cat.working_memory[KEY] = f
    
    if f.is_complete():
        #f.submit()
        utter = f.completion_utterance()
        del cat.working_memory[KEY]
    else:
        utter = f.ask_user_utterance(cat)
    return {
        "output": utter
    }

