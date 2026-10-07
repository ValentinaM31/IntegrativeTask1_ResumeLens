"""UTF-8 TXT -> JSON 1.0 CLI, without overwriting by default."""
import argparse
import json
from pathlib import Path
import sys
from .first_stage import process_resume


def main(argv=None):
    parser = argparse.ArgumentParser(description="Extract and normalize a UTF-8 TXT resume")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--name", help="Optional name when an explicit name line is absent")
    parser.add_argument("--force", action="store_true", help="Allow overwriting an existing JSON file")
    args = parser.parse_args(argv)
    try:
        if args.input.suffix.lower() != ".txt":
            raise ValueError("Input must be a UTF-8 .txt file")
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Output must differ from input")
        # newline='' preserves CRLF; the UTF-8 BOM is an encoding marker.
        with args.input.open(encoding="utf-8-sig", newline="") as stream:
            text = stream.read()
        result = process_resume(text, args.name)
        payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w" if args.force else "x", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
    except UnicodeError:
        print("Error: the file is not valid UTF-8", file=sys.stderr)
        return 2
    except FileExistsError:
        print("Error: output already exists; use another path or --force", file=sys.stderr)
        return 2
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(f"JSON generated: {args.output}")
    return 0
