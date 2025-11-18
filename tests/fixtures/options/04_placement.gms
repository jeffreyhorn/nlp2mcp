* Fixture 4: Options Placement (Before and After Declarations)
* Tests option statements in different locations

* Option before any declarations
option limrow = 0;

Set i /1*3/;
Parameter p(i);

* Option after declarations
option decimals = 8;

Scalar x;
x = 100;

* Option after code
option limcol = 0;
