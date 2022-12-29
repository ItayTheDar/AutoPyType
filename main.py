"""
Author: Itay Dar
Date: 2022-12-12

Description:

The purpose of this library is to enable users to cover their code with types hints even if it is an old code base.
The library is based on the idea of the "typeguard" library, but it is more flexible and more powerful.

package flow:

the input is a python file, the output is a python file with the same name but with the suffix "_typed.py".
when the input file is entered, we parse it and send it to ChatGPT that generates an output file.
then you can run the output file and see the results.

"""
import os
from pathlib import Path
import timeit
import openai
import logging
from openai.openai_object import OpenAIObject

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def send_request_to_openai(model: str, prompt: str, max_tokens: int) -> OpenAIObject:
    """
    send request to openai by using the completion api
    :param model: model name (e.g. "text-davinci-003")
    :param prompt: the prompt to send to openai
    :param max_tokens: number of tokens to send to openai
    :return: the response from openai
    """
    return openai.Completion.create(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens
    )


def create_typed_python_file(api_key: str, prompt: str, window: int = 20, max_len: int = 100, max_tokens=42) -> str:
    """
    create typed python file by using openai api, and especially the chatgpt model that help us to add type hints, logs and comments, and more.
    :param api_key: the api key of openai - you can get it from https://beta.openai.com/
    :param prompt: the prompt to send to openai (the python file + instructions what to do)
    :param window: the window size - which part of the prompt to send to openai (the last window size words
    :param max_len: the maximum length of the output
    :param max_tokens: the maximum number of tokens to send to openai in each batch
    :return: the function return a python file in a string format.
    """
    global location_end_prompt
    openai.api_key = api_key
    logger.info("api key is set")
    code = prompt
    i = 0
    while len(code.split(" ")) < max_len:
        logger.info("code is less than max_len - starting to generate the next piece of the code")
        response = send_request_to_openai("text-davinci-003", code, max_tokens)
        logger.info(f"response is ready")
        old_code = code
        if i == 0:
            location_end_prompt = len(old_code)
        code += response.choices[0].text
        if old_code == code:
            logger.info("code is not changing - breaking the loop")
            break
        logger.info(f"code is ready - {code}")
        prompt = " ".join(code.split(" ")[-window:])
        logger.info(f"next prompt is ready - {prompt}")
    # import pprint
    # pprint.pprint(code)

    return code[location_end_prompt:]


if __name__ == '__main__':
    ABSOLUTE_PATH = Path(__file__).parent.absolute()
    python_path = ABSOLUTE_PATH / "examples/example.py"
    python_file = open(python_path, "r").read()
    base_prompt = "\n this is the code:\n" + python_file
    base_tokens = 4096
    instructions = [
        "please add type hints to each and every variable in each class or function, remain imports as they are and add import statements if needed",
        "add logs to the code using logging library",
        "add documentation to each and every class or function",
        # "please make sure that every package that is used in the code is imported and fix bugs if needed",
    ]
    for instruction in instructions:
        s = timeit.default_timer()
        logger.info(f"starting to generate code for instruction - {instruction}")
        code = create_typed_python_file(
            api_key=os.getenv("OPENAI_API_KEY"),
            prompt= instruction + "\nthis is the code:\n" + base_prompt,
            window=len(base_prompt.split(" ")) - 1,
            max_len=len(base_prompt.split(" ")) + 100,
            max_tokens=base_tokens - len(base_prompt.split(" ")) - len(instruction.split(" ")) - 5
        )
        base_prompt = code

    with open(ABSOLUTE_PATH / "examples/example_typed_2.py", "w") as f:
        f.write(base_prompt)




    # python_typed_file = create_typed_python_file(
    #     api_key=os.getenv('OPENAI_API_KEY'),
    #     prompt=prompt,
    #     window=20,
    #     max_len=len(prompt.split(" ")) + 100,
    #     max_tokens=base_tokens - len(prompt.split(" "))
    # )
    # rand = "Today is the the day that I will start to learn how to use openai, this is so exciting, I can't wait to start. "
    #            "by gaining the abbility to use openai I will be able to do so many things, I will be able to create a "
#         api_key = os.environ['OPENAI_API_KEY']
#     openai.api_key = api_key
#     # list engines
#     engines = openai.Engine.list()
#
#     # print the first engine's id
#     # print(engines.data[0].id)
#
#     # create a completion
#     completion = openai.Completion.create(engine="ada", prompt="Hello world")
#
#     # print the completion
#     # print(completion.choices[0].text)
#
#     # prompt = "say this is a text"
#     response = openai.Completion.create(
#     model = "text-davinci-003",
#     prompt = prompt,
#     max_tokens = 7,
#     temperature = 0
#
# )
# print(response.choices[0].text)
# print(response)

# import requests
#
# url = "https://api.openai.com/v1/edits"
#
# payload = {
#     "model": "text-davinci-edit-001",
#     "input": "What day of the wek is it?",
#     "instruction": "Fix the spelling mistakes"
# }
# headers = {
#     "Content-Type": "application/json",
#     "Authorization": f"Bearer {api_key}"
# }
#
# response = requests.request("POST", url, json=payload, headers=headers)
#
# print(response.text)
