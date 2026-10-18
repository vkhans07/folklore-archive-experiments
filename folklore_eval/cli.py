import argparse
import json

from .evaluate import evaluate, evaluate_archive
from .predict import freeze_prompt, predict
from .prepare import prepare
from .report import report, report_archive


def main():
    parser = argparse.ArgumentParser(prog="folklore-eval")
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--doc")
    p = commands.add_parser("freeze-prompt")
    p.add_argument("--target", choices=["archive", "regions"], default="archive")
    p = commands.add_parser("predict")
    p.add_argument("--doc")
    p.add_argument("--model")
    p.add_argument("--phase", choices=["development", "evaluation"], default="development")
    p.add_argument("--target", choices=["archive", "regions"], default="archive")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-resume", action="store_true")
    p = commands.add_parser("evaluate")
    p.add_argument("--doc")
    p.add_argument("--model")
    p.add_argument("--phase", choices=["development", "evaluation"], default="evaluation")
    p.add_argument("--target", choices=["archive", "regions"], default="archive")
    p = commands.add_parser("report")
    p.add_argument("--phase", choices=["development", "evaluation"], default="evaluation")
    p.add_argument("--target", choices=["archive", "regions"], default="archive")
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.doc)
    elif args.command == "freeze-prompt":
        result = freeze_prompt(args.target)
    elif args.command == "predict":
        result = predict(args.doc, args.model, args.phase, args.dry_run, not args.no_resume, args.target)
    elif args.command == "evaluate":
        result = evaluate_archive(args.phase, args.doc, args.model) if args.target == "archive" else evaluate(args.phase, args.doc, args.model)
    else:
        result = report_archive(args.phase) if args.target == "archive" else report(args.phase)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
