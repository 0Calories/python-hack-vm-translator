from .parser import Command

class CodeWriter:
    def __init__(self, output_file_path: str):
        self.output_file = open(output_file_path, "w")
        if not self.output_file:
            raise FileNotFoundError(f"Could not open output file: {output_file_path}")

    def write_command(self, command: Command):
        print(command)

    def close(self):
        self.output_file.close()

