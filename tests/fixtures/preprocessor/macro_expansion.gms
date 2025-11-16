* macro_expansion.gms - Macro variable expansion test
* Tests: %variable% substitution in various contexts

$set rows 3
$set cols 4
$set total 12

Sets
    i / 1*%rows% /
    j / 1*%cols% /;

Parameters
    A(i,j)
    sum;

A(i,j) = 1;
sum = %total%;

display sum;
