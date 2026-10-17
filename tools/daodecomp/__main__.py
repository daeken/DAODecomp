import argparse
from pathlib import Path
from .harness import compare, load_json, write_json
from .pe import fingerprint


def main():
    parser = argparse.ArgumentParser(description="DAODecomp intake and differential validation")
    commands = parser.add_subparsers(dest="command", required=True)
    intake = commands.add_parser("fingerprint", help="hash and inspect a PE without executing it")
    intake.add_argument("binary")
    intake.add_argument("--output", required=True)
    check = commands.add_parser("compare", help="compare two JSON protocol runners")
    check.add_argument("--contract", required=True)
    check.add_argument("--cases", required=True)
    check.add_argument("--oracle-command", required=True, help="JSON file containing an argv array")
    check.add_argument("--candidate-command", required=True, help="JSON file containing an argv array")
    check.add_argument("--artifact", action="append", default=[], help="file to hash before/after execution")
    check.add_argument("--output", required=True)
    check.add_argument("--timeout", type=float, default=5)
    check.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args()
    try:
        inputs = ([args.binary] if args.command == "fingerprint" else
                  [args.contract, args.cases, args.oracle_command, args.candidate_command, *args.artifact])
        destination = Path(args.output).resolve()
        for source in map(Path, inputs):
            if destination == source.resolve() or (destination.exists() and source.exists() and destination.samefile(source)):
                raise ValueError("output must not overwrite an input file")
        if args.command == "fingerprint":
            result = fingerprint(args.binary)
        else:
            result = compare(load_json(args.contract), load_json(args.cases),
                             load_json(args.oracle_command), load_json(args.candidate_command),
                             repeats=args.repeats, timeout=args.timeout,
                             artifacts=[args.contract, args.cases, args.oracle_command,
                                        args.candidate_command, *args.artifact])
        write_json(args.output, result)
        print(f"{result.get('status', 'fingerprinted')}: {args.output}")
        return 1 if result.get("status") == "failed" else 0
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())

