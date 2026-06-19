$title Shape 1 - single-axis offset Sum (general offset stationarity)
Set t /t1*t4/;
Alias(t,tt);
Parameter c(t); c(t) = 1;
Variable x(t), z;
Equation obj, link(t);
obj..     z =e= sum(t, c(t)*x(t));
link(t).. x(t) =g= sum(tt$(ord(tt) = ord(t)+1), x(tt)) - 1;
Model m /all/;
solve m using nlp minimizing z;
