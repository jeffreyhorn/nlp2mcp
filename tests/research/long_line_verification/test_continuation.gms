$title Test GAMS Line Continuation Syntax
$ontext
This tests various line continuation strategies for GAMS equations.
We need to verify what works and what doesn't.
$offtext

Variables x1, x2, x3, x4, x5, x6, x7, x8, x9, x10;
Variables x11, x12, x13, x14, x15, x16, x17, x18, x19, x20;
Variable obj;

Equations
    objdef
    test_simple_break
    test_operator_break
    test_multi_line
    test_nested_break
    test_sum_break;

* Test 1: Simple line break after operator (most common)
test_simple_break..
    x1 =e=
        x2 + x3 + x4 +
        x5 + x6 + x7;

* Test 2: Break at various operators
test_operator_break..
    x1 =e=
        x2 + x3 *
        x4 - x5 /
        x6;

* Test 3: Multi-line with deep indentation
test_multi_line..
    x1 =e=
        x2 + x3 + x4 + x5 +
        x6 + x7 + x8 + x9 +
        x10 + x11 + x12 + x13 +
        x14 + x15 + x16 + x17;

* Test 4: Nested expressions with breaks
test_nested_break..
    x1 =e=
        (x2 + x3) *
        (x4 + x5) +
        (x6 + x7) *
        (x8 + x9);

* Test 5: Breaking with sum() calls
test_sum_break..
    obj =e=
        x1 + x2 +
        x3 + x4;

objdef.. obj =e= x1;

Model test / all /;
solve test using nlp minimizing obj;

display "All continuation syntax tests compiled successfully!";
