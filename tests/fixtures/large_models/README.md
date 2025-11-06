# Large Model Test Fixtures

This directory contains test models for production hardening and performance testing.

## Models

### resource_allocation_250.gms
- **Size**: 250 variables
- **Input file**: 2.3K
- **Purpose**: Medium-scale model testing with asterisk notation
- **Structure**: Quadratic NLP with sum constraint
- **Performance**: ~5.1s conversion, ~50K MCP output

### resource_allocation_500.gms
- **Size**: 500 variables  
- **Input file**: 4.3K
- **Purpose**: Large-scale model testing with long parameter lists
- **Structure**: Quadratic NLP with sum constraint
- **Performance**: ~13.5s conversion, ~196K MCP output

### resource_allocation_1k.gms
- **Size**: 1,000 variables
- **Input file**: 8.3K
- **Purpose**: Stress testing with 1K variables and long comma-separated lists
- **Structure**: Quadratic NLP with sum constraint
- **Performance**: ~45.9s conversion, ~766K MCP output

## Model Structure

All models follow this pattern:

```gams
* Quadratic resource allocation NLP
Sets
    i /i1*iN/  ; Uses asterisk notation!
;

Parameters
    a(i) / i1 2, i2 3, ..., iN 1 /  ; Long comma-separated lists
;

Variables
    x(i) decision variables
    obj objective value
;

Equations
    objdef objective definition
    constraint1 sum constraint
    non_negative(i) nonnegativity constraints
;

objdef.. obj =e= sum(i, a(i)*x(i)*x(i));
constraint1.. sum(i, x(i)) =l= 100;
non_negative(i).. x(i) =g= 0;

Model resource_allocation /all/;
Solve resource_allocation using NLP minimizing obj;
```

## Usage

Generate all models:
```bash
python tests/fixtures/generate_large_models.py
```

Test conversion:
```bash
nlp2mcp tests/fixtures/large_models/resource_allocation_1k.gms -o /tmp/out.gms
```

## Performance Baselines

Performance metrics measured on MacBook Pro (Apple M2 Max, 32GB RAM):

| Model | Variables | Input Size | Conversion Time | Output Size | Throughput |
|-------|-----------|------------|-----------------|-------------|------------|
| 250   | 250       | 2.3K       | 5.1s           | 37K         | ~49 vars/s |
| 500   | 500       | 4.3K       | 13.5s          | 71K         | ~37 vars/s |
| 1K    | 1,000     | 8.3K       | 45.9s          | 139K        | ~22 vars/s |

**Performance scaling**: Roughly quadratic (O(n²)) as expected for:
- Jacobian computation (n variables × m constraints)
- KKT system assembly (n² potential gradient × constraint interactions)

**Memory usage**: All models complete within normal memory limits (<500MB peak)

## Solvability

All test fixtures are verified to solve correctly with GAMS:

- **Original NLP**: Solves with CONOPT (Model Status: Locally Optimal)
- **Generated MCP**: Solves with PATH (Model Status: Optimal)

This ensures the generated MCP formulations are mathematically correct and can be used for validation testing.

## Features Tested

These models leverage recently added parser features:

1. **Asterisk notation**: Set notation like `/i1*i1000/` for compact set definitions
2. **Long comma-separated lists**: Parameters with hundreds/thousands of values across long lines
3. **Large-scale models**: Testing parser and derivative computation at 250, 500, and 1K variable scales
