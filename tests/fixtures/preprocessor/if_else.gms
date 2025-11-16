* if_else.gms - $if/$else branch test
* Tests: Conditional branching with $if/$else

$if set debug
$set level 10
$else
$set level 5
$endif

Sets
    i / 1*%level% /;

Scalars
    n;

n = card(i);

display n;
