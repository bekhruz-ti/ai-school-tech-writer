from general_utils import openai_call
from gdrive_utils import download_document
from prompts import TEMPLATE_PARSER_SYSTEM_PROMPT, TEMPLATE_FILLER_SYSTEM_PROMPT

def build_queries(template_id):

    metadata, content = download_document(template_id)

    queries = openai_call(TEMPLATE_PARSER_SYSTEM_PROMPT, content, is_json = True)

    return queries

def fill_template(information, template_id):

    metadata, content = download_document(template_id)

    filled_template = openai_call(TEMPLATE_FILLER_SYSTEM_PROMPT.format(information=information), content)

    return filled_template




