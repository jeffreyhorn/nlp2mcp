$title Head-Offset IR Round-Trip Fixture (Sprint 31 P1 — #1443)
* Minimal mine-shaped model: a head-domain-offset equation pr(k,l+1,i,j) whose
* head carries +1 on domain position l, plus parameter offsets li(k)/lj(k) on the
* body tail indices. Guards the P1 head-offset IR plumbing at the PARSE layer:
* after Phase 1 lands, parse -> EquationDef must carry
*   head_domain_offsets[1] == IndexOffset('l', Const(1.0), circular=False)
* (the l+1 head), while the param offsets li(k)/lj(k) stay preserved in the body.
* See docs/planning/EPIC_4/SPRINT_31/HEAD_OFFSET_IR_PLUMBING_DESIGN.md §4.

Set k /nw/, l /1*3/, i /1*2/, j /1*2/;
Parameter li(k) /nw 0/, lj(k) /nw 0/;
Set c(l,i,j); c(l,i,j) = yes;
Positive Variable x(l,i,j);
Variable z;
x.up(l,i,j) = 1;
Equation pr(k,l+1,i,j), def;
pr(k,l+1,i,j)$(c(l,i,j) and ord(l) < card(l))..  x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j);
def..                     z =e= sum((l,i,j), x(l,i,j));
Model m /all/;  Solve m maximizing z using lp;
