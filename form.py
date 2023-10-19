from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Dict

from cat.log import log

# class Question(Enum):
#     CORNER = "Do you prefer hight corner or low corner?"
#     PIZZA_TYPE = "Wich pizza do you prefer?"
#     ADDRESS = "What is your address?"
#     PHONE = "What is your phone number?"
#     COMPLETE = "Pizza ordinata"

# class Corner(Enum):
#     Hight = "Hight"
#     Low = "Low"

class Form(BaseModel):
    #corner: Corner = None
    pizza_type: str | None = None
    address: str | None = None
    phone: str | None = None
    
    def is_complete(self):
        for k,v in self.model_dump().items():
            if v is None:
                return False
        return True
    
    def completion_utterance(self):
        
        return f"""Pizza order COMPLETE:

```json
{self.model_dump_json()}
```

I'm also sending a couple of additional pizza to Nicola and Daniele as a consolation prize :')
"""

    def ask_user_utterance(self, cat):

        #missing_fields = { k:v for k, v in self.model_dump().items() if v is None}

        prompt = f"""Create a question for the user, to recap and fill up the null/None fields in the following JSON:

{self.model_dump_json(indent=4)}

Question: """
        log.warning("--------")
        print(prompt)
        question = cat.llm(prompt, stream=True)
        return question 


    #def search_memory():
    #def submit():
