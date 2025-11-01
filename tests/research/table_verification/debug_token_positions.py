#!/usr/bin/env python3
"""Debug script to check if tokens have line/column position info."""

from pathlib import Path
from src.ir.parser import parse_file
from lark import Tree, Token


def debug_token_positions():
    """Parse and show token position information."""
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
        print("Token positions in table_block:\n")

        # Collect all tokens
        def collect_tokens(node):
            tokens = []
            if isinstance(node, Token):
                return [node]
            elif isinstance(node, Tree):
                for child in node.children:
                    tokens.extend(collect_tokens(child))
            return tokens

        all_tokens = collect_tokens(table_blocks[0])

        print(f"{'Type':<10} {'Value':<15} {'Line':<6} {'Column':<6}")
        print("-" * 50)
        for token in all_tokens:
            line = getattr(token, "line", "N/A")
            column = getattr(token, "column", "N/A")
            print(f"{token.type:<10} {str(token.value):<15} {str(line):<6} {str(column):<6}")


if __name__ == "__main__":
    debug_token_positions()
