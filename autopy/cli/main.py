import os
from pathlib import Path
import timeit
import openai
import logging
from openai.openai_object import OpenAIObject
import click
from typing import List, Union
from autopy.autopy import AutoPy
from autopy.models.models import ModelType


@click.group()
def autopy_cli() -> None:
    pass


@autopy_cli.command(
    help="convert python code to python code with type hints",
)
@click.option(
    "-p",
    "--path",
    required=True,
    type=str,
    help="Path to a python file.",
)
@click.option(
    "--api_key",
    required=True,
    type=str,
    help="API key of openai",
)
@click.option(
    "--m",
    "--model",
    optional=True,
    type=str,
    help="choose model to use",
)
def run(path: Union[str, List[str]], api_key: str, model: str = ModelType.TEXT_DAVINCI_003) -> None:
    autopy = AutoPy(path=path, api_key=api_key, model=model)
    autopy.run()
