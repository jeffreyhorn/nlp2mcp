"""Parser utilities that turn the grammar output into ModelIR structures."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from functools import lru_cache
from itertools import product
from pathlib import Path

from lark import Lark, Token, Tree

from .ast import Binary, Call, Const, Expr, ParamRef, Sum, Unary, VarRef
from .model_ir import ModelIR, ObjectiveIR
from .symbols import (
    AliasDef,
    EquationDef,
    ObjSense,
    ParameterDef,
    Rel,
    SetDef,
    VariableDef,
    VarKind,
)


class ParserSemanticError(ValueError):
    """Raised when parsed input violates semantic assumptions."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        super().__init__(message)
        self.line = line
        self.column = column

    def __str__(self) -> str:
        base = super().__str__()
        if self.line is not None and self.column is not None:
            return f"{base} (line {self.line}, column {self.column})"
        if self.line is not None:
            return f"{base} (line {self.line})"
        return base


_ROOT = Path(__file__).resolve().parents[1]
_GRAMMAR_PATH = _ROOT / "gams" / "gams_grammer.lark"

_WRAPPER_NODES = {
    "sum_expr",
    "or_expr",
    "and_expr",
    "comp_expr",
    "arith_expr",
    "term",
    "factor",
    "power",
}

_REL_MAP = {
    "=e=": Rel.EQ,
    "=l=": Rel.LE,
    "=g=": Rel.GE,
}

_VAR_KIND_MAP = {
    "POSITIVE_K": VarKind.POSITIVE,
    "NEGATIVE_K": VarKind.NEGATIVE,
    "BINARY_K": VarKind.BINARY,
    "INTEGER_K": VarKind.INTEGER,
}

_FUNCTION_NAMES = {"abs", "exp", "log", "sqrt", "sin", "cos", "tan"}


@lru_cache
def _build_lark() -> Lark:
    """Load the shared Lark parser (cached for reuse across tests).

    Note: Using standard lexer (not dynamic_complete) to avoid tokenization issues
    where multi-character identifiers are split into individual characters.
    """
    return Lark.open(
        _GRAMMAR_PATH,
        parser="earley",
        start="start",
        maybe_placeholders=False,
        ambiguity="resolve",
    )


def _resolve_ambiguities(node: Tree | Token) -> Tree | Token:
    """Collapse Earley ambiguity nodes by picking the first alternative.

    With ambiguity="resolve" in the parser, ambiguity nodes are rare, but this
    function handles any that do appear by consistently picking the first alternative.
    This avoids exponential blowup in pathological grammar cases.
    """
    if isinstance(node, Token):
        return node

    if node.data == "_ambig":
        if not node.children:
            return node
        # Pick the first alternative to resolve ambiguity
        return _resolve_ambiguities(node.children[0])

    resolved_children = [_resolve_ambiguities(child) for child in node.children]
    return Tree(node.data, resolved_children)


def parse_text(source: str) -> Tree:
    """Parse a source string and return a disambiguated Lark parse tree."""
    parser = _build_lark()
    raw = parser.parse(source)
    return _resolve_ambiguities(raw)


def parse_file(path: str | Path) -> Tree:
    """Parse a GAMS source file and return the parse tree."""
    data = Path(path).read_text()
    return parse_text(data)


def parse_model_text(source: str) -> ModelIR:
    """Parse a source string into a populated ModelIR instance."""
    tree = parse_text(source)
    return _ModelBuilder().build(tree)


def parse_model_file(path: str | Path) -> ModelIR:
    """
    Parse a file path into a populated ModelIR instance.

    This function automatically handles $include directives by preprocessing
    the file before parsing.
    """
    from src.ir.preprocessor import preprocess_gams_file

    # Preprocess to expand all $include directives
    data = preprocess_gams_file(Path(path))
    return parse_model_text(data)


def _token_text(token: Token) -> str:
    value = str(token)
    if token.type == "STRING" and len(value) >= 2:
        return value[1:-1]
    return value


def _id_list(node: Tree) -> tuple[str, ...]:
    return tuple(_token_text(tok) for tok in node.children if isinstance(tok, Token))


