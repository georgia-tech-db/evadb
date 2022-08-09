#!/usr/bin/env bash

###############################################################
### ANTLR4
###############################################################

# Get Antlr4 JAR
wget --no-check-certificate https://www.antlr.org/download/antlr-4.10.1-complete.jar

# Generate grammar files
java -jar ./antlr-4.10.1-complete.jar -Dlanguage=Python3 eva/parser/evaql/evaql_lexer.g4
java -jar ./antlr-4.10.1-complete.jar -Dlanguage=Python3 -visitor eva/parser/evaql/evaql_parser.g4

# Cleanup Antlr4 JAR
rm ./antlr-4.10.1-complete.jar
