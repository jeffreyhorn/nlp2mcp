* eolcom.gms - End-of-line comment directive test
* Tests: $eolCom character definition

$eolCom #

Sets
    i / 1*5 /;  # This is a comment using the new eolcom character

Scalars
    x / 10 /;   # Another comment

# Full line comment
display x;  # Inline comment
