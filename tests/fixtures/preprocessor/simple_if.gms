* simple_if.gms - Basic $if not set conditional
* Tests: Conditional variable definition

$if not set n $set n 10

Sets
    i / 1*%n% /;

Scalars
    count;

count = card(i);

display count;
