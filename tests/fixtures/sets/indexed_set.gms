* indexed_set.gms - Indexed set (subset) test
* Tests: Set active(i) - subset declaration

Sets
    i / 1*5 /
    active(i) / 1, 3, 5 /;

Scalars
    n_total, n_active;

n_total = card(i);
n_active = card(active);

display n_total, n_active;
