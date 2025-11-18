$title Indexed Expressions on RHS Test
$ontext
Purpose: Test indexed parameter references in expressions (mathopt1.gms pattern)
Pattern: data('diff') = data('global') - data('solver');
Sprint: 8 Day 4
$offtext

Set metric /global, solver, diff/;
Parameter data(metric);

data('global') = 1.0;
data('solver') = 0.95;
data('diff') = data('global') - data('solver');

display data;
