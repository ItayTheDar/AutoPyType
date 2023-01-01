
class Validator:

    def __init__(self):
        pass

    @staticmethod
    def validate_function_signature(line: str) -> bool:
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
            statements.append(":" in arg)
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


if __name__ == '__main__':
    val = Validator()
    print(val.validate_function_signature("def hello(a: int, b: int) -> int:"))