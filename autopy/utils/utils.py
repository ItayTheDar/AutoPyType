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
