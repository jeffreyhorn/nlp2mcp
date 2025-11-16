* range_with_macro.gms - Range with macro expansion test
* Tests: Set i / 1*%n% / (macro in range)

$set n 8

Sets
    i / 1*%n% /;

Scalars
    size;

size = card(i);

display size;
