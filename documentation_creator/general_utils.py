from typing import Dict, List
import httpx
import logging
import time
from openai import OpenAI
import json 
import re

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


def llm(system_message: str, user_message: str, history: List[Dict[str, str]] = [], model = "gpt-4-turbo", is_json = False) -> List[str]:
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