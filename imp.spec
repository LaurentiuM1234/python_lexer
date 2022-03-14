KEYWORDS begin | end | if | then | else | fi | while | do | od;
SPACES ' ' | '\t';
EXPR ([a-z]+ | -*[0-9]+)(' '*('+' | '*' | - | > | ==)' '*([a-z]+ | -*[0-9]+))*;
ASSIGN [a-z]+' '*=;
WHITESPACE '\n';
PAR '(' | ')';
