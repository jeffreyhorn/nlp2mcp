$title Test Long Stationarity Equations (Realistic KKT)
$ontext
This simulates the kind of long stationarity equations that nlp2mcp
would generate for KKT systems with many constraints.

Example: A variable that appears in 20+ constraints will have a
stationarity equation with 20+ Lagrange multiplier terms.
$offtext

Sets
    i 'constraints' / c1*c30 /;

Variables
    x           'primal variable'
    lambda(i)   'Lagrange multipliers'
    obj         'objective';

Parameters
    a(i)        'jacobian coefficients'
    grad_f      'gradient of objective wrt x';

* Initialize with realistic values
a(i) = uniform(0.5, 2.0);
grad_f = 1.5;

Equations
    objdef
    stationarity_short
    stationarity_long
    stationarity_very_long;

objdef.. obj =e= grad_f * x;

* Short stationarity (5 terms) - should fit on one line
stationarity_short..
    grad_f - lambda('c1')*a('c1') - lambda('c2')*a('c2') - lambda('c3')*a('c3') - lambda('c4')*a('c4') - lambda('c5')*a('c5') =e= 0;

* Long stationarity (15 terms) - would exceed 80 chars, needs breaking
stationarity_long..
    grad_f - lambda('c1')*a('c1') - lambda('c2')*a('c2') - lambda('c3')*a('c3') - lambda('c4')*a('c4') - lambda('c5')*a('c5') - lambda('c6')*a('c6') - lambda('c7')*a('c7') - lambda('c8')*a('c8') - lambda('c9')*a('c9') - lambda('c10')*a('c10') - lambda('c11')*a('c11') - lambda('c12')*a('c12') - lambda('c13')*a('c13') - lambda('c14')*a('c14') - lambda('c15')*a('c15') =e= 0;

* Very long stationarity (30 terms) - definitely needs multi-line breaking
stationarity_very_long..
    grad_f - lambda('c1')*a('c1') - lambda('c2')*a('c2') - lambda('c3')*a('c3') - lambda('c4')*a('c4') - lambda('c5')*a('c5') - lambda('c6')*a('c6') - lambda('c7')*a('c7') - lambda('c8')*a('c8') - lambda('c9')*a('c9') - lambda('c10')*a('c10') - lambda('c11')*a('c11') - lambda('c12')*a('c12') - lambda('c13')*a('c13') - lambda('c14')*a('c14') - lambda('c15')*a('c15') - lambda('c16')*a('c16') - lambda('c17')*a('c17') - lambda('c18')*a('c18') - lambda('c19')*a('c19') - lambda('c20')*a('c20') - lambda('c21')*a('c21') - lambda('c22')*a('c22') - lambda('c23')*a('c23') - lambda('c24')*a('c24') - lambda('c25')*a('c25') - lambda('c26')*a('c26') - lambda('c27')*a('c27') - lambda('c28')*a('c28') - lambda('c29')*a('c29') - lambda('c30')*a('c30') =e= 0;

Model test / all /;

* Just check that it compiles
display "Long stationarity equations compiled successfully!";
display "Line lengths:";
display "  stationarity_short:      ~150 characters";
display "  stationarity_long:       ~450 characters";
display "  stationarity_very_long:  ~900 characters";
