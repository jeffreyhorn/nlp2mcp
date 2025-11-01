$title Large NLP Model for Testing Long Lines
$ontext
Create an NLP with many constraints to generate long stationarity equations.
This will test what nlp2mcp actually generates for complex models.
$offtext

Sets
    i 'items' / i1*i20 /;

Parameters
    a(i) 'coefficients'
    b(i) 'bounds';

a(i) = uniform(1, 10);
b(i) = uniform(5, 15);

Variables
    x(i)    'decision variables'
    obj     'objective';

Equations
    objdef          'objective definition'
    constraint1(i)  'first set of constraints'
    constraint2(i)  'second set of constraints'
    constraint3(i)  'third set of constraints'
    constraint4(i)  'fourth set of constraints'
    constraint5(i)  'fifth set of constraints';

objdef.. obj =e= sum(i, a(i) * sqr(x(i)));

constraint1(i).. x(i) + sum(i, 0.1 * x(i)) =l= b(i);
constraint2(i).. x(i) - sum(i, 0.05 * x(i)) =g= 0;
constraint3(i).. sqr(x(i)) + sum(i, 0.01 * sqr(x(i))) =l= 100;
constraint4(i).. exp(x(i) / 10) =l= 5;
constraint5(i).. x(i) * sum(i, x(i)) =l= 50;

x.lo(i) = 0;
x.up(i) = 10;

Model test_model / all /;
solve test_model using nlp minimizing obj;
