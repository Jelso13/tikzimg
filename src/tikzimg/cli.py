import argparse
import logging
import subprocess
from pathlib import Path
from typing import Sequence

from .core import process_command

def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    # ... (code for parse_args is identical to the original script) ...
    parser = argparse.ArgumentParser(
        description="A CLI tool to quickly create and compile TikZ diagrams to SVG."
    )
    parser.add_argument("file", nargs='?', type=Path, default=None, help="An existing .tex file to process.")
    parser.add_argument("-o", "--output", type=Path, default=Path.cwd(), help="The output directory.")
    parser.add_argument("-t", "--type", type=str, default='svg', help="Output type (currently only 'svg').")
    return parser.parse_args(argv)

def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s  - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    args = parse_args(argv)
    args.output = args.output.resolve()

    try:
        logging.info("RUNNING")
        process_command(args)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logging.error(f"A critical error occurred: {e}")
        return 1
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return 1

    return 0

if __name__ == '__main__':
    # Allows running the module directly via `python -m tikzimg.cli`
    raise SystemExit(main())
