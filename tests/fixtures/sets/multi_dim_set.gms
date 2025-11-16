* multi_dim_set.gms - Multi-dimensional set test
* Tests: Set pairs(i,j) - 2D set declaration

Sets
    i / 1*3 /
    j / 1*2 /
    pairs(i,j) / 1.1, 2.1, 3.2 /;

Scalars
    n_pairs;

n_pairs = card(pairs);

display n_pairs;
