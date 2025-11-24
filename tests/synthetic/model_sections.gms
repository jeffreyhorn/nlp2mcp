$title Synthetic Test: Model Declaration and Solve Statements
$onText
Synthetic Test for Model Sections

Purpose:
Validate that model declaration and solve statement syntax works in isolation.

Feature:
Model declaration creates a model object containing equations.
Solve statement invokes a solver on the model.

Expected Result:
PARSE SUCCESS

Pass Criteria:
- Parser succeeds without errors
- IR contains model declaration with equation list
- IR contains solve statement with model name and solver type

Fail Criteria:
- Parse error on Model or Solve keywords
- IR missing model or solve nodes
- Incorrect solver type or equation references

Minimal Example:
This test uses minimum: one variable, one equation, model declaration, solve.
No parameters, no complex equations - just the model section syntax.

Dependencies:
- Basic variable declaration
- Basic equation definition

Sprint:
9 (Implemented)

Reference:
- Sprint 9 implemented model sections
- Required for hs62.gms and other models
- This test validates isolated functionality

$offText

* ===== TEST CODE BELOW =====

Variable x;

Equation obj;

obj.. x =e= 0;

Model test /obj/;

Solve test using nlp minimizing x;

* ===== END TEST CODE =====

* Verification Notes:
* - Tests Model declaration with equation list
* - Tests Solve statement with using/minimizing clauses
* - If this passes, model sections work correctly
