
lexer grammar evaql_lexer;

channels { EVAQLCOMMENT, ERRORCHANNEL }

// SKIP

SPACE:                               [ \t\r\n]+    -> channel(HIDDEN);
SPEC_EVAQL_COMMENT:                  '/*!' .+? '*/' -> channel(EVAQLCOMMENT);
COMMENT_INPUT:                       '/*' .*? '*/' -> channel(HIDDEN);
LINE_COMMENT:                        (
                                       ('-- ' | '#') ~[\r\n]* ('\r'? '\n' | EOF) 
                                       | '--' ('\r'? '\n' | EOF) 
                                     ) -> channel(HIDDEN);

// Keywords
// Common Keywords

ALTER:                               'ALTER';
AND:                                 'AND';
AS:                                  'AS';
COLUMN:                              'COLUMN';
CREATE:                              'CREATE';
DATABASE:                            'DATABASE';
DELETE:                              'DELETE';
DESCRIBE:                            'DESCRIBE';
DISTINCT:                            'DISTINCT';
DROP:                                'DROP';
EXIT:                                'EXIT';
EXPLAIN:                             'EXPLAIN';
FALSE:                               'FALSE';
FROM:                                'FROM';
GROUP:                               'GROUP';
HAVING:                              'HAVING';
IN:                                  'IN';
INDEX:                               'INDEX';
INSERT:                              'INSERT';
JOIN:                                'JOIN';
KEY:                                 'KEY';
LIKE:                                'LIKE';
LIMIT:                               'LIMIT';
LOAD:                                'LOAD';
ON:                                  'ON';
OR:                                  'OR';
PRIMARY:                             'PRIMARY';
REFERENCES:                          'REFERENCES';
SELECT:                              'SELECT';
TABLE:                               'TABLE';
TRUE:                                'TRUE';
UNIQUE:                              'UNIQUE';
UNLOCK:                              'UNLOCK';
UNSIGNED:                            'UNSIGNED';
UPDATE:                              'UPDATE';
WHERE:                               'WHERE';

// EVAQL keywords

ERROR_BOUNDS:						 'ERROR_WITHIN';
CONFIDENCE_LEVEL:					 'AT_CONFIDENCE';

// ML models
BTREE:                               'BTREE';
HASH:                                'HASH';

// DATA TYPE Keywords

SMALLINT:                            'SMALLINT';
INTEGER:                             'INTEGER';
FLOAT:                               'FLOAT';
VARCHAR:                             'VARCHAR';

// Group function Keywords

AVG:                                 'AVG';
COUNT:                               'COUNT';
MAX:                                 'MAX';
MIN:                                 'MIN';
STD:                                 'STD';
SUM:                                 'SUM';
FCOUNT: 						     'FCOUNT';

// Keywords, but can be ID
// Common Keywords, but can be ID

AUTO_INCREMENT:                      'AUTO_INCREMENT';
BOOLEAN:                             'BOOLEAN';
BTREE:                               'BTREE';
COLUMNS:                             'COLUMNS';
HELP:                                'HELP';
TEMPTABLE:                           'TEMPTABLE';
VALUE:                               'VALUE';

// Common function names

ABS:                                 'ABS';

// Operators
// Operators. Assigns

VAR_ASSIGN:                          ':=';
PLUS_ASSIGN:                         '+=';
MINUS_ASSIGN:                        '-=';
MULT_ASSIGN:                         '*=';
DIV_ASSIGN:                          '/=';
MOD_ASSIGN:                          '%=';
AND_ASSIGN:                          '&=';
XOR_ASSIGN:                          '^=';
OR_ASSIGN:                           '|=';


// Operators. Arithmetics

STAR:                                '*';
DIVIDE:                              '/';
MODULE:                              '%';
PLUS:                                '+';
MINUSMINUS:                          '--';
MINUS:                               '-';
DIV:                                 'DIV';
MOD:                                 'MOD';


// Operators. Comparation

EQUAL_SYMBOL:                        '=';
GREATER_SYMBOL:                      '>';
LESS_SYMBOL:                         '<';
EXCLAMATION_SYMBOL:                  '!';


// Operators. Bit

BIT_NOT_OP:                          '~';
BIT_OR_OP:                           '|';
BIT_AND_OP:                          '&';
BIT_XOR_OP:                          '^';

// Constructors symbols

DOT:                                 '.';
LR_BRACKET:                          '(';
RR_BRACKET:                          ')';
COMMA:                               ',';
SEMI:                                ';';
AT_SIGN:                             '@';
ZERO_DECIMAL:                        '0';
ONE_DECIMAL:                         '1';
TWO_DECIMAL:                         '2';
SINGLE_QUOTE_SYMB:                   '\'';
DOUBLE_QUOTE_SYMB:                   '"';
REVERSE_QUOTE_SYMB:                  '`';
COLON_SYMB:                          ':';

// Literal Primitives


START_NATIONAL_STRING_LITERAL:       'N' SQUOTA_STRING;
STRING_LITERAL:                      DQUOTA_STRING | SQUOTA_STRING;
REAL_LITERAL:                        (DEC_DIGIT+)? '.' DEC_DIGIT+
                                     | DEC_DIGIT+ '.' EXPONENT_NUM_PART
                                     | (DEC_DIGIT+)? '.' (DEC_DIGIT+ EXPONENT_NUM_PART)
                                     | DEC_DIGIT+ EXPONENT_NUM_PART;
NULL_SPEC_LITERAL:                   '\\' 'N';



// Hack for dotID
// Prevent recognize string:         .123somelatin AS ((.123), FLOAT_LITERAL), ((somelatin), ID)
//  it must recoginze:               .123somelatin AS ((.), DOT), (123somelatin, ID)

DOT_ID:                              '.' ID_LITERAL;



// Identifiers

ID:                                  ID_LITERAL;
// DOUBLE_QUOTE_ID:                  '"' ~'"'+ '"';
REVERSE_QUOTE_ID:                    '`' ~'`'+ '`';
STRING_USER_NAME:                    (
                                       SQUOTA_STRING | DQUOTA_STRING 
                                       | BQUOTA_STRING | ID_LITERAL
                                     ) '@' 
                                     (
                                       SQUOTA_STRING | DQUOTA_STRING 
                                       | BQUOTA_STRING | ID_LITERAL
                                     );
LOCAL_ID:                            '@'
                                (
                                  [A-Z0-9._$]+ 
                                  | SQUOTA_STRING
                                  | DQUOTA_STRING
                                  | BQUOTA_STRING
                                );
GLOBAL_ID:                           '@' '@' 
                                (
                                  [A-Z0-9._$]+ 
                                  | BQUOTA_STRING
                                );

// Fragments for Literal primitives

fragment EXPONENT_NUM_PART:          'E' '-'? DEC_DIGIT+;
fragment ID_LITERAL:                 [A-Z_$0-9]*?[A-Z_$]+?[A-Z_$0-9]*;
fragment DQUOTA_STRING:              '"' ( '\\'. | '""' | ~('"'| '\\') )* '"';
fragment SQUOTA_STRING:              '\'' ('\\'. | '\'\'' | ~('\'' | '\\'))* '\'';
fragment BQUOTA_STRING:              '`' ( '\\'. | '``' | ~('`'|'\\'))* '`';
fragment DEC_DIGIT:                  [0-9];
fragment BIT_STRING_L:               'B' '\'' [01]+ '\'';

// Last tokens must generate Errors

ERROR_RECONGNIGION:                  .    -> channel(ERRORCHANNEL);
