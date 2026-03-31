# mexls: Universal Set '*' Not Found in ModelIR

**GitHub Issue:** [#940](https://github.com/jeffreyhorn/nlp2mcp/issues/940)
**Status:** FIXED (universal set error resolved; translation may timeout for large model)
**Model:** mexls (GAMSlib SEQ=210, "Mexico Steel - Large Static")

## Fix

Added universal set `*` handling in `resolve_set_members()` (`src/ad/index_mapping.py`). When `*` is encountered as a set domain, the function computes the union of all elements from all declared sets in the model. This resolves the `"Set or alias '*' not found"` error.

The model now progresses past the index mapping stage into the differentiation phase. As a large LP model, translation may still take significant time (similar to other LP timeout models).

**Changes:**
- `src/ad/index_mapping.py`: Added `*` handling before the `raise ValueError` — collects all unique elements from all sets
