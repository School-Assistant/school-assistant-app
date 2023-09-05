import os
import requests
from langchain.chat_models import ChatOpenAI
from langchain.prompts import load_prompt, ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.schema import AIMessage, HumanMessage, BaseMessage, SystemMessage, ChatMessage, FunctionMessage
from langchain import PromptTemplate
from langchain.chains import LLMChain

from dotenv import load_dotenv

import ast
import logging

# !!! requires following env variables set: OPENAI_API_KEY, WOLFRAM_APP_ID !!!

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()


THOUGHT_PROMPT = """Analyze the dialogue to understand the student's needs and current obstacles. Strategize on how to guide them towards the solution effectively. Consider what additional information could improve your guidance.

Current dialog:
{history}

User characteristics: 
Grade: 11
"""

SYSTEM_PROMPT = """Assist the student in solving math problems. Provide hints, ask questions, clarify concepts. Use Wolfram Alpha for internal validation but never reveal full solutions. If the user has arrived at a solution, you may confirm its correctness or provide corrections. Multiple approaches? Ask for preference.

{thought}

Remember to validate the solutions.

User Grade: 11
"""


function_descriptions = [
    {
        "name": "query_wolfram_alpha",
        "description": "Queries Wolfram Alpha to internally validate mathematical steps.",
        "example": "query_wolfram_alpha({'query': '2+2'})",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Wolfram Alpha-compatible query for validating equations or math problems."
                }
            },
            "required": ["query"]
        },
    }
]

def wolfram_alpha_query(query):
    base_url = "http://api.wolframalpha.com/v2/query"
    params = {
        "input": query,
        "format": "plaintext",
        "output": "JSON",
        "appid": os.environ['WOLFRAM_APP_ID']
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    # Check if the request was successful
    if data["queryresult"]["success"] and data["queryresult"]["numpods"] > 0:
        # Extracting results from relevant pods
        results = []
        for pod in data["queryresult"]["pods"]:
            for subpod in pod["subpods"]:
                results.append({ pod["title"]: subpod["plaintext"]})
        return results if results else "No relevant results found"
    else:
        return "No result found or query was not understood."
    

def get_llm_response(messages, llm, thought_llm):
    dialogue = []
    for m in messages:
        if isinstance(m, AIMessage):
            msg = f'AI: {m.content}'
        elif isinstance(m, HumanMessage):
            msg = f'Human: {m.content}'
        elif isinstance(m, FunctionMessage):
            msg = f'Function ({m.name}): {m.content}'
        else:
            raise Exception(f"Invalid message type: {type(m)}")
        
        dialogue.append(msg)

    dialogue = "\n".join(dialogue)

    thought_messages = [
        SystemMessage(content=THOUGHT_PROMPT.format(history=dialogue))
    ]

    thought_response = thought_llm.predict_messages(thought_messages)

    response_messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(thought=thought_response.content)),
        *messages
    ]

    response = llm.predict_messages(response_messages, functions=function_descriptions)

    logging.info(f"Received LLM response: {response}")

    if 'function_call' in response.additional_kwargs:
        messages.append(response) 

        function_name = response.additional_kwargs['function_call']['name']

        logging.info(f'Calling function: {function_name}')

        if function_name == 'query_wolfram_alpha':
            query = ast.literal_eval(response.additional_kwargs['function_call']['arguments']).get('query')
            
            function_response = wolfram_alpha_query(query)

            logging.info(f'Response from function {function_name}: {function_response}')

        message = FunctionMessage(
            name=function_name,
            content=str(function_response)
        )

        messages.append(message)

        return get_llm_response(messages, llm, thought_llm)


    messages.append(response)

    return response.content


def main():
    messages = []


    llm = ChatOpenAI(model='gpt-4-0613')
    thought_llm = ChatOpenAI(model='gpt-4-0613')
    
    logging.info("ChatBot started.")

    while True:
        user_request =  input('User: ')

        messages.append(HumanMessage(content=user_request))

        response = get_llm_response(messages, llm, thought_llm)

        print(f'ChatBot: {response}')

if __name__ == '__main__':
    main()
