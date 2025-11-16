* range_prefix.gms - Prefix range syntax test
* Tests: Set with custom prefix / p1*p100 /

Sets
    plants / p1*p100 /;

Scalars
    total_plants;

total_plants = card(plants);

display total_plants;
