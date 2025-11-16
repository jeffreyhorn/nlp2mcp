* simple_set.gms - Basic $set directive test
* Tests: Simple variable definition with $set

$set myvar 100

Sets
    i / 1*%myvar% /;

Scalars
    total;

total = card(i);

display total;
