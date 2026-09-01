"""Classify positional-vs-declared-domain sites by whether a REPEATED symbol breaks them.

The discriminator is NOT "does it touch a domain positionally". zip()/enumerate()
over a domain pair position i with position i and survive repeats untouched.
What breaks is a SYMBOL -> (position|value) step: a repeated symbol collapses it.
"""
import ast, pathlib, collections, sys

ROOTS = ["src/kkt", "src/ad", "src/emit", "src/ir"]
DOMAINISH = ("domain", "indices", "index_names", "declared")

def txt(n):
    try: return ast.unparse(n)
    except Exception: return ""

def domainish(n):
    s = txt(n).lower()
    return any(k in s for k in DOMAINISH)

rows = []
for root in ROOTS:
    for path in sorted(pathlib.Path(root).rglob("*.py")):
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
        parents = {}
        for p in ast.walk(tree):
            for c in ast.iter_child_nodes(p):
                parents[c] = p
        def enclosing_func(n):
            while n in parents:
                n = parents[n]
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return n.name
            return "<module>"

        for node in ast.walk(tree):
            # --- K1: dict comprehension whose KEY is the loop var over a domain ---
            if isinstance(node, ast.DictComp):
                for gen in node.generators:
                    if domainish(gen.iter) and isinstance(gen.target, ast.Name) \
                       and txt(node.key) == gen.target.id:
                        rows.append((path, node.lineno, enclosing_func(node),
                                     "K1 symbol-keyed dictcomp", txt(node)[:90]))
            # --- K2: dict(zip(domain, ...)) ---
            if isinstance(node, ast.Call) and txt(node.func) == "dict":
                for a in node.args:
                    if isinstance(a, ast.Call) and txt(a.func) == "zip" and a.args and domainish(a.args[0]):
                        rows.append((path, node.lineno, enclosing_func(node),
                                     "K2 symbol-keyed dict(zip)", txt(node)[:90]))
            # --- K3: d[<loopvar over domain>] = ... inside a for over a domain ---
            if isinstance(node, ast.For) and domainish(node.iter) and isinstance(node.target, ast.Name):
                tv = node.target.id
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Assign):
                        for tgt in sub.targets:
                            if isinstance(tgt, ast.Subscript) and txt(tgt.slice) == tv:
                                rows.append((path, sub.lineno, enclosing_func(sub),
                                             "K3 symbol-keyed store in domain loop", txt(sub)[:90]))
            # --- K4: .index(x) on a domain -> ALWAYS the first position ---
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
               and node.func.attr == "index" and domainish(node.func.value):
                rows.append((path, node.lineno, enclosing_func(node),
                             "K4 .index() first-position", txt(node)[:90]))
            # --- K5: first-match scan: for p,s in enumerate(domain) with == test + early exit ---
            if isinstance(node, ast.For) and isinstance(node.iter, ast.Call) \
               and txt(node.iter.func) == "enumerate" and node.iter.args and domainish(node.iter.args[0]):
                body = list(ast.walk(node))
                has_eq = any(isinstance(b, ast.Compare) and any(isinstance(o, ast.Eq) for o in b.ops) for b in body)
                has_exit = any(isinstance(b, (ast.Break, ast.Return)) for b in body)
                if has_eq and has_exit:
                    rows.append((path, node.lineno, enclosing_func(node),
                                 "K5 first-match scan (== + early exit)", txt(node.iter)[:90]))
            # --- K6: `in` membership test against a domain (symbol -> bool, position lost) ---
            if isinstance(node, ast.Compare) and any(isinstance(o, ast.In) for o in node.ops):
                for c in node.comparators:
                    if domainish(c) and isinstance(node.left, (ast.Name, ast.Constant, ast.Attribute)):
                        rows.append((path, node.lineno, enclosing_func(node),
                                     "K6 membership test on domain", txt(node)[:90]))

seen = set(); out = []
for r in rows:
    k = (str(r[0]), r[1], r[3])
    if k in seen: continue
    seen.add(k); out.append(r)

by_kind = collections.Counter(r[3] for r in out)
print("=== AT-RISK SHAPES (a symbol -> position|value step) ===")
for k, n in by_kind.most_common(): print(f"  {n:4d}  {k}")
print(f"  {len(out):4d}  TOTAL\n")
by_file = collections.Counter(str(r[0]) for r in out)
for f, n in by_file.most_common(): print(f"  {n:4d}  {f}")
print()
for r in sorted(out, key=lambda r: (str(r[0]), r[1])):
    print(f"{r[0]}:{r[1]}  [{r[3]}]  {r[2]}()")
