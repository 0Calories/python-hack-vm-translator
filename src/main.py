import sys
from .parser import parser
from .code_writer import code_writer

def main():
    if len(sys.argv) != 2:
        print("Usage: hack-vm-translate <file>")
        sys.exit(1)

    input_file = sys.argv[1]
    print(f"Processing file: {input_file}")

    # TODO: Implement the main logic
    print(parser())
    print(code_writer())

if __name__ == "__main__":
    main()