"""Command-line entry point for the complete workflow and HTML bundle."""
import argparse
from pathlib import Path
import sys
from textx import TextXError
from .workflow import BUNDLE_FILES, process_complete_resume, save_bundle


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run all four ResumeLens stages and generate a candidate HTML bundle")
    parser.add_argument("input", type=Path, help="UTF-8 TXT resume")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output bundle directory")
    parser.add_argument("--name", help="Optional name when an explicit name line is absent")
    parser.add_argument("--force", action="store_true", help="Allow replacing the four existing bundle files")
    args = parser.parse_args(argv)
    try:
        if args.input.suffix.lower() != ".txt":
            raise ValueError("Input must be a UTF-8 .txt file")
        for filename in BUNDLE_FILES:
            target = args.output / filename
            if (target.resolve() == args.input.resolve()
                    or (target.exists() and args.input.exists() and target.samefile(args.input))):
                raise ValueError("Bundle output must differ from input")
        # Match the original CLI: discard BOM while retaining decoded CRLF spans.
        with args.input.open(encoding="utf-8-sig", newline="") as stream:
            text = stream.read()
        result = process_complete_resume(text, args.name)
        save_bundle(result, args.output, args.force)
    except UnicodeError:
        print("Error: the file is not valid UTF-8", file=sys.stderr)
        return 2
    except (OSError, ValueError, TextXError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    accepted = result["classification"]["accepted_profiles"]
    print("Accepted profiles: " + (", ".join(accepted) or "none"))
    print(f"Validated DSL and HTML generated: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
