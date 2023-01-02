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
import threading
import openai

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
            "add type hints to each and every variable in each class, follow the PEP8 guidelines",
            # "add logs to the code using logging library add documentation to each and every class or function"
        ]
        self.imports = "\n".join([line for line in self.python_file.split("\n") if
                                  line.strip(" ").startswith("import") or line.strip(" ").startswith("from")])

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

        for _ in range(3):
            try:
                response = self.send_request_to_openai(code, max_tokens)
                return response.choices[0].text
            except InvalidRequestError as e:
                logger.error(f"error: {e}")
                # if the error is because of the max_tokens, we will reduce the max_tokens by 10% and try again
                if "max_tokens" in str(e):
                    max_tokens = int(max_tokens * 0.9)
                    logger.info(f"max_tokens was too high, reducing it to {max_tokens}")
                    continue
        return Exception("error in creating typed python file")
        # logger.info(f"response is ready")
        # old_code = code
        # if i == 0:
        #     location_end_prompt = len(old_code)
        # else:
        #     code += response.choices[0].text
        # if old_code == code:
        #     logger.info("code is not changing - breaking the loop")
        #     break
        # prompt = " ".join(code.split(" ")[-window:])
        # logger.info(f"new prompt is ready")
        # import pprint
        # pprint.pprint(code)

        # return code[location_end_prompt:]

    def validate_file(self, python_file: str) -> bool:
        """
        this function takes as input the new generated python file and make sure that each and every var has type hint as well as function signatures.
        :param python_file: the generated python file that gpt model output
        :return: python
        """
        parsed_python_file = python_file.split("\n")
        for i, line in enumerate(parsed_python_file):
            if line.strip(" ").startswith("def"):
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
            max_tokens=self.base_tokens - len(self.base_prompt.split(" ")) - 100
        )
        typed_python_path = Path(self.path).parent / f"{Path(self.path).stem}_typed.py"
        # self.validate_file(typed_code)
        typed_code = "\n".join([line for line in typed_code.split("\n") if line not in self.imports.split("\n")])
        typed_code = self.imports + "\n" + typed_code

        with open(typed_python_path, "w") as f:
            f.write(typed_code)
        logger.info(f"typed python file is ready in {typed_python_path}")

    def slice_and_complete(self, filepath: Path, instruction: str, number_of_workers=2) -> None:
        """Slices a Python file into 4 chunks and uses OpenAI's Completion API to complete each chunk with the given instruction.

        Args:
        - filepath (str): The filepath of the Python file to slice.
        - instruction (str): The instruction to provide to the Completion API.

        """
        output = [None] * number_of_workers
        # Read the Python file
        with open(filepath, "r") as f:
            contents = f.read()

        imports = "\n".join([line for line in contents.split("\n") if
                             line.strip(" ").startswith("import") or line.strip(" ").startswith("from")])

        # Split the file into 4 chunks
        chunk_size = len(contents) // number_of_workers
        chunks = {i: contents[i * chunk_size:(i + 1) * chunk_size] for i in range(number_of_workers)}

        # Create a list of threads
        threads = []

        # Define a completion function
        def complete_chunk(chunk: str, chunk_number: int) -> None:
            # Use the Completion API to complete the chunk
            model_engine = ModelType.TEXT_DAVINCI_003.value
            if chunk_number == 0:
                prompt = f"{instruction}\n{chunk}"
            else:
                prompt = f"{instruction}\n{imports}\n{chunk}"
            completions = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=4096 - len(prompt))
            # Print the completions
            print(completions.choices[0].text)
            output[chunk_number] = completions.choices[0].text

        # Create a thread for each chunk
        for chunk in chunks:
            thread = threading.Thread(target=complete_chunk, args=(chunks[chunk], chunk))
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Write the output to a file
        for i, chunk in enumerate(output):
            with open(filepath.parent / f"{filepath.stem}_typed_{i}.py", "w") as f:
                f.write(chunk)

        with open(filepath.parent / f"{filepath.stem}_typed.py", "w") as f:
            f.write("".join(output))

        # output_file = "".join(output)
        # for line in contents.split("\n"):
        #     if line


if __name__ == '__main__':
    # path = Path("/Users/itayd/PycharmProjects/openai-python/openai/openai_object.py")
    path = Path(__file__).parent.parent.parent / "examples/test.py"

    autopy = AutoPy(
        api_key=os.getenv("OPENAI_API_KEY"),
        path="/Users/itayd/PycharmProjects/AutoPyType/examples/test.py",
    )
    # autopy.slice_and_complete(path, "Add a type hint to each and every variable and function (include return arrow).\n", number_of_workers=3)
    autopy.run()
