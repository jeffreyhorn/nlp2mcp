# Large Model Test Fixtures

This directory contains test models for production hardening and performance testing.

## Models

### resource_allocation_small.gms
- **Size**: 10 variables
- **Purpose**: Baseline fast conversion test
- **Conversion time**: ~1.7 seconds
- **Structure**: Quadratic NLP with sum constraint

### resource_allocation_medium.gms
- **Size**: 50 variables  
- **Purpose**: Moderate scale testing
- **Conversion time**: ~1.5 seconds
- **Structure**: Quadratic NLP with sum constraint

### resource_allocation_large.gms
- **Size**: 100 variables
- **Purpose**: Stress testing within parser limits
- **Conversion time**: ~1.9 seconds
- **Structure**: Quadratic NLP with sum constraint

## Model Structure

All models follow this pattern:

```gams
* Quadratic resource allocation NLP
Sets
    i /i1, i2, ..., iN/
;

Parameters
    a(i) / ... /
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
nlp2mcp tests/fixtures/large_models/resource_allocation_medium.gms -o /tmp/out.gms
```

## Parser Limitations

The current GAMS parser has some limitations encountered during test fixture creation:

1. **Long comma-separated lists**: Lists with 100+ elements can cause timeouts (30+ seconds)
2. **Asterisk notation**: Set notation like `/i1*i100/` is not supported; must use explicit comma-separated lists
3. **Multi-dimensional parameters**: 2D parameter data like `usage(tasks, resources)` is not supported
4. **Positive Variables declaration**: The `Positive Variables` keyword is not supported; use constraints instead
5. **Equation description text**: Cannot contain hyphens (e.g., use "nonnegativity" not "non-negativity")

These models are designed to work within these limitations while still providing meaningful performance testing.
