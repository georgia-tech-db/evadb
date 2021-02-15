#!/usr/bin/env bash

###############################################################
### ANTLR4
###############################################################

# Get Antlr4 JAR
# wget https://www.antlr.org/download/antlr-4.8-complete.jar
#export CLASSPATH="./antlr-4.8-complete.jar::$CLASSPATH"
#alias antlr4='java -jar ./antlr-4.8-complete.jar'

# Generate grammar files
java -jar ./antlr-4.8-complete.jar -Dlanguage=Python3 src/parser/evaql/evaql_lexer.g4
java -jar ./antlr-4.8-complete.jar -Dlanguage=Python3 -visitor src/parser/evaql/evaql_parser.g4

# Cleanup Antlr4 JAR
rm ./antlr-4.8-complete.jar
