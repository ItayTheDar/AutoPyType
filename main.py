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
from pathlib import Path
from typing import List, Union, Dict, Any, Optional, Tuple, Callable, TypeVar, Generic, Type, Set, Iterable, Iterator


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