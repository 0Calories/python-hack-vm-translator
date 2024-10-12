from enum import Enum

class CommandType(Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8

class ArithmeticCommand(Enum):
    ADD = "add"
    SUB = "sub"
    NEG = "neg"
    EQ = "eq"
    GT = "gt"
    LT = "lt"
    AND = "and"
    OR = "or"
    NOT = "not"

class MemoryAccessCommand(Enum):
    PUSH = "push"
    POP = "pop"

class Command:
    def __init__(self, unparsed_command: str):
        self.arg1 = None
        self.arg2 = None

        lexemes = unparsed_command.split(" ")

        if is_arithmetic_command(lexemes[0]):
            self.type = CommandType.C_ARITHMETIC
            self.arg1 = ArithmeticCommand(lexemes[0])

            if len(lexemes) > 1:
                raise ValueError(f"Invalid command: {unparsed_command}: Arithmetic commands should not have a second argument")
            
        elif is_memory_access_command(lexemes[0]):
            operation = MemoryAccessCommand(lexemes[0])
            if operation == MemoryAccessCommand.PUSH:
                self.type = CommandType.C_PUSH
            elif operation == MemoryAccessCommand.POP:
                self.type = CommandType.C_POP

            self.arg1 = lexemes[1]
            self.arg2 = lexemes[2]

            if len(lexemes) > 3:
                raise ValueError(f"Invalid command: {unparsed_command}: Memory access commands should only have two arguments")
        else:
            raise ValueError(f"Invalid command: {lexemes[0]}")        
        
    def __str__(self):
        return f"Command(type={self.type}, arg1={self.arg1}, arg2={self.arg2 if self.arg2 is not None else 'None'})"

class Parser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.current_command = None
        self.line_number = 0

        try:
            self.file = open(file_path, "r")
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        
    def advance(self):
        line = self.file.readline()

        if line == "":
            self.current_command = None
            return
        
        line = line.strip()
        
        if line.startswith("//"):
            self.advance()
            return
        
        self.line_number += 1
        
        # Handle inline comments
        line = line.split("//")[0].strip()
        
        self.current_command = Command(line)
        
    
    def has_more_commands(self):
        return self.current_command is not None or self.line_number == 0

def is_arithmetic_command(command: str) -> bool:
    try:
        ArithmeticCommand(command)
    except ValueError:
        return False
    return True

def is_memory_access_command(command: str) -> bool:
    try:
        MemoryAccessCommand(command)
    except ValueError:
        return False
    return True
