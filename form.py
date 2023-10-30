import json

from cat.log import log

from pydantic import ValidationError

class Form:
    
    def __init__(self, model, cat):
        self.model = model
        self.cat = cat

    def is_complete(self):
        for k,v in self.model.model_dump().items():
            if v is None:
                return False
        return True
    
    def completion_utterance(self):
        
        return f"""Pizza order COMPLETE:

```json
{self.model.model_dump_json()}
```
"""

    def ask_missing_information(self):

        #missing_fields = { k:v for k, v in self.model_dump().items() if v is None}

        user_message = self.cat.working_memory["user_message_json"]["text"]
        chat_history = self.cat.agent_manager.agent_prompt_chat_history(
            self.cat.working_memory["history"]
        )

        prefix = self.cat.mad_hatter.execute_hook("agent_prompt_prefix",'')

        prompt = f"""{prefix}
        
Create a question for the user, to recap and fill up the null/None fields in the following JSON:

{{
    "pizza_type": "Margherita",
    "address": "Via Roma 1",
    "phone": null
}}
Human: I want to order a Margherita pizza
AI: Margherita! Greate choice, what address can I deliver it to?
Human: I live in Via Roma 1
AI: A margherita pizza in Via Roma 1, I need a phone number to contact you, can you provide me with one?
        
{{
    "pizza_type": "Margherita",
    "address": null,
    "phone": null
}}
Human: Can ypu order a Marghetia pizza for me?
AI: Margherità! Greate choice, what address can I deliver it to?
Human: I've changed my mind, maybe an Ortolana pizza is better
AI: No problem, I replace Margherita with Ortolana, what is the delivery address?

{{
    "pizza_type": null,
    "address": null,
    "phone": null
}}
Human: I want to order a pizza
AI: Sure, what kind of pizza would you like?

{self.model.model_dump_json(indent=4)}
{chat_history}
Human: {user_message}
AI: """

        log.warning("--------")
        print(prompt)
        question = self.cat.llm(prompt)
        return question 

    def update(self):

        # extract new info
        details = self._extract_info()

        # update form
        new_details = self.model.model_dump() | details

        if new_details == self.model.model_dump():
            return False

        try:
            self.model.model_validate(new_details)
        except ValidationError as e:
            for error_message in e.errors():
                return error_message["msg"]

        self.model = self.model.model_construct(**new_details)
        return True

    def _extract_info(self):

        user_message = self.cat.working_memory["user_message_json"]["text"]
        prompt = f"""Update the following JSON with information extracted from the Sentence:

Sentence: I want to order a pizza
JSON:{{
    "pizza_type": null,
    "address": null,
    "phone": null
}}
UPDATED JSON:{{
    "pizza_type": null,
    "address": null,
    "phone": null
}}

Sentence: I live in Via Roma 1
JSON:{{
    "pizza_type": "Margherita",
    "address": null,
    "phone": null
}}
Updated JSON:{{
    "pizza_type": "Margherita",
    "address": "Via Roma 1",
    "phone": null
}}

Sentence: {user_message}
JSON:{self.model.model_dump_json(indent=4)}
Updated JSON:"""
        
        print(prompt)

        json_str = self.cat.llm(prompt)

        return json.loads(json_str)

    #def search_memory():
    #def submit():
