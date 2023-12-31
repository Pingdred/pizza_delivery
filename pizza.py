from cat.mad_hatter.decorators import hook, tool
from pydantic import BaseModel, field_validator
from typing import Dict

from cat.log import log

from cat.plugins.pizza_delivery.form import Form
KEY = "pizza_delivery"

menu = [
            "Margherita",
            "Marinara",
            "Boscaiola",
            "Napoletana",
            "Capricciosa",
            "Diavola",
            "Ortolana"
        ]



class PizzaOrder(BaseModel):
    pizza_type: str | None = None
    address: str | None = None
    phone: str | None = None

    @field_validator("pizza_type")
    @classmethod
    def validate_pizza_type(cls, pizza_type: str):
        log.critical("VALIDATIONS")

        if pizza_type is None:
            return

        if pizza_type not in menu:
            raise ValueError(f"{pizza_type} is not present in the menù")



@tool(return_direct=True)
def order_pizza(details, cat):
    '''I would like to order a pizza
I'll take a Margherita pizza'''

    f = Form(model=PizzaOrder(), cat=cat)
    
    # update form
    res = f.update()

    log.critical(res)

    if isinstance(res, str):
        log.critical("VALIDATION ERROR")
        return res

    if f.is_complete():
        return f.completion_utterance()
    else:
        cat.working_memory[KEY] = f
        return f.ask_missing_information()


@tool()
def pizza_menu(input, cat):
    '''What is on the menu?
Which types of pizza do you have?'''

    responce = "The available pizzas are the following:"
    for pizza in menu:
        responce += f"\n - {pizza}"

    return responce

@hook
def agent_fast_reply(fast_reply: Dict, cat) -> Dict:

    if KEY not in cat.working_memory.keys():
        log.critical("NO KEY")
        return fast_reply
    
    log.critical(f"WORKING MEMORY: {KEY})")
    print(cat.working_memory[KEY])

    f = cat.working_memory[KEY]

    res = f.update()
    if isinstance(res, str):
        return {
            "output": res
        }
    # There is no information in the new message that can update the form
    elif res is False:
        return

    if f.is_complete():
        utter = f.completion_utterance()
        del cat.working_memory[KEY]
    else:
        cat.working_memory[KEY] = f
        utter = f.ask_missing_information()
        
    return {
        "output": utter
    }

