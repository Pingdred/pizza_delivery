from cat.mad_hatter.decorators import hook, tool
from pydantic import BaseModel, field_validator, ValidationError
from typing import Dict

from cat.log import log

from cat.plugins.pizza_delivery.form import Form
KEY = "pizza_delivery"


class PizzaOrder(BaseModel):
    pizza_type: str | None = None
    address: str | None = None
    phone: str | None = None

    @field_validator("pizza_type")
    @classmethod
    def validate_pizza_type(cls, pizza_type: str):
        log.critical("VALIDATIONS")

        available_pizzas = [
            "Margherita",
            "Marinara",
            "Boscaiola",
            "Napoletana",
            "Capricciosa",
            "Diavola",
            "Ortolana"
        ]

        if pizza_type not in available_pizzas:
            raise ValueError(f"{pizza_type} is not present in the menù")



@tool(return_direct=True)
def order_pizza(details, cat):
    '''Use this tool to order one pizza'''

    f = Form(model=PizzaOrder(), cat=cat)
    
    # update form
    f.update()

    if f.is_complete():
        return f.completion_utterance()
    else:
        cat.working_memory[KEY] = f
        return f.ask_missing_information()


@hook
def agent_fast_reply(fast_reply: Dict, cat) -> Dict:

    if KEY not in cat.working_memory.keys():
        log.critical("NO KEY")
        return fast_reply
    
    log.critical(f"WORKING MEMORY: {KEY})")
    print(cat.working_memory[KEY])

    f = cat.working_memory[KEY]

    # update form
    if not f.update():
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

