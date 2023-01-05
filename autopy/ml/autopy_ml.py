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
from typing import Union, Dict
import openai
import logging
from openai.openai_object import OpenAIObject
from openai.error import InvalidRequestError
import threading
import openai
# from autopy.models.models import ModelType
import pandas as pd
from nbconvert import NotebookExporter
import nbformat as nbf

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AutoPyML:
    def __init__(
            self,
            api_key: str,
            path_to_csv: Union[str, Path],
            target: str,
            task: str = "predict",
            model: str = "text-davinci-003"
    ) -> None:
        openai.api_key = api_key
        logger.info("api key is set")

        if isinstance(path_to_csv, str):
            self.path = Path(path_to_csv)
        else:
            self.path = path_to_csv
        assert os.path.exists(self.path), "the path to the csv file does not exist"
        assert Path(self.path).suffix == ".csv", "the path to the csv file is not a csv file"

        self.df = pd.read_csv(self.path)
        self.target = target
        assert self.target in self.df.columns, "the target column does not exist in the csv file"

        self.base_tokens = 4096

        self.model = model
        self.task = task
        self.prompt = self.create_prompt(self.task)

    def create_prompt(self, task: str) -> str:
        col_to_type: Dict[str, str] = {
            col: self.df[col].dtype for col in self.df.columns
        }
        if task == "predict":
            prompt = f"create a python code that takes as input a csv file named {self.path.stem} and returns a model that can predict the target column - {self.target}." \
                     "\nInstructions:" \
                     "\n import necessary libraries" \
                     "\n1. load the data from path variable" \
                     "\n2. use label encoder to handle categorical and binary data" \
                     "\n3. drop nulls by axis=0" \
                     f"\n4. split df into target(y) and features(X) where y={self.target}" \
                     "\n5. use standard scaler to scale the data of X" \
                     "\n6. split the data into train and test" \
                     "\n6. add grid search to 5 models with 3 params each" \
                     "\n7. loop over all the models and grid search for every one" \
                     "\n8. save all scores, print them and print the best model, parameters and score" \
                     "\nthe data structure is as following: \n\n" + " | ".join(
                [f"{col}:{col_to_type[col]}" for col in self.df.columns])
        elif task == "analysis":
            prompt = f"create a python code that takes as input a csv file named {self.path.stem} and perform deep data analysis" \
                     f"\nusing pandas, matplotlib, seaborn and more." \
                     f"\ncreate 10 different charts both with sns and pyplot" \
                     f"\ncheck number of nulls and add statistics of the table and for each column" \
                     "\nthe data structure is as following: \n\n" + " | ".join(
                    [f"{col}:{col_to_type[col]}" for col in self.df.columns])
        else:
            raise ValueError("task must be either predict or analysis")
        return prompt

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

    def save_code_into_notebook(self, python_file: str) -> str:
        notebook = nbf.v4.new_notebook()
        i = 0
        batch = []
        for i, line in enumerate(python_file.splitlines()):
            if line == "":
                continue
            if "#" in line:
                if line.startswith("#"):
                    if len(batch) > 0:
                        notebook["cells"].append(nbf.v4.new_code_cell("\n".join(batch)))
                        batch = []

                    if line[1] == " ":
                        notebook["cells"].append(nbf.v4.new_markdown_cell(line))
                    else:
                        line = line[0] + " " + line[1:]
                        notebook["cells"].append(nbf.v4.new_markdown_cell(line))
                else:
                    line = line[:line.index("#")]
                    batch.append(line)
            else:
                if i == len(python_file.splitlines()) - 1:
                    batch.append(line)
                    notebook["cells"].append(nbf.v4.new_code_cell("\n".join(batch)))
                batch.append(line)

        if os.path.isfile(f"{self.path.stem}_{self.task}_notebook.ipynb"):
            import random
            out_dir = f"{self.path.stem}_notebook_{random.randint(0, 100)}.ipynb"
        else:
            out_dir = f"{self.path.stem}_{self.task}_notebook.ipynb"
        with open(out_dir, "w") as f:
            nbf.write(notebook, f)
        with open(f"{self.path.stem}_{self.task}.py", "w") as f:
            f.write(python_file)

    def run(self):
        response = self.send_request_to_openai(self.prompt, self.base_tokens - int(len(self.prompt) // 3.14) - 100)
        with open("prediction_code.py", "w") as f:
            f.write(response.choices[0].text)
        self.save_code_into_notebook(response.choices[0].text)
        return response.choices[0].text


if __name__ == '__main__':
    # path = Path("/Users/itayd/PycharmProjects/openai-python/openai/openai_object.py")
    # path = Path(__file__).parent.parent.parent / "examples/test.py"
    path = Path("/Users/itayd/PycharmProjects/openai-python/openai/util.py")

    autopy = AutoPyML(
        api_key=os.getenv("OPENAI_API_KEY"),
        path_to_csv="/Users/itayd/PycharmProjects/AutoPyType/autopy/ml/examples/superstore_data.csv",
        target="Response",
        task="analysis"
    )
    # autopy.slice_and_complete(path, "Add a type hint to each and every variable and function (include return arrow).\n", number_of_workers=3)
    autopy.run()
    # autopy.save_code_into_notebook(open("/Users/itayd/PycharmProjects/AutoPyType/autopy/ml/superstore_data.py").read())
