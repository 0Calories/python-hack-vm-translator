import sys
from .parser import dummy_parser_function
from .code_writer import dummy_code_writer_function

def main():
    if len(sys.argv) != 2:
        print("Usage: hack-vm-translate <file>")
        sys.exit(1)

    input_file = sys.argv[1]
    print(f"Processing file: {input_file}")

    # Call dummy functions
    print(dummy_parser_function())
    print(dummy_code_writer_function())

if __name__ == "__main__":
    main()