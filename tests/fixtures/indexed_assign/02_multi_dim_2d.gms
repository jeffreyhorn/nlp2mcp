$title Multi-Dimensional 2D Indexed Assignment Test
$ontext
Purpose: Test 2D parameter indexed assignment (mathopt1.gms pattern)
Pattern: report('global','x1') = 1.0;
Sprint: 8 Day 4
$offtext

Set scenario /global, solver/;
Set metric /x1, x2/;
Parameter report(scenario, metric);

report('global','x1') = 1.0;
report('global','x2') = 1.0;
report('solver','x1') = 0.95;
report('solver','x2') = 1.02;

display report;
