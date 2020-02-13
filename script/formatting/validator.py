# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ======================================================
# GOAL : Warn about print statements and commented code
# ======================================================


import argparse
import os
import re
import functools

from formatter import LOG

# ==============================================
# LOGGING CONFIGURATION
# ==============================================

EXIT_SUCCESS = 0
EXIT_FAILURE = -1

VALIDATOR_PATTERNS = [ re.compile(patterns) for patterns in [
    r"print"
    ]
]

CODE_SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))
EVA_DIR = functools.reduce(os.path.join,
                           [CODE_SOURCE_DIR, os.path.pardir, os.path.pardir])

EVA_SRC_DIR = os.path.join(EVA_DIR, "src")
EVA_TEST_DIR = os.path.join(EVA_DIR, "test")
EVA_SCRIPT_DIR = os.path.join(EVA_DIR, "script")

DIRS = [EVA_SRC_DIR,EVA_TEST_DIR]

# ==============================================
# UTILITY FUNCTION DEFINITIONS
# ==============================================

def contains_commented_out_code(line):
    line = line.lstrip()
    
    if 'utf-8' in line:
        return False

    if not line.startswith('#'):
        return False

    line = line.lstrip(' \t\v\n#').strip()

    # Regex for checking function definition; for, with loops; 
    # continue and break
    regex_list = [
        r"def .+\)[\s]*[->]*[\s]*[a-zA-Z_]*[a-zA-Z0-9_]*:$",
        r"with .+ as [a-zA-Z_][a-zA-Z0-9_]*:$",
        r"for [a-zA-Z_][a-zA-Z0-9_]* in .+:$",
        r'continue$', r'break$'
    ]

    for regex in regex_list:
        if re.search(regex,line):
            return True

    symbol_list = list('[]{}=%') +\
        ['print', 'break', 
        'import ','elif ']


    for symbol in symbol_list:
        if symbol in line:
            return True

    #Handle return statements in a specific way
    if 'return' in line:
        if len(line.split(' ')) >= 2:
            return False
        else:
            return True
    return False


def validate_file(file):

    file = os.path.abspath(file)

    if not os.path.isfile(file):
        LOG.info ("ERROR: " + file + " isn't a file")
        sys.exit(EXIT_FAILURE)

    if not file.endswith('.py'):
        return True

    code_validation = True
    line_number = 1
    commented_code = False

    with open(file,'r') as opened_file:
        for line in opened_file:

            #Check if the line has commented code
            if line.lstrip().startswith('#'):
                commented_code = contains_commented_out_code(line)

                if commented_code:
                    LOG.info ("Commented code " \
                            +"in file "+file \
                            +" Line {}: {}".format(line_number,line.strip()))

            
            #Search for a pattern, and report hits
            for validator_pattern in VALIDATOR_PATTERNS:
                if validator_pattern.search(line):
                    code_validation = False
                    LOG.info ("Unacceptable pattern:"\
                            +validator_pattern.pattern.strip()\
                            +" in file "+file
                            +" Line {}: {}".format(line_number,line.strip()))

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
            
            status = validate_file(each_file)

            if not status:
                LOG.info ("WARNING: Code Validation fails for file:"+each_file)

    else:
        # Scanning entire source directory
        status = True
        status = validate_directory(DIRS)

        if not status:
            LOG.info ("WARNING: Code Validation fails!")


        
