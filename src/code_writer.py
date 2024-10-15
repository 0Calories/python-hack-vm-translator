import os
from .parser import Command, CommandType, ArithmeticCommand 

MEMORY_SEGMENT_MAP = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
    # The following do not map to real memory segments but we include them for simplicity
    "temp": "TEMP",
    "pointer": "POINTER",
    "static": "STATIC",
}

STACK_POINTER = "SP"

TEMP_BASE_ADDRESS = 5

class CodeWriter:
    def __init__(self, output_file_path: str):
        if not output_file_path.endswith(".asm"):
            raise ValueError(f"Invalid file extension: {output_file_path}")

        self.output_file = open(output_file_path, "w")
        if not self.output_file:
            raise FileNotFoundError(f"Could not open output file: {output_file_path}")
        
        self.filename = os.path.basename(output_file_path).split(".")[0]

        # This counter is used to create unique labels for each arithmetic command
        self.label_counter = 0
        
    def write_command(self, command: Command):
        if command.type == CommandType.C_ARITHMETIC:
            self.write_arithmetic(command)
        elif command.type == CommandType.C_PUSH or command.type == CommandType.C_POP:
            self.write_push_pop(command)

    # This is extremely messy and should eventually be refactored
    # There are a lot of duplicate assembly lines that can be refactored into repeatable functions
    def write_arithmetic(self, command: Command):
        if command.arg1 == ArithmeticCommand.ADD:
            self.output_file.writelines([
                "// add\n",
                *self.pop_from_stack(),
                *self.point_to_top_of_stack(),
                "M=D+M\n",
                *self.increment_stack_pointer()
            ])
        elif command.arg1 == ArithmeticCommand.SUB:
            self.output_file.writelines([
                "// sub\n",
                *self.pop_from_stack(),
                *self.point_to_top_of_stack(),
                "M=M-D\n",
                *self.increment_stack_pointer()
            ])
        elif command.arg1 == ArithmeticCommand.NEG:
            self.output_file.writelines([
                "// neg\n",
                # Get the value at the top of the stack and make it negative
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "M=-M\n"
                # Increment the stack pointer
                f"@{STACK_POINTER}\n",
                "M=M+1\n",
            ])
        elif command.arg1 == ArithmeticCommand.EQ:
            self.output_file.writelines([
                "// eq\n",
                # Get the value at the top of the stack
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "D=M\n",
                # Clear the value at the top of the stack
                "M=0\n",
                # Decrement the stack pointer and subtract the stored value with the current value
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "D=M-D\n",
                # Jump logic to set the value at the top of the stack to 1 if the result is 0
                f"@IS_EQ_{self.label_counter}\n",
                "D;JEQ\n",
                f"(NOT_EQ_{self.label_counter})\n",
                f"   @{STACK_POINTER}\n",
                "   A=M\n",
                "   M=0\n",
                f"   @END_EQ_{self.label_counter}\n",
                "   0;JMP\n",
                f"(IS_EQ_{self.label_counter})\n",
                f"   @{STACK_POINTER}\n",
                "   A=M\n",
                # -1 is the largest value in a 16-bit register so we use it to indicate true
                "   M=-1\n",
                f"(END_EQ_{self.label_counter})\n",
                # Increment the stack pointer
                f"@{STACK_POINTER}\n",
                "M=M+1\n",
            ])

            # Increment the label counter so the next command that involves jumping will have a unique label
            self.label_counter += 1

        elif command.arg1 == ArithmeticCommand.GT:
            self.output_file.writelines([
                "// gt\n",
                # Get the value at the top of the stack
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "D=M\n",
                # Clear the value at the top of the stack
                "M=0\n",
                # Decrement the stack pointer and subtract the stored value with the current value
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "D=M-D\n",
                # Jump logic to set the value at the top of the stack to 1 if the result is 0
                f"@IS_GT_{self.label_counter}\n",
                "D;JGT\n",
                f"(NOT_GT_{self.label_counter})\n",
                f"   @{STACK_POINTER}\n",
                "   A=M\n",
                "   M=0\n",
                f"   @END_GT_{self.label_counter}\n",
                "   0;JMP\n",
                f"(IS_GT_{self.label_counter})\n",
                f"   @{STACK_POINTER}\n",
                "   A=M\n",
                # -1 is the largest value in a 16-bit register so we use it to indicate true
                "   M=-1\n",
                f"(END_GT_{self.label_counter})\n",
                # Increment the stack pointer
                f"@{STACK_POINTER}\n",
                "M=M+1\n",
            ])

            # Increment the label counter so the next command that involves jumping will have a unique label
            self.label_counter += 1

        elif command.arg1 == ArithmeticCommand.LT:
            self.output_file.writelines([
                "// lt\n",
                # Get the value at the top of the stack
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "D=M\n",
                # Clear the value at the top of the stack
                "M=0\n",
                # Decrement the stack pointer and subtract the stored value with the current value
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "D=M-D\n",
                # Jump logic to set the value at the top of the stack to 1 if the result is 0
                f"@IS_LT_{self.label_counter}\n",
                "D;JLT\n",
                f"(NOT_LT_{self.label_counter})\n",
                f"   @{STACK_POINTER}\n",
                "   A=M\n",
                "   M=0\n",
                f"   @END_LT_{self.label_counter}\n",
                "   0;JMP\n",
                f"(IS_LT_{self.label_counter})\n",
                f"   @{STACK_POINTER}\n",
                "   A=M\n",
                # -1 is the largest value in a 16-bit register so we use it to indicate true
                "   M=-1\n",
                f"(END_LT_{self.label_counter})\n",
                # Increment the stack pointer
                f"@{STACK_POINTER}\n",
                "M=M+1\n",
            ])

            # Increment the label counter so the next command that involves jumping will have a unique label
            self.label_counter += 1

        elif command.arg1 == ArithmeticCommand.AND:
            self.output_file.writelines([
                "// and\n",
                # Get the value at the top of the stack
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "D=M\n",
                # Clear the value at the top of the stack
                "M=0\n",
                # Decrement the stack pointer and AND the stored value with the current value
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "M=D&M\n",
                # Increment the stack pointer
                f"@{STACK_POINTER}\n",
                "M=M+1\n",
            ])
        elif command.arg1 == ArithmeticCommand.OR:
            self.output_file.writelines([
                "// or\n",
                # Get the value at the top of the stack
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "D=M\n",
                # Clear the value at the top of the stack
                "M=0\n",
                # Decrement the stack pointer and OR the stored value with the current value
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "M=D|M\n",
                # Increment the stack pointer
                f"@{STACK_POINTER}\n",
                "M=M+1\n",
            ])
        elif command.arg1 == ArithmeticCommand.NOT:
            self.output_file.writelines([
                "// not\n",
                # Get the value at the top of the stack and negate it
                f"@{STACK_POINTER}\n",
                "AM=M-1\n",
                "M=!M\n",
                # Increment the stack pointer
                f"@{STACK_POINTER}\n",
                "M=M+1\n",
            ])

    def write_push_pop(self, command: Command):
        if not command.arg1 or not command.arg2:
            raise ValueError("Invalid command")
        
        if command.type == CommandType.C_POP and command.arg1 == "constant":
            raise ValueError("Cannot pop constant")
        
        if command.arg1 == "constant":
            self.output_file.writelines([
                f"// push constant {command.arg2}\n",
                # Store the value to the top of the stack
                f"@{command.arg2}\n",
                "D=A\n",
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "M=D\n",
                # Increment the stack pointer
                f"@{STACK_POINTER}\n",
                "M=M+1\n",
            ])
            return
        
        if command.arg1 not in MEMORY_SEGMENT_MAP:
            raise ValueError(f"Invalid memory segment: {command.arg1}")

        # Handle static segment
        if command.arg1 == "static":
            dest_address = f"{self.filename}.{command.arg2}"

            if command.type == CommandType.C_PUSH:
                self.output_file.writelines([
                    f"// push static {command.arg2}\n",
                    f"@{dest_address}\n",
                    "D=M\n",
                    f"@{STACK_POINTER}\n",
                    "A=M\n",
                    "M=D\n",
                    f"@{STACK_POINTER}\n",
                    "M=M+1\n",
                ])
                return
            
            if command.type == CommandType.C_POP:
                self.output_file.writelines([
                    f"// pop static {command.arg2}\n",
                    # Set the address to the top of the stack
                    f"@{STACK_POINTER}\n",
                    "AM=M-1\n",
                    "D=M\n",
                    # Clear the value at the top of the stack
                    "M=0\n",
                    # Store the value in the given static register
                    f"@{dest_address}\n",
                    "M=D\n",
                ])
                return

        # Handle temp segment
        if command.arg1 == "temp":
            if int(command.arg2) > 7:
                raise ValueError(f"Temp register address out of bounds: {command.arg2}")
            
            dest_segment = f"R{TEMP_BASE_ADDRESS + int(command.arg2)}"

            if command.type == CommandType.C_PUSH:
                self.output_file.writelines([
                    f"// push temp {command.arg2}\n",
                    f"@{dest_segment}\n",
                    "D=M\n",
                    f"@{STACK_POINTER}\n",
                    "A=M\n",
                    "M=D\n",
                    f"@{STACK_POINTER}\n",
                    "M=M+1\n",
                ])
                return
            
            if command.type == CommandType.C_POP:
                self.output_file.writelines([
                    f"// pop temp {command.arg2}\n",
                    f"@{STACK_POINTER}\n",
                    "AM=M-1\n",
                    "D=M\n",
                    "M=0\n",
                    f"@{dest_segment}\n",
                    "M=D\n",
                ])
                return

        dest_segment = MEMORY_SEGMENT_MAP[command.arg1]


        # Handle pointer segment
        if command.arg1 == "pointer":
            if int(command.arg2) not in (0, 1):
                raise ValueError(f"Pointer values can only be 0 or 1")
            
            dest_segment = "THIS" if int(command.arg2) == 0 else "THAT"

            if command.type == CommandType.C_PUSH:
                self.output_file.writelines([
                    f"// push {command.arg1} {command.arg2}\n",
                    f"@{dest_segment}\n",
                    "D=M\n",
                    f"@{STACK_POINTER}\n",
                    "A=M\n",
                    "M=D\n",
                    f"@{STACK_POINTER}\n",
                    "M=M+1\n",
                ])
                return
            
            if command.type == CommandType.C_POP:
                self.output_file.writelines([
                    f"// pop {command.arg1} {command.arg2}\n",
                    # Set the address to the top of the stack
                    f"@{STACK_POINTER}\n",
                    "AM=M-1\n",
                    "D=M\n",
                    # Clear the value at the top of the stack
                    "M=0\n",
                    # Store the value in THIS or THAT
                    f"@{dest_segment}\n",
                    "M=D\n"
                ])
                return

        # Handle LOCAL, ARGUMENT, THIS, THAT
        if command.type == CommandType.C_PUSH:
            self.output_file.writelines([
                f"// push {command.arg1} {command.arg2}\n",
                # Take the address of the segment
                f"@{dest_segment}\n",
                "D=M\n",
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
                # Decrement the stack pointer
                f"@{STACK_POINTER}\n",
                "M=M-1\n"
                # Calculate the selected address
                f"@{dest_segment}\n",
                "D=M\n",
                f"@{command.arg2}\n",
                "D=D+A\n",
                # Store the address in a temporary register
                "@R15\n",
                "M=D\n",
                # Take the value addressed by the stack pointer
                f"@{STACK_POINTER}\n",
                "A=M\n",
                "D=M\n",
                # Clear the value from the stack
                "M=0\n",
                # Store this value in the selected address
                "@R15\n",
                "A=M\n",
                "M=D\n",
            ])

    def decrement_stack_pointer(self):
        """
        Helper function that returns the instructions to decrement the stack pointer.
        This simply decrements the value in the @SP register by 1 and does not store the result anywhere else.

        This will do the following:
            - `@SP`
            - `M=M-1`
        """
        return [
            f"@{STACK_POINTER}\n",
            "M=M-1\n"
        ]
    
    def increment_stack_pointer(self):
        """
        Helper function that returns the instructions to increment the stack pointer.
        This simply increments the value in the @SP register by 1 and does not store the result anywhere else.

        This will do the following:
            - `@SP`
            - `M=M+1`
        """
        return [
            f"@{STACK_POINTER}\n",
            "M=M+1\n"
        ]

    def point_to_top_of_stack(self):
        """
        Helper function that returns the instructions to point to the value stored at the top of the stack.
        This will decrement the value of the stack pointer and store it in the address register, since in this implementation,
        the stack pointer always points to the next available slot rather than the value at the top of the stack.

        This will do the following:
            - `@SP`
            - `AM=M-1`
        """
        return [
            f"@{STACK_POINTER}\n",
            "AM=M-1\n",
        ]
    
    def pop_from_stack(self):
        """
        Helper function that returns the instructions to pop the value at the top of the stack and store
        the result in the D register.

        This will do the following:
            - `@SP`
            - `AM=M-1`
            - `D=M`
            - `M=0`
        """
        return [
            f"@{STACK_POINTER}\n",
            "AM=M-1\n",
            "D=M\n",
            "M=0\n",
        ]
    

    def close(self):
        self.output_file.close()

