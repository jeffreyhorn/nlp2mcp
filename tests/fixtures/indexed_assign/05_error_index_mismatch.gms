$title Error Handling - Index Count Mismatch Test
$ontext
Purpose: Test validation of index count matching parameter domain
Pattern: p('i1') = 10; with p(i,j) domain
Expected: ParserSemanticError - index count mismatch
Sprint: 8 Day 4
$offtext

Set i /i1, i2/;
Set j /j1, j2/;
Parameter p(i, j);

p('i1') = 10;
