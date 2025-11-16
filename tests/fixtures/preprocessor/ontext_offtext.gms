* ontext_offtext.gms - Text block comment test
* Tests: $onText/$offText directives (already supported)

Sets
    i / 1*4 /;

$onText
This is a multi-line comment block.
It can contain anything, including GAMS-like syntax:
    Variables x, y, z;
    Equations eq1, eq2;
None of this should be parsed.
$offText

Scalars
    count;

count = card(i);

display count;
