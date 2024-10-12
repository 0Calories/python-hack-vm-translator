import sys
from .parser import Parser
from .code_writer import CodeWriter

def main():
    if len(sys.argv) != 2:
        print("Usage: hack-vm-translate <file>")
        sys.exit(1)

    input_file = sys.argv[1]
    print(f"Processing file: {input_file}")

    parser = Parser(input_file)
    writer = CodeWriter(input_file.removesuffix(".vm") + ".asm")
    
    while parser.has_more_commands():
        writer.write_command(parser.current_command)
        parser.advance()

    writer.close()

if __name__ == "__main__":
    main()