import argparse
import os
import re

EXIT_SUCCESS = 0
EXIT_FAILURE = -1

VALIDATOR_PATTERNS = [ re.compile(patterns) for patterns in [
    r"print"
    ]
]

CODE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
EVA_SRC_DIRECTORY = os.path.abspath(
                        os.path.join(os.path.abspath(CODE_DIRECTORY),os.pardir,os.pardir,"src")
                    )   

DIRS = [EVA_SRC_DIRECTORY]

def validate_file(file):

    if not os.path.isfile(file):
        print ("ERROR: " + file + " isn't a file")
        sys.exit(EXIT_FAILURE)

    if not file.endswith('.py'):
        return True

    code_validation = True
    line_number = 1

    with open(file,'r') as opened_file:
        for line in opened_file:
            
            #Search for a pattern, and report hits
            for validator_pattern in VALIDATOR_PATTERNS:
                if validator_pattern.search(line):
                    code_validation = False
                    print ("Unacceptable pattern:",validator_pattern.pattern.strip(),"in file",file,end=". ")
                    print ("Line {}: {}".format(line_number,line.strip()))

            line_number += 1

    return code_validation

def validate_directory(directory_list):

    code_validation = True

    for dir in directory_list:
        for dir_path, _, files in os.walk(dir):
            for each_file in files:

                file_path = dir_path + os.path.sep + each_file

                if not validate_file(file_path):
                    code_validation = False

    return code_validation

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(
        description="Perform source code validation on EVA."
    )

    PARSER.add_argument("--files",nargs="*",help="Provide a list of specific files to validate")

    ARGS = PARSER.parse_args()

    if ARGS.files:
        for each_file in ARGS.files:
            each_file = os.path.abspath(each_file.lower())
            print (each_file)
            
            status = validate_file(each_file)

            if not status:
                print ("WARNING: Code Validation fails for file:",each_file)

    else:
        # Scanning entire source directory
        status = validate_directory(DIRS)

        if not status:
            print ("WARNING: Code Validation fails!")


        
