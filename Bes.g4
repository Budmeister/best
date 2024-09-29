grammar Bes;

file
    :   (importDecl | statement)* EOF
    ;

// Lexer rules

COMMENT
    :   '#' ~[\r\n]* -> skip
    ;

WS
    : [ \t\r\n]+ -> skip
    ;

IMPORT
    :   'IMPORT'
    ;

LET
    :   'let'
    ;

EXPR
    :   'expr'
    ;

MACRO
    :   'macro'
    ;

FN
    :   'fn'
    ;

IF
    :   'if'
    ;

IFL
    :   'ifl'
    ;

ELSE
    :   'else'
    ;



fragment ESCAPABLE_CHAR
    : '"' | '`'
    ;

fragment ESCAPED_CHAR
    :   '\\' ESCAPABLE_CHAR
    ;

FORMULA_LITERAL
    :   '"' (ESCAPED_CHAR | ~["\\])* '"'
    ;

STRING_LITERAL
    :   's"' (ESCAPED_CHAR | ~["\\])* '"'
    ;

DEFINED_EXPRESSION
    :   '`' IDENTIFIER '`'
    ;

IDENTIFIER
    :   [a-zA-Z0-9_\\] [a-zA-Z0-9_.]*
    ;

// Parser rules

importDecl
    :   'import' IDENTIFIER ';'
    ;

idList
    :   (IDENTIFIER (',' IDENTIFIER)*)?
    ;

functionStm
    :   FN IDENTIFIER '(' idList ')' blockExpr
    ;

letStm
    :   LET IDENTIFIER '=' expression ';'
    ;

exprStm
    :   EXPR IDENTIFIER '=' expression ';'
    ;

statement
    :   letStm
    |   exprStm
    |   functionStm
    ;

blockExpr
    :   '{' statement* expression '}'
    ;

ifExpr
    :   IF expression blockExpr ELSE blockExpr
    |   IF expression blockExpr ELSE ifExpr
    ;

iflExpr
    :   IFL expression blockExpr ELSE blockExpr
    |   IFL expression blockExpr ELSE ifExpr
    ;

expression
    :   blockExpr
    |   ifExpr
    |   iflExpr
    |   FORMULA_LITERAL
    |   STRING_LITERAL
    |   DEFINED_EXPRESSION
    |   IDENTIFIER
    |   '(' expression ')'
    ;
