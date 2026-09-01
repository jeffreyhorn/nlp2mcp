import os as _os
OUT = _os.environ.get("OUT", "/tmp/s39t7")
_os.makedirs(OUT, exist_ok=True)
import json
reach=json.load(open(f"{OUT}/reach.json"))
N=len(reach)
REACH_LABEL = {'src/ad/constraint_jacobian.py:1466': 'K4 _sub_idx', 'src/ad/constraint_jacobian.py:1474': 'K4 _sub_idx IndexOffset', 'src/ad/constraint_jacobian.py:1513': 'K4 _substitute_indices Sum/Prod', 'src/ad/constraint_jacobian.py:1536': 'K4 _substitute_indices SymbolRef', 'src/ad/derivative_rules.py:2362': 'K5 _diff_sum wrt scan', 'src/ad/derivative_rules.py:2411': 'K5 _diff_sum duplicate_sym guard', 'src/emit/emit_gams.py:795': 'K5 _visit domain scan', 'src/ir/condition_eval.py:52': 'K4 star-domain split', 'src/ir/condition_eval.py:117': 'K2 dict(zip(domain_sets,...))', 'src/ir/parser.py:5530': 'K5 param.domain[pos] alias expand', 'src/ir/parser.py:6007': 'K5 multidim set alias substitution', 'src/ir/parser.py:6086': 'K4 expanded_indices.index()', 'src/kkt/empty_equation_detector.py:127': 'K2 dict(zip(eq_def.domain,...))', 'src/kkt/stationarity.py:1091': 'K5 _pos first-match', 'src/kkt/stationarity.py:1104': 'K3 bindings[eqi]=p', 'src/kkt/stationarity.py:1500': 'K5 _remap_condition_to_domain (#1350)', 'src/kkt/stationarity.py:3432': 'K5 _apply_alias_offset_to_deriv', 'src/kkt/stationarity.py:4880': 'K5 _match_subset_domain', 'src/kkt/stationarity.py:5140': 'K3 _compute_index_offset_key p1', 'src/kkt/stationarity.py:5148': 'K3 _compute_index_offset_key p2', 'src/kkt/stationarity.py:5770': 'K5 _sigma_sp_domain_collision'}
cnt={}
for v in reach.values():
    for s in v["sites"]: cnt[s]=cnt.get(s,0)+1
def R(fileline):
    lab = REACH_LABEL[fileline]   # KeyError = a site that does not join
    return cnt.get(lab, 0)

