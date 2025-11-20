# Day 7 Prompt: Conversion Pipeline - Part 1

**Branch:** Create a new branch named `sprint9-day7-conversion-pipeline-part1` from `sprint9-advanced-features`

**Objective:** Implement converter class scaffolding, implement IR → MCP GAMS mappings for variables, parameters, and equations.

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 837-886) - Day 7 summary
- Read `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 5) - Conversion pipeline architecture
- Read `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` (Unknowns 9.2.1-9.2.9) - Conversion unknowns
- Verify Checkpoint 3 passed: All parser features complete, parse rate ≥60%
- Review Task 5 architecture: IR → MCP GAMS transformation design

**Tasks to Complete (4-5 hours):**

1. **Implement Converter class scaffolding** (1 hour)
   - Create `src/converter/converter.py`
   - Implement base Converter class:
     ```python
     class Converter:
         """Converts ModelIR to MCP GAMS format."""
         
         def __init__(self, ir: ModelIR):
             self.ir = ir
             self.output = []
             self.errors = []
         
         def convert(self) -> ConversionResult:
             """Convert IR to MCP GAMS."""
             try:
                 self.convert_variables()
                 self.convert_parameters()
                 self.convert_equations()
                 return ConversionResult(
                     success=True,
                     output="\n".join(self.output),
                     errors=self.errors
                 )
             except ConversionError as e:
                 return ConversionResult(
                     success=False,
                     output=None,
                     errors=[str(e)] + self.errors
                 )
         
         def convert_variables(self):
             """Convert variable declarations."""
             pass  # Implement in step 2
         
         def convert_parameters(self):
             """Convert parameter declarations."""
             pass  # Implement in step 3
         
         def convert_equations(self):
             """Convert equation declarations."""
             pass  # Implement in step 4
     ```
   - Add ConversionResult dataclass
   - Add ConversionError exception class
   - Verify scaffolding with basic test

2. **Implement variable IR → MCP mappings** (1-1.5 hours)
   - Implement `convert_variables()` method
   - Map IR VariableDeclaration to MCP GAMS format:
     ```python
     def convert_variables(self):
         """Convert variable declarations to GAMS format."""
         for var in self.ir.variables:
             # Map variable type
             var_type = self.map_variable_type(var.type)
             
             # Map bounds if present
             bounds = self.map_variable_bounds(var)
             
             # Generate GAMS declaration
             gams_decl = f"{var_type} Variable {var.name}{bounds};"
             self.output.append(gams_decl)
     
     def map_variable_type(self, ir_type: str) -> str:
         """Map IR variable type to GAMS type."""
         type_map = {
             "free": "Free",
             "positive": "Positive",
             "negative": "Negative",
             "binary": "Binary",
             "integer": "Integer"
         }
         return type_map.get(ir_type, "Free")
     
     def map_variable_bounds(self, var: VariableDeclaration) -> str:
         """Map variable bounds to GAMS syntax."""
         if var.lower_bound and var.upper_bound:
             return f".lo = {var.lower_bound}; {var.name}.up = {var.upper_bound}"
         elif var.lower_bound:
             return f".lo = {var.lower_bound}"
         elif var.upper_bound:
             return f".up = {var.upper_bound}"
         return ""
     ```
   - Handle indexed variables (sets)
   - Test with mhw4d or rbrock variables

3. **Implement parameter IR → MCP mappings** (1-1.5 hours)
   - Implement `convert_parameters()` method
   - Map IR ParameterDeclaration to MCP GAMS:
     ```python
     def convert_parameters(self):
         """Convert parameter declarations to GAMS format."""
         for param in self.ir.parameters:
             # Handle scalar parameters
             if param.is_scalar:
                 gams_decl = f"Parameter {param.name} = {param.value};"
             # Handle indexed parameters
             else:
                 gams_decl = f"Parameter {param.name}({', '.join(param.indices)});"
                 if param.values:
                     # Generate assignment table
                     gams_decl += self.format_parameter_table(param)
             
             self.output.append(gams_decl)
     
     def format_parameter_table(self, param: ParameterDeclaration) -> str:
         """Format parameter value table."""
         table = [f"{param.name}({','.join(indices)}) = {value};" 
                  for indices, value in param.values.items()]
         return "\n".join(table)
     ```
   - Test with mhw4d or rbrock parameters

4. **Implement equation IR → MCP mappings** (1-2 hours)
   - Implement `convert_equations()` method
   - Map IR EquationDeclaration to MCP GAMS:
     ```python
     def convert_equations(self):
         """Convert equation declarations to GAMS format."""
         for eq in self.ir.equations:
             # Map equation type (=E=, =L=, =G=)
             eq_type = self.map_equation_type(eq.type)
             
             # Convert expression to GAMS syntax
             lhs = self.convert_expression(eq.lhs)
             rhs = self.convert_expression(eq.rhs)
             
             # Generate GAMS equation
             gams_eq = f"Equation {eq.name}; {eq.name}.. {lhs} {eq_type} {rhs};"
             self.output.append(gams_eq)
     
     def map_equation_type(self, ir_type: str) -> str:
         """Map IR equation type to GAMS operator."""
         type_map = {
             "eq": "=E=",
             "leq": "=L=",
             "geq": "=G="
         }
         return type_map.get(ir_type, "=E=")
     
     def convert_expression(self, expr: IRNode) -> str:
         """Convert IR expression to GAMS syntax."""
         if isinstance(expr, Const):
             return str(expr.value)
         elif isinstance(expr, VariableRef):
             return expr.name
         elif isinstance(expr, BinaryOp):
             left = self.convert_expression(expr.left)
             right = self.convert_expression(expr.right)
             return f"({left} {expr.op} {right})"
         # Add more expression types as needed
         else:
             raise ConversionError(f"Unsupported expression type: {type(expr)}")
     ```
   - Test with mhw4d or rbrock equations

5. **Write converter unit tests** (1 hour)
   - Create `tests/converter/test_converter.py`
   - Test cases:
     - `test_convert_variable()` - Variable conversion
     - `test_convert_parameter()` - Parameter conversion
     - `test_convert_equation()` - Equation conversion
     - `test_variable_bounds()` - Variable with bounds
     - `test_indexed_parameter()` - Multi-dimensional parameter
     - `test_expression_conversion()` - Complex expressions
     - `test_conversion_error_handling()` - Unsupported IR nodes
   - Target coverage: ≥80% for converter code

**Deliverables:**
- `src/converter/converter.py` - Converter class with scaffolding
- `src/converter/mappings.py` - IR → MCP GAMS mappings (if separated)
- Unit tests in `tests/converter/test_converter.py` (≥80% coverage)

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Converter class instantiates and accepts IR as input
- [ ] Variables convert to MCP GAMS format
- [ ] Parameters convert to MCP GAMS format
- [ ] Equations convert to MCP GAMS format
- [ ] Unit tests cover all IR node types
- [ ] All quality checks pass
- [ ] Mark Day 7 complete in PLAN.md
- [ ] Update README.md and CHANGELOG.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 9 Day 7: Conversion Pipeline - Part 1 (Infrastructure)" \
             --body "Completes Day 7 tasks from Sprint 9 PLAN.md

## Conversion Pipeline Infrastructure
- Converter class scaffolding complete
- Variable IR → MCP GAMS mappings
- Parameter IR → MCP GAMS mappings
- Equation IR → MCP GAMS mappings

## Tests
- XX unit tests with ≥80% coverage
- All mappings tested individually

Ready for Day 8 (end-to-end conversion validation)." \
             --base sprint9-advanced-features
```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 837-886)
- `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 5)
- Task 5 architecture design

**Notes:**
- Effort: 4-5h total
- Focus on infrastructure and mappings (not end-to-end yet)
- Day 8 will validate with actual model conversion
- Start with simplest models (mhw4d or rbrock)
