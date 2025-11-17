$onText
Fixture 04: Option Statement (Not Yet Supported)
Tests: option statement handling
Priority: High
Note: Option statements not yet supported, so they are commented out
$offText

* Option statements configure GAMS solver behavior
* Currently not supported by parser - this tests error handling
* Uncomment when option support is added:
* option limrow = 0;
* option limcol = 0;

Variables x;
Equations eq1;

eq1.. x =e= 5;

Model test /all/;
