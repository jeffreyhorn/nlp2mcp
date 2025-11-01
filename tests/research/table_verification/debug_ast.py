#!/usr/bin/env python3
"""Debug script to examine the AST structure for sparse tables."""

from pathlib import Path
from src.ir.parser import parse_file
from lark import Tree, Token


def print_tree(node, indent=0):
    """Recursively print the parse tree structure."""
    prefix = "  " * indent
    if isinstance(node, Tree):
        print(f"{prefix}{node.data}")
        for child in node.children:
            print_tree(child, indent + 1)
    elif isinstance(node, Token):
        print(f"{prefix}Token({node.type}, {node.value!r})")
    else:
        print(f"{prefix}{type(node).__name__}: {node}")


def debug_sparse_table():
    """Parse and debug sparse table AST."""
    gms_file = Path(__file__).parent / "test_sparse_table.gms"

    print(f"Parsing: {gms_file}\n")
    tree = parse_file(str(gms_file))

    # Find the table_block node
    def find_table_blocks(node):
        if isinstance(node, Tree):
            if node.data == "table_block":
                return [node]
            results = []
            for child in node.children:
                results.extend(find_table_blocks(child))
            return results
        return []

    table_blocks = find_table_blocks(tree)

    if table_blocks:
        print("Found table_block AST:\n")
        print_tree(table_blocks[0])

        print("\n" + "=" * 60)
        print("Analyzing table_row nodes:")
        print("=" * 60)

        for i, child in enumerate(table_blocks[0].children):
            if isinstance(child, Tree) and child.data == "table_row":
                print(f"\nRow {i}:")
                tokens = []
                for token_child in child.children:
                    if isinstance(token_child, Token):
                        tokens.append(f"{token_child.type}:{token_child.value}")
                    elif isinstance(token_child, Tree) and token_child.data == "table_value":
                        for grandchild in token_child.children:
                            if isinstance(grandchild, Token):
                                tokens.append(f"{grandchild.type}:{grandchild.value}")
                print(f"  Tokens: {tokens}")


if __name__ == "__main__":
    debug_sparse_table()
