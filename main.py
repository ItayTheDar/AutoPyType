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
from typing import List, Union, Dict, Any, Optional, Tuple, Callable, TypeVar, Generic, Type, Set, Iterable, Iterator
import timeit
import openai
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_file_from_path(path: Path) -> str:
    """
    get file from path
    :param path: path to the python file that user want to add type hints
    :return: string of the python file
    """
    with open(path, 'r') as f:
        return f.read()


def send_file_in_batch_to_gpt(file: str, batch_size: int = 10) -> List[str]:
    """
    send file in batch to gpt
    :param file: the file to send
    :param batch_size: the batch size
    :return: list of batches
    """
    return [file[i:i + batch_size] for i in range(0, len(file), batch_size)]


def create_connection_openai():
    """create connection openai"""
    pass


def send_batch_to_openai(batch: str) -> str:
    """send batch to openai"""
    pass


def send_file_to_openai(file: str, batch_size: int = 10) -> List[str]:
    """send file to openai"""
    batches = send_file_in_batch_to_gpt(file, batch_size)
    return [send_batch_to_openai(batch) for batch in batches]


def create_typed_python_file(api_key: str, prompt: str, window: int = 20, max_len: int = 100, max_tokens=42):
    global location_end_prompt
    import openai
    logger.info("creating a story")
    openai.api_key = api_key
    logger.info("api key is set")
    story = prompt
    logger.info("story is set")
    i = 0
    while len(story.split(" ")) < max_len:
        logger.info("story is less than max_len - starting to generate the next piece of the story")
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=max_tokens
        )
        logger.info(f"response is ready - {response.choices[0].text}")
        old_story = story
        if i == 0:
            location_end_prompt = len(old_story)
        story += response.choices[0].text
        if old_story == story:
            logger.info("story is not changing - breaking the loop")
            break
        logger.info(f"story is ready - {story}")
        prompt = " ".join(story.split(" ")[-window:])
        logger.info(f"next prompt is ready - {prompt}")
    import pprint
    pprint.pprint(story)

    return story[location_end_prompt:]


if __name__ == '__main__':
    # prompt = "please complete this story: \nThis is story about two friends that went out for a tour in northern india, they've went down from the bus in the city of delhi and then ...  "
    # prompt = "please generate a function that will get a list of numbers and return the sum of the numbers: \n def sum_of_numbers(numbers):"
    # prompt = "please create a small flask application that helps students to sign they're courses\n Notes: make this function with types, logs and well documented:"
    python_file = open("/Users/itayd/PycharmProjects/AutoPyType/examples/example.py", "r").read()
    prompt = "please add type hints to each and every variable in each" \
             " class or function. if the type is not yet imported, " \
             "please import it. also, please add logs to the code using logging library." \
             "\n this is the code:\n" + python_file
    base_tokens = 4096
    python_typed_file = create_typed_python_file(
        api_key=os.getenv('OPENAI_API_KEY'),
        prompt=prompt,
        window=50,
        max_len=len(prompt.split(" ")) + 100,
        max_tokens=base_tokens - len(prompt.split(" "))
    )
    print(python_typed_file)
    with open("/Users/itayd/PycharmProjects/AutoPyType/examples/example_typed.py", "w") as f:
        f.write(python_typed_file)
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
