* nested_if.gms - Nested conditional test
* Tests: Nested $if statements

$if not set mode $set mode 1

$if %mode% == 1
$set size 5
$if not set multiplier $set multiplier 2
$else
$set size 10
$set multiplier 1
$endif

Sets
    i / 1*%size% /;

Scalars
    result;

result = card(i) * %multiplier%;

display result;
