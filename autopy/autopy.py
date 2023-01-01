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
from typing import Union
from utils.validator import Validator
import openai
import logging
from openai.openai_object import OpenAIObject
from openai.error import InvalidRequestError
from models.models import ModelType

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AutoPy:
    def __init__(self, api_key: str, path: Union[str, Path], model: str = ModelType.TEXT_DAVINCI_003.value) -> None:
        openai.api_key = api_key
        logger.info("api key is set")

        self.path = path
        self.python_file = open(self.path, "r").read()
        self.model = model
        self.validator = Validator()
        self.base_prompt = "\n this is the code:\n" + self.python_file
        self.base_tokens = 4096
        self.instructions = [
            "add type hints to each and every variable in each class or function",
            "add logs to the code using logging library add documentation to each and every class or function"
        ]

    def send_request_to_openai(self, prompt: str, max_tokens: int) -> OpenAIObject:
        """
        send request to openai by using the completion api
        :param prompt: the prompt to send to openai
        :param max_tokens: number of tokens to send to openai
        :return: the response from openai
        """
        return openai.Completion.create(
            model=self.model,
            prompt=prompt,
            max_tokens=max_tokens
        )

    def create_typed_python_file(self, prompt: str, window: int = 20, max_len: int = 100, max_tokens=42) -> str:
        """
        create typed python file by using openai api, and especially the chatgpt model that help us to add type hints, logs and comments, and more.
        :param prompt: the prompt to send to openai (the python file + instructions what to do)
        :param window: the window size - which part of the prompt to send to openai (the last window size words
        :param max_len: the maximum length of the output
        :param max_tokens: the maximum number of tokens to send to openai in each batch
        :return: the function return a python file in a string format.
        """
        global location_end_prompt
        code = prompt
        i = 0
        while len(code.split(" ")) < max_len:
            logger.info("code is less than max_len - starting to generate the next piece of the code")
            for _ in range(5):
                try:
                    response = self.send_request_to_openai(code, max_tokens)
                    break
                except InvalidRequestError as e:
                    logger.error(f"error: {e}")
                    # if the error is because of the max_tokens, we will reduce the max_tokens by 10% and try again
                    if "max_tokens" in str(e):
                        max_tokens = int(max_tokens * 0.9)
                        logger.info(f"max_tokens was too high, reducing it to {max_tokens}")
                        continue
            logger.info(f"response is ready")
            old_code = code
            if i == 0:
                location_end_prompt = len(old_code)
            code += response.choices[0].text
            if old_code == code:
                logger.info("code is not changing - breaking the loop")
                break
            prompt = " ".join(code.split(" ")[-window:])
            logger.info(f"new prompt is ready")
        # import pprint
        # pprint.pprint(code)

        return code[location_end_prompt:]

    def _validate_file(self, python_file: str) -> bool:
        """
        this function takes as input the new generated python file and make sure that each and every var has type hint as well as function signatures.
        :param python_file: the generated python file that gpt model output
        :return: python
        """
        parsed_python_file = python_file.split("\n")
        for i, line in enumerate(parsed_python_file):
            if line.startswith("def"):
                if self.validator.validate_function_signature(line):
                    continue
                else:
                    logger.info(f"line {i} is not valid")
                    return False
            if "=" in line and not line.startswith("def") and not line.startswith("class"):
                parsed_python_file[i] = self.validator.validate_var(line)

    def run(self) -> None:
        """
        run the autopy library
        :return: None
        """
        prompt = " ".join(self.instructions) + self.base_prompt
        typed_code = self.create_typed_python_file(
            prompt=prompt,
            window=len(self.base_prompt.split(" ")) - 1,
            max_len=len(self.base_prompt.split(" ")) + 100,
            max_tokens=self.base_tokens - len(self.base_prompt.split(" ")) - len(
                " ".join(self.instructions).split(" ")) - 5,
        )
        typed_python_path = Path(self.path).parent / f"{Path(self.path).stem}_typed.py"
        self._validate_file(typed_code)
        with open(typed_python_path, "w") as f:
            f.write(typed_code)
        logger.info(f"typed python file is ready in {typed_python_path}")


if __name__ == '__main__':
    autopy = AutoPy(
        api_key=os.getenv("OPENAI_API_KEY"),
        path=Path(__file__).parent.parent / "examples" / "example.py"
    )
    autopy.run()
