$title Nonlinear Regression Problem (LEAST,SEQ=24)

$onText
Nonlinear least squares estimation problem of Mitcherlisch's law.


Bracken, J, and McCormick, G P, Chapter 8.4. In Selected Applications of
Nonlinear Programming. John Wiley and Sons, New York, 1968, pp. 89-90.

Keywords: nonlinear programming, least square estimation, nonlinear regression,
          econometrics
$offText

Set i 'observation number' / 1*6 /;

Table dat(i,*) 'basic data'
         y      x
   1   127     -5
   2   151     -3
   3   379     -1
   4   421      5
   5   460      3
   6   426      1;

Variable
   ols     'ordinary least squares'
   dev(i)  'deviation'
   b1
   b2
   b3;

Equation
   dols    'definition of ols'
   ddev(i) 'definition of deviations'
   sequ    'single equation definition';

dols..    ols =e= sum(i, sqr(dev(i)));

ddev(i).. dat(i,"y") =e= b1 + b2*exp(b3*dat(i,"x")) + dev(i);

sequ..    ols =e= sum(i, sqr(dat(i,"y")-b1-b2*exp(b3*dat(i,"x"))));

Model
   least  'ordinary least squares' / dols, ddev /
   single 'single equ definition'  / sequ       /;

b1.l  = 500;
b2.l  = -150;
b3.lo = -5.0;
b3.l  = - .2;
b3.up =  5.0;

solve single minimizing ols using nlp;

solve least  minimizing ols using nlp;
