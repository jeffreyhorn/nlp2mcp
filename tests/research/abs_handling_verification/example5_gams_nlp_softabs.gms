$title Simple NLP Example with Soft-Abs Approximation
$ontext
This example demonstrates solving an NLP in GAMS using the soft-abs
approximation for the absolute value function.

Problem: Minimize the sum of absolute values of deviations from targets
         min sum_i |x_i - target_i|
         subject to: sum_i x_i = total_constraint

This is a simple portfolio rebalancing or resource allocation problem.
$offtext

Sets
    i 'portfolio items' / item1*item5 /;

Parameters
    target(i) 'target values'
    / item1  10.0
      item2   5.0
      item3  15.0
      item4   8.0
      item5  12.0 /

    total_required 'total constraint' / 55.0 /;

Scalar epsilon 'smoothing parameter for soft-abs' / 1e-6 /;

Variables
    x(i)        'decision variables'
    total_dev   'total deviation (objective)';

Equations
    obj         'objective: minimize sum of absolute deviations'
    total_con   'constraint: sum must equal total_required';

* Soft-abs approximation: |x_i - target_i| ≈ sqrt((x_i - target_i)^2 + epsilon)
obj.. total_dev =e= sum(i, sqrt(sqr(x(i) - target(i)) + epsilon));

total_con.. sum(i, x(i)) =e= total_required;

* Initial values (start at targets)
x.l(i) = target(i);

* Bounds (allow reasonable deviations)
x.lo(i) = 0;
x.up(i) = 30;

Model portfolio / all /;

* Solve as NLP (GAMS will use default NLP solver)
* Common solvers: CONOPT, IPOPT, MINOS, SNOPT
solve portfolio using nlp minimizing total_dev;

* Display results
display x.l, total_dev.l;

* Calculate actual absolute deviations for comparison
Parameters
    actual_dev(i)   'actual |x_i - target_i|'
    soft_dev(i)     'soft-abs approximation'
    error(i)        'approximation error'
    sum_actual      'sum of actual absolute deviations'
    sum_soft        'sum of soft-abs values';

actual_dev(i) = abs(x.l(i) - target(i));
soft_dev(i) = sqrt(sqr(x.l(i) - target(i)) + epsilon);
error(i) = soft_dev(i) - actual_dev(i);
sum_actual = sum(i, actual_dev(i));
sum_soft = sum(i, soft_dev(i));

display "=== Solution Analysis ===";
display x.l, target;
display "=== Deviation Comparison ===";
display actual_dev, soft_dev, error;
display "=== Total Deviations ===";
display sum_actual, sum_soft;
display "=== Model Statistics ===";
display portfolio.modelstat, portfolio.solvestat;
