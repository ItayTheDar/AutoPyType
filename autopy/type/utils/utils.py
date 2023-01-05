from typing import List
import threading
import openai
from pathlib import Path
from autopy.models.models import ModelType



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


def slice_and_complete(filepath: Path, instruction: str, number_of_workers=2) -> None:
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
