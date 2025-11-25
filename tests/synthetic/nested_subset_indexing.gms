$title Nested/Subset Indexing Test Case
$onText
This is a minimal synthetic test case for verifying GAMS nested/subset
indexing support in nlp2mcp. It focuses exclusively on the subset domain
syntax in equation definitions.

Key features tested:
1. 2D subset declaration with parent set
2. Subset assignment with static condition (ord() function)
3. Equation definition with explicit subset indices: equation(subset(i,j))
4. Subset usage in equation body

Expected parsing behavior (Sprint 11 implementation):
- Parse rate: 100% (all lines should parse)
- AST: 1 EquationDef with SubsetDomain in domain list
- Semantic: 3 equation instances (for n=3: (p2,p1), (p3,p1), (p3,p2))
- IR: 3 concrete equations
- MCP: 3 equality constraints

This test case is derived from maxmin.gms (GAMSLib) but simplified to
isolate the nested/subset indexing feature.
$offText

* ============================================================================
* SET DECLARATIONS
* ============================================================================

Set n 'base set' / p1*p3 /;

Set low(n,n) 'lower triangle subset of n x n';

* ============================================================================
* ALIAS DECLARATIONS
* ============================================================================

Alias (n, nn);

* ============================================================================
* SUBSET ASSIGNMENT
* ============================================================================

* Static subset condition: evaluable at compile time
* For n={p1,p2,p3}, this generates 3 members:
*   low(p2,p1): ord(p2)=2 > ord(p1)=1 -> TRUE
*   low(p3,p1): ord(p3)=3 > ord(p1)=1 -> TRUE
*   low(p3,p2): ord(p3)=3 > ord(p2)=2 -> TRUE

low(n,nn) = ord(n) > ord(nn);

* Display subset members for verification
Display low;

* ============================================================================
* VARIABLE DECLARATIONS
* ============================================================================

Variable
   dist(n,n)  'distance between points n and nn';

* ============================================================================
* EQUATION DECLARATIONS
* ============================================================================

Equation
   defdist(low(n,nn))  'distance definition for lower triangle only';

* ============================================================================
* EQUATION DEFINITIONS
* ============================================================================

* PRIMARY TEST CASE: Equation with explicit subset indices
* This is the core syntax that requires nested/subset indexing support.
* The equation domain uses low(n,nn), which is a SubsetDomain node in AST.
*
* Expected behavior:
*   - Parser: Recognize low(n,nn) as domain_element -> subset_domain
*   - AST: SubsetDomain(subset_name='low', indices=['n', 'nn'])
*   - Semantic: Expand to 3 instances based on low membership
*   - IR: Generate 3 concrete equations:
*       defdist[p2,p1].. dist(p2,p1) =e= 1;
*       defdist[p3,p1].. dist(p3,p1) =e= 1;
*       defdist[p3,p2].. dist(p3,p2) =e= 1;

defdist(low(n,nn)).. dist(n,nn) =e= 1;

* ============================================================================
* MODEL DEFINITION
* ============================================================================

Model test /all/;

* ============================================================================
* SOLVE STATEMENT
* ============================================================================

* Note: Solve statement is not yet supported in nlp2mcp
* This is a placeholder for future Sprint work

* solve test using nlp minimizing dist;

* ============================================================================
* END OF FILE
* ============================================================================

* Expected output (when fully implemented):
*   Parse rate: 100%
*   Equations parsed: 1 (defdist)
*   Equation instances: 3 (one for each low member)
*   Variables: 9 (dist(n,nn) for all n x nn pairs)
*   Constraints: 3 (one per equation instance)
