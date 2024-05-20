from typing import List, Dict, Any, Union, Optional
import logging
import time
from openai import OpenAI
import json 
import re

EMBEDDINGS_MODEL="text-embedding-3-large"

def extract_json_response(text):
    matches = re.findall(r"```json(.*?)```", text, re.DOTALL)

    if len(matches) == 0:
        matches = re.findall(r"```(.*?)```", text, re.DOTALL)
        if len(matches) == 0:
            return None 
        elif len(matches) > 1:
            raise Exception("Found more than 1 json string.")

    json_string = matches[0]
    return json_string

def str_2_json(_str: str) -> str:
    try:
        return json.loads(extract_json_response(_str))
    except:
        return json.loads(_str) 
def openai_embeddings(text: str) -> List[float]:
    client = OpenAI()
    embeddings = client.embeddings.create(
                    model=EMBEDDINGS_MODEL,
                    input=text,
                    encoding_format="float"
                )
    return embeddings.data[0].embedding

def openai_call(system_message, user_message, history: List[Dict[str, Any]] = [], model: str = 'gpt-4-turbo', is_json=False) -> Union[dict, str]:
    client = OpenAI()

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            *history,
            {"role": "user", "content": user_message}
        ]
    )
    response = completion.choices[0].message.content
    return str_2_json(response) if is_json else response