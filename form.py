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

        prefix = self.cat.mad_hatter.execute_hook("agent_prompt_prefix",'')

        prompt = f"""{prefix}
        
Create a question for the user, to recap and fill up the null/None fields in the following JSON:

{{
    "pizza_type": "Margherita",
    "address": "Via Roma 1",
    "phone": null
}}
User: Sure, I live in Via Roma 1
Question: A margherita pizza in Via Roma 1, I need a phone number to contact you, can you provide me with one?
        
{{
    "pizza_type": "Margherita",
    "address": null,
    "phone": null
}}
User: I've changed my mind, maybe a margherita pizza is better
Question: Margherità! Greate choice, what address can I deliver it to?


{self.model.model_dump_json(indent=4)}
User: {user_message}
Question: """

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

        Sentence: Sure, i want a pizza margherita
        JSON: {{
            "pizza_type": null,
            "address": "Via Roma 1",
            "phone": null
        }}
        Updated JSON:{{
            "pizza_type": "Margherita",
            "address": "Via Roma 1",
            "phone": null
        }}
        
        Sentence: {user_message}
        JSON: {self.model.model_dump_json(indent=4)}
        Updated JSON: """
        
        print(prompt)

        json_str = self.cat.llm(prompt)

        return json.loads(json_str)

    #def search_memory():
    #def submit():
