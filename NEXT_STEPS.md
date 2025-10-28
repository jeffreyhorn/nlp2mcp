Notes & next steps

This grammar + IR gets you through Sprint 1 objectives: you can parse declarations, equations, assignments (incl. x.lo = …), and the Solve line into a structured ModelIR.

In Sprint 2 you’ll:

build the parser using Lark visitors/transformers that instantiate these IR classes,

add shape/dimension checks against the domain tuples,

and start wiring the AD engine over ir.ast nodes.

If you want, I can also drop a tiny parser.py skeleton with a Lark(…, parser="lalr") and a Transformer that constructs ModelIR incrementally.
