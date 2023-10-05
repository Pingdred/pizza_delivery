from cat.mad_hatter.decorators import hook, tool
from pydantic import BaseModel
from enum import Enum
from typing import Dict

from cat.log import log

import json

KEY = "pizza_delivery"

class Question(Enum):
    CORNER = "Do you prefer hight corner or low corner?"
    PIZZA_TYPE = "Wich pizza do you prefer?"
    ADDRESS = "What is your address?"
    PHONE = "What is your phone number?"
    COMPLETE = "Pizza ordinata"

class Corner(Enum):
    Hight = "Hight"
    Low = "Low"

class Form(BaseModel):
    corner: Corner = None
    pizza_type: str = None
    address: str = None
    phone: str = None

    def check(self):
        if self.corner is None:
         return Question.CORNER
    
        if self.pizza_type is None:
            return Question.PIZZA_TYPE
        
        if self.address is None:
            return Question.ADDRESS
        
        if self.phone is None:
            return Question.PHONE
        
        return Question.COMPLETE



@tool(return_direct=True)
def order_pizza(details, cat):
    '''Use this tool to order a pizza. Use the information th eyser give you to fullfill the following json as Action Inputs:
    {
        "corner": null # Can be "Hight" or "Low",
        "pizza_type": null # Can be any type of pizza ,
        "address": null # The address where delivery the pizza,
        "phone": null # The phone number of the customer,
    }'''

    try:
        details = json.loads(details)
        f = Form(**details)
    except:
        f = Form()

    check_result = f.check()

    if check_result != Question.COMPLETE:
        cat.working_memory[KEY] = f

    return check_result.value


@hook
def agent_fast_reply(fast_reply: Dict, cat) -> Dict:

    if KEY not in cat.working_memory.keys():
        log.critical("NO KEY")
        return fast_reply
    
    log.critical(f"WORKING MEMORY: {KEY})")
    print(cat.working_memory[KEY])

    details = cat.working_memory[KEY]

    check_result = details.check()

    user_mesage = cat.working_memory["user_message_json"]["text"]

    if check_result == Question.CORNER:
        details.corner = user_mesage
        log.critical(details.corner)
        return {
            "output": Question.PIZZA_TYPE.value
        }

    if check_result == Question.PIZZA_TYPE:
        details.pizza_type = user_mesage
        return {
            "output": Question.ADDRESS.value
        }

    if check_result == Question.ADDRESS:
        details.address = user_mesage
        return {
            "output": Question.PHONE.value
        }

    if check_result == Question.PHONE:
        details.phone = user_mesage
        del cat.working_memory[KEY]
        return {
            "output": f"{details.dict()}"
        }
    

    log.critical("DETAILS")
    print(details.dict())

    cat.working_memory[KEY] = details