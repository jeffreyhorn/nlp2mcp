#!/usr/bin/env python3
"""Convert a GAMS NLP model to MCP GAMS format using the Converter.

This script demonstrates the end-to-end conversion pipeline:
1. Parse GAMS source → IR
2. Convert IR → MCP GAMS format

Usage:
    python scripts/convert_model.py <input.gms> <output.gms>

Exit codes:
    0: Conversion succeeded
    1: Conversion failed (parse or conversion errors)
    2: Invalid arguments or file not found
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.converter import Converter
from src.ir.parser import parse_model_file


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/convert_model.py <input.gms> <output.gms>")
        sys.exit(2)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(2)

    print(f"Converting {input_file} → {output_file}")
    print("-" * 60)

    # Step 1: Parse GAMS source → IR
    print("\n[1/3] Parsing GAMS source to IR...")
    try:
        ir = parse_model_file(str(input_file))
        print(f"  ✓ Parsed successfully")
        print(f"    - Variables: {len(ir.variables)}")
        print(f"    - Parameters: {len(ir.params)}")
        print(f"    - Equations: {len(ir.equations)}")
    except Exception as e:
        print(f"  ✗ Parse failed: {e}")
        sys.exit(1)

    # Step 2: Convert IR → MCP GAMS
    print("\n[2/3] Converting IR to MCP GAMS format...")
    try:
        converter = Converter(ir)
        result = converter.convert()

        if not result.success:
            print(f"  ✗ Conversion failed:")
            for error in result.errors:
                print(f"    - {error}")
            sys.exit(1)

        print(f"  ✓ Converted successfully")
    except Exception as e:
        print(f"  ✗ Conversion error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Save output
    print(f"\n[3/3] Writing output to {output_file}...")
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(result.output)
        print(f"  ✓ Wrote {len(result.output)} characters")
    except Exception as e:
        print(f"  ✗ Write failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ Conversion complete!")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