@dataclass
class _ModelBuilder:
    """Walks the parse tree and instantiates ModelIR components."""

    model: ModelIR = field(default_factory=ModelIR)
    _equation_domains: dict[str, tuple[str, ...]] = None
    _context_stack: list[tuple[str, Tree | Token | None, tuple[str, ...]]] = field(
        default_factory=list
    )
    _declared_equations: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if self._equation_domains is None:
            self._equation_domains = {}

    def build(self, tree: Tree) -> ModelIR:
        for child in tree.children:
            if not isinstance(child, Tree):
                continue
            handler = getattr(self, f"_handle_{child.data}", None)
            if handler:
                handler(child)
        self._validate()
        return self.model

    def _handle_sets_block(self, node: Tree) -> None:
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            if child.data == "set_simple":
                name = _token_text(child.children[0])
                members = [
                    _token_text(tok) for tok in child.children[1].children if isinstance(tok, Token)
                ]
                self.model.add_set(SetDef(name=name, members=members))
            elif child.data == "set_empty":
                name = _token_text(child.children[0])
                self.model.add_set(SetDef(name=name))
            elif child.data == "set_domain":
                name = _token_text(child.children[0])
                domain = _id_list(child.children[1])
                self.model.add_set(SetDef(name=name, members=list(domain)))

    def _handle_aliases_block(self, node: Tree) -> None:
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            ids = [
                _token_text(tok)
                for tok in child.children
                if isinstance(tok, Token) and tok.type == "ID"
            ]
            if child.data == "alias_plain" and len(ids) == 2:
                alias_name, target = ids
                self._register_alias(alias_name, target, None, child)
            elif child.data == "alias_with_universe" and len(ids) == 3:
                alias_name, target, universe = ids
                self._register_alias(alias_name, target, universe, child)
            else:
                raise self._error("Unsupported alias declaration form", child)

    def _handle_params_block(self, node: Tree) -> None:
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            if child.data in {
                "param_domain",
                "param_domain_data",
                "param_plain",
                "param_plain_data",
            }:
                param = self._parse_param_decl(child)
                self.model.add_param(param)

    def _handle_variables_block(self, node: Tree) -> None:
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            if child.data in {"var_indexed", "var_scalar"}:
                kind, name, domain = self._parse_var_decl(child)
                self.model.add_var(VariableDef(name=name, domain=domain, kind=kind))

    def _handle_scalars_block(self, node: Tree) -> None:
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            name_token = child.children[0]
            name = _token_text(name_token)
            param = ParameterDef(name=name)

            if child.data == "scalar_with_data":
                # Format: ID "/" scalar_data_items "/" (ASSIGN expr)?
                # child.children[0] = ID
                # child.children[1] = scalar_data_items tree
                # child.children[2] = optional expr
                data_node = child.children[1]
                values = [
                    float(_token_text(tok))
                    for tok in data_node.scan_values(
                        lambda v: isinstance(v, Token) and v.type == "NUMBER"
                    )
                ]
                if values:
                    param.values[()] = values[-1]
                # Check for optional assignment after the data
                if len(child.children) > 2 and isinstance(child.children[2], Tree):
                    value_expr = self._expr_with_context(
                        child.children[2], f"scalar '{name}' assignment", ()
                    )
                    param.values[()] = self._extract_constant(
                        value_expr, f"scalar '{name}' assignment"
                    )
            elif child.data == "scalar_with_assign":
                # Format: ID ASSIGN expr
                value_expr = self._expr_with_context(
                    child.children[1], f"scalar '{name}' assignment", ()
                )
                param.values[()] = self._extract_constant(value_expr, f"scalar '{name}' assignment")
            # else: scalar_plain, just declare without value

            self.model.add_param(param)

    def _parse_var_decl(self, node: Tree) -> tuple[VarKind, str, tuple[str, ...]]:
        idx = 0
        kind = VarKind.CONTINUOUS
        if isinstance(node.children[idx], Token) and node.children[idx].type in _VAR_KIND_MAP:
            kind = _VAR_KIND_MAP[node.children[idx].type]
            idx += 1
        name = _token_text(node.children[idx])
        idx += 1
        domain: tuple[str, ...] = ()
        if idx < len(node.children) and isinstance(node.children[idx], Tree):
            domain = _id_list(node.children[idx])
        return kind, name, domain

    def _handle_equations_block(self, node: Tree) -> None:
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            if child.data == "eqn_head_scalar":
                name = _token_text(child.children[0])
                self._declared_equations.add(name)
                self._equation_domains[name] = ()
            elif child.data == "eqn_head_domain":
                name = _token_text(child.children[0])
                domain = _id_list(child.children[1])
                self._ensure_sets(domain, f"equation '{name}' domain", child)
                self._declared_equations.add(name)
                self._equation_domains[name] = domain

    def _handle_eqn_def_scalar(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        if name not in self._declared_equations:
            raise self._error(f"Equation '{name}' defined without declaration", node)
        lhs_node = node.children[1]
        rel_token = node.children[2]
        rhs_node = node.children[3]
        domain = self._equation_domains.get(name, ())
        relation = _REL_MAP[rel_token.value.lower()]
        lhs = self._expr_with_context(lhs_node, f"equation '{name}' LHS", domain)
        rhs = self._expr_with_context(rhs_node, f"equation '{name}' RHS", domain)
        equation = EquationDef(
            name=name,
            domain=domain,
            relation=relation,
            lhs_rhs=(lhs, rhs),
        )
        self.model.add_equation(equation)

    def _handle_eqn_def_domain(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        domain = _id_list(node.children[1])
        if name not in self._declared_equations:
            raise self._error(f"Equation '{name}' defined without declaration", node)
        self._ensure_sets(domain, f"equation '{name}' domain", node)
        lhs_node = node.children[2]
        rel_token = node.children[3]
        rhs_node = node.children[4]
        relation = _REL_MAP[rel_token.value.lower()]
        lhs = self._expr_with_context(lhs_node, f"equation '{name}' LHS", domain)
        rhs = self._expr_with_context(rhs_node, f"equation '{name}' RHS", domain)
        equation = EquationDef(
            name=name,
            domain=domain,
            relation=relation,
            lhs_rhs=(lhs, rhs),
        )
        self.model.add_equation(equation)

    def _handle_solve(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        self.model.model_name = name
        sense = ObjSense.MIN
        objvar = None
        idx = 1
        if (
            idx < len(node.children)
            and isinstance(node.children[idx], Tree)
            and node.children[idx].data == "obj_sense"
        ):
            sense_token = node.children[idx].children[0]
            sense = ObjSense.MIN if sense_token.type == "MINIMIZING_K" else ObjSense.MAX
            idx += 1
        if idx < len(node.children) and isinstance(node.children[idx], Token):
            objvar = _token_text(node.children[idx])
        if objvar:
            self.model.objective = ObjectiveIR(sense=sense, objvar=objvar)

    def _handle_model_all(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        if self.model.declared_model is None:
            self.model.declared_model = name
        self.model.model_equations = []
        self.model.model_uses_all = True

    def _handle_model_with_list(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        refs = [
            _token_text(tok)
            for tok in node.children[1].children
            if isinstance(tok, Token) and tok.type == "ID"
        ]
        if self.model.declared_model is None:
            self.model.declared_model = name
        self.model.model_equations = refs
        self.model.model_uses_all = False

    def _handle_model_decl(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        if self.model.declared_model is None:
            self.model.declared_model = name
        self.model.model_equations = []
        self.model.model_uses_all = False

    def _handle_assign(self, node: Tree) -> None:
        # Expected structure: lvalue, ASSIGN token, expression
        if len(node.children) < 3:
            raise self._error("Malformed assignment statement", node)
        lvalue_tree = node.children[0]
        expr_tree = next(
            (
                child
                for child in reversed(node.children)
                if isinstance(child, Tree) and child.data != "lvalue"
            ),
            None,
        )
        if expr_tree is None:
            raise self._error("Malformed assignment expression", node)
        if not isinstance(lvalue_tree, Tree) or lvalue_tree.data != "lvalue":
            raise self._error("Malformed assignment target", lvalue_tree)

        expr = self._expr_with_context(expr_tree, "assignment", ())
        value = self._extract_constant(expr, "assignment")

        target = next(
            (child for child in lvalue_tree.children if isinstance(child, (Tree, Token))),
            None,
        )
        if target is None:
            raise self._error("Empty assignment target", lvalue_tree)

        if isinstance(target, Tree):
            if target.data == "bound_indexed":
                var_name = _token_text(target.children[0])
                bound_token = target.children[1]
                indices = _id_list(target.children[2]) if len(target.children) > 2 else ()
                self._apply_variable_bound(var_name, bound_token, indices, value, target)
                return
            if target.data == "bound_scalar":
                var_name = _token_text(target.children[0])
                bound_token = target.children[1]
                self._apply_variable_bound(var_name, bound_token, (), value, target)
                return
            if target.data == "symbol_indexed":
                raise self._error("Indexed assignments are not supported yet", target)
        elif isinstance(target, Token):
            name = _token_text(target)
            if name in self.model.params:
                param = self.model.params[name]
                if param.domain:
                    raise self._error(
                        f"Assignment to parameter '{name}' requires indices for domain {param.domain}",
                        target,
                    )
                param.values[()] = value
                return
            if name in self.model.variables:
                var = self.model.variables[name]
                var.lo = var.up = var.fx = value
                return
        raise self._error("Unsupported assignment target", lvalue_tree)

    def _expr(self, node: Tree | Token, free_domain: tuple[str, ...]) -> Expr:
        if isinstance(node, Token):
            if node.type == "NUMBER":
                return self._attach_domain(Const(float(node)), free_domain)
            if node.type == "ID":
                name = _token_text(node)
                if name.lower() in {"inf", "+inf"}:
                    return self._attach_domain(Const(math.inf), free_domain)
                if name.lower() == "-inf":
                    return self._attach_domain(Const(-math.inf), free_domain)
                return self._make_symbol(name, (), free_domain, node)
            raise ValueError(f"Unexpected token in expression: {node!r}")

        if node.data in _WRAPPER_NODES:
            for child in node.children:
                if isinstance(child, (Tree, Token)):
                    if isinstance(child, Token) and child.type == "SEMI":
                        continue
                    return self._expr(child, free_domain)
            raise ValueError(f"Empty wrapper node: {node.data}")

        if node.data == "symbol_plain":
            name_token = node.children[0]
            name = _token_text(name_token)
            if name.lower() in {"inf", "+inf"}:
                return self._attach_domain(Const(math.inf), free_domain)
            if name.lower() == "-inf":
                return self._attach_domain(Const(-math.inf), free_domain)
            return self._make_symbol(name, (), free_domain, name_token)

        if node.data == "symbol_indexed":
            name = _token_text(node.children[0])
            indices_node = node.children[1]
            if name in self.model.variables or name in self.model.params:
                indices = _id_list(indices_node)
                return self._make_symbol(name, indices, free_domain, node)
            if name.lower() in _FUNCTION_NAMES:
                args: list[Expr] = []
                for child in indices_node.children:
                    if isinstance(child, Token):
                        args.append(self._make_symbol(_token_text(child), (), free_domain, child))
                    elif isinstance(child, Tree):
                        args.append(self._expr(child, free_domain))
                expr = Call(name.lower(), tuple(args))
                return self._attach_domain(expr, self._merge_domains(args, node))
            indices = _id_list(indices_node)
            return self._make_symbol(name, indices, free_domain, node)

        if node.data == "number":
            return self._attach_domain(Const(float(node.children[0])), free_domain)

        if node.data == "sum":
            indices = _id_list(node.children[1])
            self._ensure_sets(indices, "sum indices", node)
            remaining_domain = tuple(d for d in free_domain if d not in indices)
            body_domain = tuple(indices) + remaining_domain
            body = self._expr(node.children[2], body_domain)
            expr = Sum(indices, body)
            object.__setattr__(expr, "sum_indices", tuple(indices))
            return self._attach_domain(expr, remaining_domain)

        if node.data == "binop":
            left = self._expr(node.children[0], free_domain)
            op_token = node.children[1]
            right = self._expr(node.children[2], free_domain)
            expr = Binary(self._extract_operator(op_token), left, right)
            return self._attach_domain(expr, self._merge_domains([left, right], node))

        if node.data == "unaryop":
            op_token = node.children[0]
            operand = self._expr(node.children[1], free_domain)
            expr = Unary(self._extract_operator(op_token), operand)
            return self._attach_domain(expr, self._expr_domain(operand))

        if node.data == "funccall":
            func_tree = node.children[0]
            func_name = _token_text(func_tree.children[0]).lower()
            args: list[Expr] = []
            if len(func_tree.children) > 1:
                arg_list = func_tree.children[1]
                for child in arg_list.children:
                    if isinstance(child, (Tree, Token)):
                        args.append(self._expr(child, free_domain))
            expr = Call(func_name, tuple(args))
            return self._attach_domain(expr, self._merge_domains(args, node))

        raise ValueError(f"Unsupported expression node: {node.data}")

    def _expr_with_context(self, node: Tree | Token, context: str, domain: Sequence[str]) -> Expr:
        domain_tuple = tuple(domain)
        self._context_stack.append((context, node, domain_tuple))
        try:
            return self._expr(node, domain_tuple)
        finally:
            self._context_stack.pop()

    def _current_context(self) -> str:
        return self._current_context_description()

    def _current_context_description(self) -> str:
        if not self._context_stack:
            return "expression"
        return " -> ".join(desc for desc, _, _ in self._context_stack)

    def _error(self, message: str, node: Tree | Token | None = None) -> ParserSemanticError:
        context_desc = self._current_context_description()
        if context_desc:
            message = f"{message} [context: {context_desc}]"
        if self._context_stack:
            current_domain = self._context_stack[-1][2]
            if current_domain:
                message = f"{message} [domain: {current_domain}]"
        line, column = self._node_position(node)
        if line is None and self._context_stack:
            for _, ctx_node, _ in reversed(self._context_stack):
                line, column = self._node_position(ctx_node)
                if line is not None:
                    break
        return ParserSemanticError(message, line, column)

    def _node_position(self, node: Tree | Token | None) -> tuple[int | None, int | None]:
        if node is None:
            return (None, None)
        if isinstance(node, Token):
            return getattr(node, "line", None), getattr(node, "column", None)
        if isinstance(node, Tree):
            meta = getattr(node, "meta", None)
            if meta is not None:
                line = getattr(meta, "line", None)
                column = getattr(meta, "column", None)
                if line is not None:
                    return line, column
            for child in node.children:
                line, column = self._node_position(child)
                if line is not None:
                    return line, column
        return (None, None)

    def _make_symbol(
        self,
        name: str,
        indices: Sequence[str],
        free_domain: Sequence[str],
        node: Tree | Token | None = None,
    ) -> Expr:
        idx_tuple = tuple(indices)
        if name in self.model.variables:
            expected = self.model.variables[name].domain
            if len(expected) != len(idx_tuple):
                raise self._error(
                    f"Variable '{name}' expects {len(expected)} indices but received {len(idx_tuple)}",
                    node,
                )
            expr = VarRef(name, idx_tuple)
            object.__setattr__(expr, "symbol_domain", expected)
            object.__setattr__(expr, "index_values", idx_tuple)
            return self._attach_domain(expr, free_domain)
        if name in self.model.params:
            expected = self.model.params[name].domain
            if len(expected) != len(idx_tuple):
                raise self._error(
                    f"Parameter '{name}' expects {len(expected)} indices but received {len(idx_tuple)}",
                    node,
                )
            expr = ParamRef(name, idx_tuple)
            object.__setattr__(expr, "symbol_domain", expected)
            object.__setattr__(expr, "index_values", idx_tuple)
            return self._attach_domain(expr, free_domain)
        if idx_tuple:
            raise self._error(
                f"Undefined symbol '{name}' with indices {idx_tuple} referenced",
                node,
            )
        raise self._error(f"Undefined symbol '{name}' referenced", node)

    def _parse_param_decl(self, node: Tree) -> ParameterDef:
        name: str | None = None
        domain: tuple[str, ...] = ()
        data_node: Tree | None = None
        for child in node.children:
            if isinstance(child, Token):
                if child.type == "ID" and name is None:
                    name = _token_text(child)
            elif isinstance(child, Tree):
                if child.data == "id_list" and not domain:
                    domain = _id_list(child)
                elif child.data == "param_data_items":
                    data_node = child
        if name is None:
            raise self._error("Parameter declaration missing name", node)
        param = ParameterDef(name=name, domain=domain)
        if domain:
            self._ensure_sets(domain, f"parameter '{name}' domain", node)
        if data_node is not None:
            param.values.update(self._parse_param_data_items(data_node, domain, name))
        return param

    def _parse_param_data_items(
        self, node: Tree, domain: tuple[str, ...], param_name: str
    ) -> dict[tuple[str, ...], float]:
        if len(domain) > 1:
            raise self._error(
                f"Parameter '{param_name}' data for multi-dimensional domains is not supported",
                node,
            )
        values: dict[tuple[str, ...], float] = {}
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            if child.data == "param_data_scalar":
                key = self._parse_data_indices(child.children[0])
                value_token = child.children[-1]
                key_tuple: tuple[str, ...] = tuple(key) if domain else ()
                if len(key_tuple) != len(domain):
                    raise self._error(
                        f"Parameter '{param_name}' data index mismatch: expected {len(domain)} dims, got {len(key_tuple)}",
                        child,
                    )
                if domain:
                    for idx, set_name in zip(key_tuple, domain, strict=True):
                        self._verify_member_in_domain(param_name, set_name, idx, child)
                values[key_tuple] = float(_token_text(value_token))
            elif child.data == "param_data_matrix_row":
                row_indices = self._parse_data_indices(child.children[0])
                number_tokens = list(
                    child.scan_values(lambda v: isinstance(v, Token) and v.type == "NUMBER")
                )
                values_list = [float(_token_text(tok)) for tok in number_tokens]
                if len(domain) != len(row_indices) + 1:
                    raise self._error(
                        f"Parameter '{param_name}' table row index mismatch",
                        child,
                    )
                set_prefix = domain[:-1]
                if len(set_prefix) != len(row_indices):
                    raise self._error(
                        f"Parameter '{param_name}' table indices do not match domain",
                        child,
                    )
                for idx_symbol, set_name in zip(row_indices, set_prefix, strict=True):
                    self._verify_member_in_domain(param_name, set_name, idx_symbol, child)
                last_set = domain[-1]
                domain_set = self._resolve_set_def(last_set, node=child)
                if not domain_set or len(domain_set.members) < len(values_list):
                    raise self._error(
                        f"Parameter '{param_name}' table has more columns than members in set '{last_set}'",
                        child,
                    )
                for col_value, col_member in zip(values_list, domain_set.members, strict=True):
                    key_tuple = tuple(row_indices + [col_member])
                    values[key_tuple] = col_value
        return values

    def _parse_data_indices(self, node: Tree | Token) -> list[str]:
        if isinstance(node, Tree):
            return [
                _token_text(tok)
                for tok in node.children
                if isinstance(tok, Token) and tok.type == "ID"
            ]
        return [_token_text(node)]

    def _attach_domain(self, expr: Expr, domain: Sequence[str]) -> Expr:
        domain_tuple = tuple(domain)
        object.__setattr__(expr, "domain", domain_tuple)
        object.__setattr__(expr, "free_domain", domain_tuple)
        object.__setattr__(expr, "rank", len(domain_tuple))
        return expr

    def _expr_domain(self, expr: Expr) -> tuple[str, ...]:
        return getattr(expr, "domain", ())

    def _merge_domains(self, exprs: Sequence[Expr], node: Tree | Token) -> tuple[str, ...]:
        domains = [self._expr_domain(expr) for expr in exprs if expr is not None]
        if not domains:
            return ()
        first = domains[0]
        for d in domains[1:]:
            if d != first:
                raise self._error("Expression domain mismatch", node)
        return first

    def _extract_constant(self, expr: Expr, context: str) -> float:
        if isinstance(expr, Const):
            return float(expr.value)
        if isinstance(expr, Unary) and expr.op == "-" and isinstance(expr.child, Const):
            return -float(expr.child.value)
        if isinstance(expr, Unary) and expr.op == "+" and isinstance(expr.child, Const):
            return float(expr.child.value)
        raise self._error(f"Assignments must use numeric constants; got {expr!r} in {context}")

    def _apply_variable_bound(
        self,
        name: str,
        bound_token: Token | str,
        indices: Sequence[str],
        value: float,
        node: Tree | Token,
    ) -> None:
        if name not in self.model.variables:
            raise self._error(
                f"Bounds reference unknown variable '{name}'",
                node,
            )
        var = self.model.variables[name]
        idx_tuple = tuple(indices)
        bound_kind = (
            bound_token.lower()
            if isinstance(bound_token, str)
            else _token_text(bound_token).lower()
        )

        if var.domain:
            if not idx_tuple:
                raise self._error(
                    f"Variable '{name}' has indices {var.domain}; bounds must specify them",
                    node,
                )
            index_tuples = self._expand_variable_indices(var, idx_tuple, name, node)
        else:
            if idx_tuple:
                raise self._error(
                    f"Variable '{name}' is scalar; indexed bounds are not allowed",
                    node,
                )
            index_tuples = [()]

        for key in index_tuples:
            self._set_bound_value(var, name, key, value, bound_kind, node)

    def _set_bound_value(
        self,
        var: VariableDef,
        var_name: str,
        key: tuple[str, ...],
        value: float,
        bound_kind: str,
        node: Tree | Token | None = None,
    ) -> None:
        label_map = {"lo": "lower", "up": "upper", "fx": "fixed"}
        map_attrs = {"lo": "lo_map", "up": "up_map", "fx": "fx_map"}
        scalar_attrs = {"lo": "lo", "up": "up", "fx": "fx"}
        label = label_map.get(bound_kind, bound_kind)
        index_hint = f" at indices {key}" if key else ""

        if math.isinf(value):
            if bound_kind == "lo" and value < 0:
                return
            if bound_kind == "up" and value > 0:
                return
            if bound_kind == "fx":
                raise self._error(
                    f"Fixed bound for variable '{var_name}' cannot be infinite",
                    node,
                )
            # For other cases (e.g., lo = +inf), treat like regular value

        if bound_kind not in map_attrs:
            raise self._error(
                f"Unknown bound modifier '{bound_kind}' for variable '{var_name}'",
                node,
            )

        if key:
            storage = getattr(var, map_attrs[bound_kind])
            existing = storage.get(key)
            if existing is not None and existing != value:
                raise self._error(
                    f"Conflicting {label} bound for variable '{var_name}'{index_hint}",
                    node,
                )
            storage[key] = value
        else:
            scalar_attr = scalar_attrs[bound_kind]
            existing = getattr(var, scalar_attr)
            if existing is not None and existing != value:
                raise self._error(
                    f"Conflicting {label} bound for variable '{var_name}'",
                    node,
                )
            setattr(var, scalar_attr, value)

    def _extract_operator(self, node: Tree | Token) -> str:
        if isinstance(node, Token):
            return node.value
        if isinstance(node, Tree):
            if node.children:
                return self._extract_operator(node.children[0])
            data = node.data
            if isinstance(data, Token):
                return data.value
            if isinstance(data, str):
                return data
        raise self._error("Unable to determine operator token", node)

    def _register_alias(
        self,
        alias: str,
        target: str,
        universe: str | None,
        node: Tree | None = None,
    ) -> None:
        if alias in self.model.sets or alias in self.model.aliases:
            raise self._error(
                f"Alias '{alias}' duplicates an existing set or alias",
                node,
            )
        self._ensure_set_exists(target, f"alias '{alias}' target", node)
        if universe is not None:
            self._ensure_set_exists(universe, f"alias '{alias}' universe", node)
        self.model.add_alias(AliasDef(name=alias, target=target, universe=universe))

    def _ensure_set_exists(
        self,
        name: str,
        context: str,
        node: Tree | Token | None = None,
    ) -> None:
        if self._resolve_set_def(name, node=node) is None:
            raise self._error(
                f"Unknown set or alias '{name}' referenced in {context}",
                node,
            )

    def _ensure_sets(
        self,
        names: Sequence[str],
        context: str,
        node: Tree | Token | None = None,
    ) -> None:
        for name in names:
            self._ensure_set_exists(name, context, node)

    def _resolve_set_def(
        self,
        name: str,
        seen: set[str] | None = None,
        node: Tree | Token | None = None,
    ) -> SetDef | None:
        if name in self.model.sets:
            return self.model.sets[name]
        alias = self.model.aliases.get(name)
        if alias:
            if seen is None:
                seen = set()
            if name in seen:
                raise self._error(f"Alias cycle detected involving '{name}'", node)
            seen.add(name)
            return self._resolve_set_def(alias.target, seen, node)
        return None

    def _verify_member_in_domain(
        self,
        param_name: str,
        set_name: str,
        member: str,
        node: Tree | Token | None = None,
    ) -> None:
        set_def = self._resolve_set_def(set_name, node=node)
        if set_def is None:
            raise self._error(
                f"Unknown set '{set_name}' referenced in parameter '{param_name}' data",
                node,
            )
        if set_def.members and member not in set_def.members:
            raise self._error(
                f"Parameter '{param_name}' references member '{member}' not present in set '{set_name}'",
                node,
            )

    def _expand_variable_indices(
        self,
        var: VariableDef,
        index_symbols: Sequence[str],
        var_name: str,
        node: Tree | Token | None = None,
    ) -> list[tuple[str, ...]]:
        if len(index_symbols) != len(var.domain):
            raise self._error(
                f"Variable '{var_name}' bounds expect {len(var.domain)} indices but received {len(index_symbols)}",
                node,
            )
        member_lists: list[list[str]] = []
        for symbol, domain_name in zip(index_symbols, var.domain, strict=True):
            domain_set = self._resolve_set_def(domain_name, node=node)
            if domain_set is None:
                raise self._error(
                    f"Variable '{var_name}' references unknown domain set '{domain_name}'",
                    node,
                )
            resolved_symbol_set = self._resolve_set_def(symbol, node=node)
            if resolved_symbol_set is not None and domain_set is not None:
                if domain_set.members and resolved_symbol_set.members:
                    if set(resolved_symbol_set.members) - set(domain_set.members):
                        raise self._error(
                            f"Alias '{symbol}' for variable '{var_name}' does not match domain '{domain_name}'",
                            node,
                        )
            if not domain_set.members:
                raise self._error(
                    f"Cannot expand bounds for variable '{var_name}' because set '{domain_name}' has no explicit members",
                    node,
                )
            member_lists.append(domain_set.members)
        return [tuple(comb) for comb in product(*member_lists)]

    def _validate(self) -> None:
        for alias_name, alias in self.model.aliases.items():
            self._ensure_set_exists(alias.target, f"alias '{alias_name}' target")
            if alias.universe is not None:
                self._ensure_set_exists(alias.universe, f"alias '{alias_name}' universe")

        for param in self.model.params.values():
            self._ensure_sets(param.domain, f"parameter '{param.name}' domain")

        for var in self.model.variables.values():
            self._ensure_sets(var.domain, f"variable '{var.name}' domain")

        for equation in self.model.equations.values():
            self._ensure_sets(equation.domain, f"equation '{equation.name}' domain")

        if self.model.model_equations and not self.model.model_uses_all:
            for eq_name in self.model.model_equations:
                if eq_name not in self.model.equations:
                    raise self._error(f"Model references unknown equation '{eq_name}'")

        if self.model.model_name is not None:
            if self.model.declared_model is None:
                raise self._error(
                    f"Solve references model '{self.model.model_name}' which is not declared"
                )
            if self.model.model_name != self.model.declared_model:
                raise self._error(
                    f"Solve references model '{self.model.model_name}' but declared model is '{self.model.declared_model}'"
                )

        if self.model.objective is not None:
            objvar = self.model.objective.objvar
            if objvar not in self.model.variables:
                raise self._error(f"Objective references variable '{objvar}' which is not declared")