# (file:line, label, shape, verdict, argument)
SITES=[
("src/ad/constraint_jacobian.py:1466","K4 _sub_idx","`symbolic_indices.index(idx)`","NEEDS A TEST",
 "Highest-reach site in the sample. `.index()` returns the FIRST position, so a repeated `symbolic_indices` substitutes every occurrence to `concrete_indices[0]` — `slp(n1,n2)` would emit as `slp(n1,n1)`. Safe **today** only because `dedupe_repeated_variable_domains` (Issue #1062) rewrites repeated VARIABLE domains before differentiation. That pass covers variables only, so the protection is upstream and incidental, not local."),
("src/ad/constraint_jacobian.py:1474","K4 _sub_idx IndexOffset","`symbolic_indices.index(idx.base)`","NEEDS A TEST",
 "Same mechanism on the `IndexOffset` base (#1045). Same upstream-only protection."),
("src/ad/constraint_jacobian.py:1513","K4 _substitute_indices Sum/Prod","`symbolic_indices.index(idx)` in a comprehension","NEEDS A TEST",
 "Builds `free_concrete` by `.index()` per free symbol; a repeat silently maps both to the first concrete value. Same upstream-only protection."),
("src/ad/constraint_jacobian.py:1536","K4 _substitute_indices SymbolRef","`symbolic_indices.index(expr.name)`","NEEDS A TEST",
 "Bare `SymbolRef` substitution (#730). Same shape."),
("src/ir/condition_eval.py:117","K2 dict(zip(domain_sets, index_values))","symbol-keyed map","NEEDS A GUARD",
 "`strict=True` catches a LENGTH mismatch but not a KEY collapse: `zip(('i','i'), ('i1','i2'))` yields `{'i': 'i2'}`, silently discarding the first position. This is elec's mechanism in a second layer, and nothing upstream de-duplicates a SET or PARAM domain. Reached by 9 of 15 sampled models."),
("src/kkt/empty_equation_detector.py:127","K2 dict(zip(eq_def.domain, inst))","symbol-keyed map","NEEDS A GUARD",
 "Identical collapse on an EQUATION domain. Two defects meet here: the map collapses, and `_enumerate_domain_instances` yields the full product for a domain a GAMS equation definition would bind diagonally. Reached by 10 of 15."),
("src/ir/parser.py:6086","K4 expanded_indices.index(child_idxs[0])","first position","NEEDS A TEST",
 "Anchors a multidim set condition at the first match, then checks contiguity. A repeated symbol can anchor the window at the wrong start. Partly mitigated by the alias substitution 80 lines above (site 6007)."),
("src/ir/condition_eval.py:52","K4 list(domain).index('*')","first position","NEEDS A TEST",
 "Searches for the `*` sentinel, not a set symbol. `p(*,*)` is expressible; the `star_pos >= 2` test happens to reject it, but `p(i,*,j,*)` is not covered by that argument. Reached by 1 of 15."),
("src/kkt/stationarity.py:1091","K5 _pos first-match over `src_indices`","first position","NEEDS A GUARD",
 "`_pos` returns the first position of a symbol in a VarRef's index tuple; `bindings` is then keyed by equation index and `var_domain[binding_position]` resolved positionally. With a repeated tuple the binding position is always the first occurrence. The `len(bindings) != 1` bail-out rejects the multi-index case but not the single-index one."),
("src/kkt/stationarity.py:1104","K3 bindings[eqi] = p","symbol-keyed store","NEEDS A GUARD",
 "Same site, the storing half. Included separately because a guard could live at either end."),
("src/kkt/stationarity.py:1500","K5 _remap_condition_to_domain","`set_declared_domain[pos]` + `_claim`","ALREADY GUARDED",
 "The #1350 consume-once fix: `used_slots` prevents two positions claiming the same variable-domain slot. This is one of the two known instances and is the survey's positive control for the 'guarded' verdict."),
("src/kkt/stationarity.py:3432","K5 _apply_alias_offset_to_deriv","`declared_domain[pi]` against a PARAM domain","NEEDS A TEST",
 "Positional throughout (pi -> pi), so no symbol->position step. But `offset_map` is symbol-keyed, so a param declared `rail(i,i)` (ferts) receives the SAME offset at both positions. Whether that is right depends on the intent, which the code cannot see. Reached by 1 of 15."),
("src/kkt/stationarity.py:4880","K5 _match_subset_domain","`used_var_positions`","ALREADY GUARDED",
 "Consume-once over variable-domain positions. Reached by 10 of 15 — the most-reached guarded site."),
("src/kkt/stationarity.py:5140","K3 _compute_index_offset_key pass 1","`used_var` consume-once","ALREADY GUARDED",
 "Exact canonical match with `used_var` preventing double-claim."),
("src/kkt/stationarity.py:5148","K3 _compute_index_offset_key pass 2","`used_var` consume-once","ALREADY GUARDED",
 "Common-root fallback, same `used_var` set."),
("src/kkt/stationarity.py:5770","K5 _sigma_sp_domain_collision","purpose-built repeated-domain detector","ALREADY GUARDED",
 "Exists FOR this class: requires >= 2 var-domain positions canonicalising to the same set. Its own docstring records 15 of 142 models reaching conjunct 1. Reached by 1 of 15 here."),
("src/ad/derivative_rules.py:2362","K5 _diff_sum wrt scan","`enumerate(wrt_indices)` + concrete test","ALREADY GUARDED",
 "Feeds the duplicate check below. Reached by 10 of 15."),
("src/ad/derivative_rules.py:2411","K5 _diff_sum duplicate_sym","explicit `seen_sym` duplicate bail-out","ALREADY GUARDED",
 "The comment names this class exactly: 'duplicates would overwrite earlier entries'. A third independent guard, in the AD layer. Reached by 10 of 15."),
("src/ir/parser.py:5530","K5 param.domain[pos] alias expansion","alias expansion","ALREADY GUARDED",
 "Its own comment cites 'tfp is an alias for tf and domain is (tf,tf)' — the parser already alias-expands a repeated PARAM domain on this path."),
("src/ir/parser.py:6007","K5 multidim set alias substitution","`seen_domain` + minted alias","ALREADY GUARDED",
 "Mints an alias for the second occurrence, 'e.g. a(n,n) -> (n,np)'. The same remedy as Issue #1062, applied at the parser for SET domains — but only on this branch."),
("src/emit/emit_gams.py:795","K5 _visit domain scan","`enumerate(domain)` + name match","NOT REACHABLE (in sample)",
 "0 of 15 sampled models executed this line, including both known instances and all five emit-level offenders. NOT a proof of unreachability — it is a measured absence over a 15-model sample chosen to be adversarial for this class, and it is recorded as such."),
]
order={"NEEDS A GUARD":0,"NEEDS A TEST":1,"ALREADY GUARDED":2,"NOT REACHABLE (in sample)":3}
rows=sorted(SITES,key=lambda r:(order[r[3]],-R(r[0])))
import collections
print(f"TOTAL SITES: {len(SITES)}")
print(collections.Counter(r[3] for r in SITES))
print()
print("| site | shape | reach | verdict |")
print("|---|---|---|---|")
for f,label,shape,verdict,arg in rows:
    print(f"| `{f}` | {shape} | {R(f)}/{N} | **{verdict}** |")
print()
for f,label,shape,verdict,arg in rows:
    print(f"**`{f}`** — {verdict} · reach {R(f)}/{N}\n\n{arg}\n")
