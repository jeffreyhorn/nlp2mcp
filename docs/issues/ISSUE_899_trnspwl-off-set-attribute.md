# trnspwl: `.off` set attribute (zero-based ordinal)

**GitHub Issue:** [#899](https://github.com/jeffreyhorn/nlp2mcp/issues/899)
**Model:** trnspwl (GAMSlib SEQ=385, "A Transportation Problem with discretized economies of scale")
**Error category:** `parser_invalid_expression`
**Error message:** `Unsupported expression type: attr_access`

## Description

The parser fails on `ss.off` — the `.off` attribute on a set element that returns the zero-based ordinal position (like `.ord` but starting from 0 instead of 1).

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/trnspwl.gms')
"
```

## Relevant Code (lines 140–150)

```gams
abort$(xmax < xhigh) 'xhigh too big', xhigh, xmax;
abort$(xlow < 0)     'xlow less than 0', xlow;

* Equidistant sampling of the sqrt function with slopes at the beginning and end
p('slope0') = -1;
p(ss)       = xlow + (xhigh-xlow)/(card(ss)-1)*ss.off;
p('slopeN') = 1;

sqrtp('slope0') = -1/sqrt(xlow);
sqrtp(ss)       = sqrt(p(ss));
sqrtp('slopeN') = (sqrt(xmax)-sqrt(xhigh))/(xmax-xhigh);
```

## Root Cause

1. `ss.off` is a GAMS set attribute that returns the zero-based ordinal of element `ss` in its domain (equivalent to `ord(ss) - 1`)
2. The grammar parses this as `attr_access` but the IR builder's `_expr()` does not handle `.off`
3. The recognized set attributes are `.pos`, `.ord`, `.val`, `.len`, `.tl`, `.te`, `.ts`, `.tf` — `.off` is missing

## Related Issues (duplicate cluster: `attr_access` / model attributes)

This issue shares the `attr_access` root cause with:
- [#897](https://github.com/jeffreyhorn/nlp2mcp/issues/897) — feasopt1: `.infeas` attribute + `File` declaration (primary issue)
- [#898](https://github.com/jeffreyhorn/nlp2mcp/issues/898) — mathopt4: `.modelStat` model attribute

**Primary fix:** Add `attr_access` and `attr_access_indexed` handlers to the IR builder's `_expr()` method. Fixing #897 should also resolve the `attr_access` portion of this issue.

## Fix Approach

1. Add `attr_access` handler to `_expr()` in `src/ir/parser.py` — shared with #897, #898
2. Add `.off` to the set attribute handlers in the IR builder
3. Translate `ss.off` as `ord(ss) - 1` in the IR (since `.off` = `.ord` - 1)
4. This is a straightforward addition similar to how `.ord` is already handled
