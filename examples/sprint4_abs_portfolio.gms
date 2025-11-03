* Portfolio Optimization with abs() Smoothing Example
* Demonstrates: abs() function with smooth approximation
* Sprint 4 Feature: Smooth abs via sqrt(x^2 + epsilon)
* Note: Run with --smooth-abs flag

Sets
    i Assets /stock1*stock4, bond1*bond2/
;

Parameters
    expectedReturn(i) Expected returns (percent)
        /stock1 12, stock2 15, stock3 10, stock4 18
         bond1 5, bond2 6/

    targetWeight(i) Target portfolio weights
        /stock1 0.20, stock2 0.15, stock3 0.15, stock4 0.10
         bond1 0.25, bond2 0.15/
;

Variables
    w(i) Actual portfolio weights
    obj Objective value
    totalDeviation Total absolute deviation from targets
;

Positive Variables w;

Equations
    objective Minimize deviation from target weights
    budgetConstraint Sum of weights equals 1
    deviationCalc Calculate total absolute deviation
;

* Objective: minimize total absolute deviation from target weights
* Uses abs() which requires --smooth-abs flag
objective..
    obj =E= sum(i, abs(w(i) - targetWeight(i)));

* Budget constraint: weights sum to 1
budgetConstraint..
    sum(i, w(i)) =E= 1.0;

* Alternative: explicit deviation calculation (commented out)
* Could use: deviation(i) = w(i) - targetWeight(i)
* Then: obj = sum(i, abs(deviation(i)))
deviationCalc..
    totalDeviation =E= sum(i, abs(w(i) - targetWeight(i)));

* Initial values at target
w.l(i) = targetWeight(i);

* Bounds
w.lo(i) = 0;
w.up(i) = 0.5;

Model portfolio /all/;
Solve portfolio using NLP minimizing obj;

Display w.l, obj.l, totalDeviation.l;

* Expected output:
* - Weights close to target (within bounds)
* - Small objective value (small deviations)
* - Note: abs() smoothed to sqrt(x^2 + epsilon) with default epsilon=1e-6
