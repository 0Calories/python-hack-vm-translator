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
            self.output_file.writelines([
                "// add\n",
                # Get the value at the top of the stack
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "D=M\n",
                # Clear the value at the top of the stack
                "M=0\n",
                # Decrement the stack pointer and add the stored value with the current value
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "M=D+M\n",
            ])
        elif command.arg1 == ArithmeticCommand.SUB:
            self.output_file.writelines([
                "// sub\n",
                # Get the value at the top of the stack
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "D=M\n",
                # Clear the value at the top of the stack
                "M=0\n",
                # Decrement the stack pointer and subtract the stored value with the current value
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "M=M-D\n",
            ])
        elif command.arg1 == ArithmeticCommand.NEG:
            self.output_file.writelines([
                "// neg\n",
                # Get the value at the top of the stack and make it negative
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "M=-M\n"
            ])
        elif command.arg1 == ArithmeticCommand.EQ:
            self.output_file.writelines([
                "// eq\n",
                # Get the value at the top of the stack
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "D=M\n",
                # Clear the value at the top of the stack
                "M=0\n",
                # Decrement the stack pointer and subtract the stored value with the current value
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "D=M-D\n",
                # Jump logic to set the value at the top of the stack to 1 if the result is 0
                "@IS_EQ\n",
                "D;JEQ\n",
                "(NOT_EQ)\n",
                "   @{STACK_POINTER}\n",
                "   A=M\n",
                "   M=0\n",
                "   @END_EQ\n",
                "   0;JMP\n",
                "(IS_EQ)\n",
                "   @{STACK_POINTER}\n",
                "   A=M\n",
                # -1 is the largest value in a 16-bit register so we use it to indicate true
                "   M=-1\n",
                "(END_EQ)\n",
            ])
        elif command.arg1 == ArithmeticCommand.GT:
            self.output_file.write("// gt\n")
        elif command.arg1 == ArithmeticCommand.LT:
            self.output_file.writelines([
                "// lt\n",
                # Get the value at the top of the stack
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "D=M\n",
                # Clear the value at the top of the stack
                "M=0\n",

            ])
        elif command.arg1 == ArithmeticCommand.AND:
            self.output_file.write("// and\n")
            self.output_file.writelines([
                "// or\n",
                # Get the value at the top of the stack
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "D=M\n",
                # Clear the value at the top of the stack
                "M=0\n",
                # Decrement the stack pointer and AND the stored value with the current value
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "M=D&M\n"
            ])
        elif command.arg1 == ArithmeticCommand.OR:
            self.output_file.writelines([
                "// or\n",
                # Get the value at the top of the stack
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "D=M\n",
                # Clear the value at the top of the stack
                "M=0\n",
                # Decrement the stack pointer and OR the stored value with the current value
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "M=D|M\n"
            ])
        elif command.arg1 == ArithmeticCommand.NOT:
            self.output_file.writelines([
                "// not\n",
                # Get the value at the top of the stack and negate it
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "M=!M\n"
            ])

    def write_push_pop(self, command: Command):
        if not command.arg1 or not command.arg2:
            raise ValueError("Invalid command")
        
        if command.type == CommandType.C_POP and command.arg1 == "constant":
            raise ValueError("Cannot pop constant")
        
        if command.arg1 == "constant":
            self.output_file.writelines([
                f"// push constant {command.arg2}\n",
                # Increment the stack pointer
                f"@{STACK_POINTER}\n",
                "M=M+1\n",
                # Store the value to the top of the stack
                f"@{command.arg2}\n",
                "D=A\n",
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "M=D\n",
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

        if command.type == CommandType.C_POP:
            self.output_file.writelines([
                f"// pop {command.arg1} {command.arg2}\n",
                # Calculate the selected address
                f"@{dest_segment}\n",
                "D=A\n",
                f"@{command.arg2}\n",
                "D=D+A\n",
                # Store the address in a temporary register
                "@R15\n",
                "M=D\n",
                # Take the value addressed by the stack pointer
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "D=M\n",
                # Store this value in the selected address
                "@R15\n",
                "A=M\n",
                "M=D\n",
                # Decrement the stack pointer
                f"@{STACK_POINTER}\n",
                "M=M-1\n"
            ])

    def close(self):
        self.output_file.close()

