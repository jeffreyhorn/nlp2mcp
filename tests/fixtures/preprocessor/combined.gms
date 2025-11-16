* combined.gms - Multiple preprocessor directives test
* Tests: Combination of $set, $if, %macro%, $eolCom

$eolCom !

$if not set n $set n 6
$set multiplier 2

Sets
    i / 1*%n% /;  ! Set with macro expansion

Scalars
    base / 10 /   ! Base value
    result;       ! Result holder

result = base * %multiplier%;  ! Calculation with macro

display result;  ! Should be 20
