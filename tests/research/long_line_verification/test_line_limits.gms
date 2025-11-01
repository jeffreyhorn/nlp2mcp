$title Test GAMS Line Length Limits
$ontext
This test file empirically tests GAMS line length limits.
We create progressively longer lines to find the actual limit.
$offtext

Variables x1, x2, x3, x4, x5, x6, x7, x8, x9, x10;
Variables x11, x12, x13, x14, x15, x16, x17, x18, x19, x20;
Variables x21, x22, x23, x24, x25, x26, x27, x28, x29, x30;
Variables x31, x32, x33, x34, x35, x36, x37, x38, x39, x40;
Variables x41, x42, x43, x44, x45, x46, x47, x48, x49, x50;
Variable obj;

Equations objdef, test_80, test_120, test_255, test_500, test_1000;

* Test 1: 80 character line (typical coding standard)
test_80.. x1 =e= x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10 + x11 + x12;

* Test 2: 120 character line (common extended limit)
test_120.. x1 =e= x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10 + x11 + x12 + x13 + x14 + x15 + x16 + x17 + x18 + x19;

* Test 3: 255 character line (often cited as GAMS limit)
test_255.. x1 =e= x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10 + x11 + x12 + x13 + x14 + x15 + x16 + x17 + x18 + x19 + x20 + x21 + x22 + x23 + x24 + x25 + x26 + x27 + x28 + x29 + x30 + x31 + x32 + x33 + x34 + x35 + x36;

* Test 4: 500 character line (testing beyond 255)
test_500.. x1 =e= x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10 + x11 + x12 + x13 + x14 + x15 + x16 + x17 + x18 + x19 + x20 + x21 + x22 + x23 + x24 + x25 + x26 + x27 + x28 + x29 + x30 + x31 + x32 + x33 + x34 + x35 + x36 + x37 + x38 + x39 + x40 + x41 + x42 + x43 + x44 + x45 + x46 + x47 + x48 + x49 + x50 + x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10 + x11 + x12 + x13 + x14 + x15 + x16 + x17 + x18 + x19 + x20 + x21 + x22 + x23 + x24 + x25;

* Test 5: 1000 character line (extreme test)
test_1000.. x1 =e= x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10 + x11 + x12 + x13 + x14 + x15 + x16 + x17 + x18 + x19 + x20 + x21 + x22 + x23 + x24 + x25 + x26 + x27 + x28 + x29 + x30 + x31 + x32 + x33 + x34 + x35 + x36 + x37 + x38 + x39 + x40 + x41 + x42 + x43 + x44 + x45 + x46 + x47 + x48 + x49 + x50 + x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10 + x11 + x12 + x13 + x14 + x15 + x16 + x17 + x18 + x19 + x20 + x21 + x22 + x23 + x24 + x25 + x26 + x27 + x28 + x29 + x30 + x31 + x32 + x33 + x34 + x35 + x36 + x37 + x38 + x39 + x40 + x41 + x42 + x43 + x44 + x45 + x46 + x47 + x48 + x49 + x50 + x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10 + x11 + x12 + x13 + x14 + x15 + x16 + x17 + x18 + x19 + x20 + x21 + x22 + x23 + x24 + x25 + x26 + x27 + x28 + x29 + x30 + x31 + x32 + x33 + x34 + x35 + x36 + x37 + x38 + x39 + x40;

objdef.. obj =e= x1;

Model test / all /;
solve test using nlp minimizing obj;

display "All line length tests compiled successfully!";
