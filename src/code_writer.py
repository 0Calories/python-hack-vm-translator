from .parser import Command, CommandType, ArithmeticCommand

MEMORY_SEGMENT_MAP = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT"
}

STACK_POINTER = "SP"

class CodeWriter:
    def __init__(self, output_file_path: str):
        if not output_file_path.endswith(".asm"):
            raise ValueError(f"Invalid file extension: {output_file_path}")

        self.output_file = open(output_file_path, "w")
        if not self.output_file:
            raise FileNotFoundError(f"Could not open output file: {output_file_path}")
        
    def write_command(self, command: Command):
        if command.type == CommandType.C_ARITHMETIC:
            self.write_arithmetic(command)
        elif command.type == CommandType.C_PUSH or command.type == CommandType.C_POP:
            self.write_push_pop(command)

    def write_arithmetic(self, command: Command):
        if command.arg1 == ArithmeticCommand.ADD:
            self.output_file.write("// add\n")
        elif command.arg1 == ArithmeticCommand.SUB:
            self.output_file.write("// sub\n")
        elif command.arg1 == ArithmeticCommand.NEG:
            self.output_file.write("// neg\n")
        elif command.arg1 == ArithmeticCommand.EQ:
            self.output_file.write("// eq\n")
        elif command.arg1 == ArithmeticCommand.GT:
            self.output_file.write("// gt\n")
        elif command.arg1 == ArithmeticCommand.LT:
            self.output_file.write("// lt\n")
        elif command.arg1 == ArithmeticCommand.AND:
            self.output_file.write("// and\n")
        elif command.arg1 == ArithmeticCommand.OR:
            self.output_file.write("// or\n")   
        elif command.arg1 == ArithmeticCommand.NOT:
            self.output_file.write("// not\n")

    def write_push_pop(self, command: Command):
        if not command.arg1 or not command.arg2:
            raise ValueError("Invalid command")
        
        if command.type == CommandType.C_POP and command.arg1 == "constant":
            raise ValueError("Cannot pop constant")
        
        if command.arg1 == "constant":
            self.output_file.writelines([
                f"// push constant {command.arg2}\n",
                f"@{command.arg2}\n",
                "D=A\n",
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "M=D\n"
            ])
            return
        
        if command.arg1 == "static":
            self.output_file.writelines([
                f"// push static {command.arg2}\n",
            ])
            return
        
        if command.arg1 not in MEMORY_SEGMENT_MAP:
            raise ValueError(f"Invalid memory segment: {command.arg1}")
        
        dest_segment = MEMORY_SEGMENT_MAP[command.arg1]

        if command.type == CommandType.C_PUSH:
            self.output_file.writelines([
                f"// push {command.arg1} {command.arg2}\n",
                # Take the address of the segment
                f"@{dest_segment}\n",
                "D=A\n",
                # Increment the address by the offset
                f"@{command.arg2}\n",
                f"D=D+A\n",
                # Take the value at the selected address and push it to the stack
                "A=D\n",
                "D=M\n",
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "M=D\n",
                # Increment the stack pointer
                f"@{STACK_POINTER}\n",
                "M=M+1\n"
            ])

    def close(self):
        self.output_file.close()

