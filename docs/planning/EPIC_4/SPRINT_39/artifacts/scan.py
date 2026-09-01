"""AST scan for positional-vs-declared-domain resolution shapes.

Shapes that BREAK when a declared domain repeats a symbol:
  R1  dict keyed by domain element   {d: ... for d in domain} / dict(zip(domain, ...))
  R2  .index(sym) on a domain        -> always the FIRST position
  R3  first-match scan               for p, d in enumerate(domain): if d == x: ...
  R4  domain[pos] where pos came from R1/R2/R3
Shapes that are SAFE:
  S1  domain[pos] where pos is the loop counter over that same tuple (positional throughout)
  S2  len(domain) / iteration with no symbol->position step
"""
import ast, pathlib, sys, collections

ROOTS = ["src/kkt", "src/ad", "src/emit", "src/ir"]
DOMAINISH = ("domain", "domains", "indices", "index_names", "declared")

def is_domainish(node):
    """Textual test: does this expression name a declared domain/index tuple?"""
    try:
        s = ast.unparse(node)
    except Exception:
        return False
    low = s.lower()
    return any(k in low for k in DOMAINISH)

hits = collections.defaultdict(list)

for root in ROOTS:
    for path in sorted(pathlib.Path(root).rglob("*.py")):
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            # R1: dict comprehension keyed by an element of a domainish iterable
            if isinstance(node, ast.DictComp):
                for gen in node.generators:
                    if is_domainish(gen.iter):
                        hits["R1-dictcomp"].append((path, node.lineno))
            # R1: dict(zip(domain, ...)) — first arg of zip is the key sequence
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "dict":
                for a in node.args:
                    if isinstance(a, ast.Call) and isinstance(a.func, ast.Name) and a.func.id == "zip" \
                       and a.args and is_domainish(a.args[0]):
                        hits["R1-dictzip"].append((path, node.lineno))
            # R2: .index(...) on a domainish receiver
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
               and node.func.attr == "index" and is_domainish(node.func.value):
                hits["R2-index"].append((path, node.lineno))
            # R3: for <p>, <d> in enumerate(domainish) — positional scan
            if isinstance(node, ast.For) and isinstance(node.iter, ast.Call) \
               and isinstance(node.iter.func, ast.Name) and node.iter.func.id == "enumerate" \
               and node.iter.args and is_domainish(node.iter.args[0]):
                hits["R3-enumerate"].append((path, node.lineno))
            # R3b: zip(domainish, other) — positional pairing of a domain with something else
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "zip" \
               and node.args and any(is_domainish(a) for a in node.args):
                hits["R3b-zip"].append((path, node.lineno))
            # subscript on a domainish value
            if isinstance(node, ast.Subscript) and is_domainish(node.value):
                hits["SUB-domain[..]"].append((path, node.lineno))

for k in sorted(hits):
    per = collections.Counter(str(p) for p, _ in hits[k])
    print(f"\n### {k}: {len(hits[k])} hit(s)")
    for f, n in per.most_common():
        print(f"   {n:3d}  {f}")
