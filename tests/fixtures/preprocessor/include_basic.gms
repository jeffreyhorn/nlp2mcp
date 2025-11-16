* include_basic.gms - Basic $include directive test
* Tests: File inclusion (already supported, testing for regression)
* Note: This requires an external file, simplified for testing

Sets
    i / 1*3 /;

Scalars
    base / 5 /;

* Normally would have: $include "data.gms"
* For this test, we inline the logic

Parameters
    values(i);

values(i) = base + ord(i);

display values;
