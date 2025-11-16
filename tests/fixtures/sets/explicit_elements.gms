* explicit_elements.gms - Explicit set elements test
* Tests: Set i / i1, i2, i3 / (comma-separated elements)

Sets
    i / i1, i2, i3 /
    j / j1, j2 /;

Scalars
    ni, nj;

ni = card(i);
nj = card(j);

display ni, nj;
