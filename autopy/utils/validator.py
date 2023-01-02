from pathlib import Path
from typing import Dict


class Validator:

    def __init__(self):
        """
        Validator class for validating the input parameters.
        """
        self.score: int = 0
        self.score_per_argument: Dict[str, int] = {}

    def validate_function_signature(self, line: str) -> bool:
        """
        this function takes as input a function signature and make sure that it has type hints.
        :param line: the function signature
        :return: the function signature with type hints
        """
        statements = [
            "->" in line,
            "def" in line,
            "(" in line,
            ")" in line
        ]
        args = line.split("(")[1].split(")")[0].split(",")
        for arg in args:
            if arg == "self":
                continue
            else:
                statements.append(":" in arg)
        self.score_per_argument.update(
            {

            }
        )
        if all(statements):
            return True
        else:
            return False

    @staticmethod
    def validate_var(line: str) -> bool:
        """
        this function takes as input a variable assignment and make sure that it has type hints.
        :param line: the variable assignment
        :return: the variable assignment with type hints
        """
        statements = [
            "=" in line,
            ":" in line
        ]
        try:
            hint = line.split(":")[1].split("=")[0].strip()
        except IndexError:
            return False
        if all(statements):
            return True
        else:
            return False


import ast


class ValidatorParser:
    def __init__(self):
        """
        Validator class for validating the input parameters.
        """
        # counter count the number of variables and functions that don't have type hints
        # total count the total number of variables and functions at the file that can be type hinted in a perfect world
        self.counter = 0
        self.total = 0

    def validate(self, filepath: str) -> float:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())

        # Validate variable declarations
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign):
                self.counter += 1
                self.total += 1
            elif isinstance(node, ast.Assign):
                self.total += 1

        # Validate function type hints
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.returns:
                    self.counter += 1
                self.total += 1
                for arg in node.args.args:
                    if arg.annotation:
                        self.counter += 1
                    self.total += 1

        # Calculate score
        score = (self.counter / self.total)
        self.counter = 0
        self.total = 0
        return score


if __name__ == '__main__':
    path = Path(__file__).parent.parent.parent
    val = ValidatorParser()
    print(val.validate(path / "examples/example.py"))
    # print(val.validate(path / "examples/test.py"))
    print(val.validate(path / "examples/example_typed.py"))
    # print(val.validate_function_signature("def hello(a: int, b: int) -> int:"))
