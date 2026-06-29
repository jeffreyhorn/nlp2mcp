$title Shape 7 - circular offset-alias objective cross-term (#1146 himmel16)

* himmel16's area is defined with the GAMS CIRCULAR lead `i++1` (wraps at the set
* boundary), and the objective sums the areas:
*   areadef(i).. area(i) =e= 0.5*(x(i)*y(i++1) - y(i)*x(i++1))
*   obj..        tot     =e= sum(i, area(i))
* x(i)/y(i) therefore appear at a circular +1 offset. The circular case routes
* through `_diff_varref(circular=True)` and is NOT handled by the (non-circular)
* successor representative-selection fix (#1143/#1447) — himmel16's `stat_area`
* residual (2.0) is the remaining #1146 work. This fixture is the catalog guard
* for that shape; the asserting test is xfail until the circular cross-term lands.

Set i /i1*i6/;
Alias(i,j);
Variable area(i), x(i), y(i), tot;

Equation areadef(i), obj;
areadef(i).. area(i) =e= 0.5*(x(i)*y(i++1) - y(i)*x(i++1));
obj..        tot     =e= sum(i, area(i));

Model m /all/;
solve m maximizing tot using nlp;
