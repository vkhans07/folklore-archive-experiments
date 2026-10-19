import argparse
import json

from .evaluate import evaluate, evaluate_archive
from .predict import freeze_prompt, predict
from .prepare import prepare
from .report import report, report_archive

PROMPT_VERSIONS = ["archive_v2", "archive_v3", "regions_v1", "regions_v3"]


def main():
    parser = argparse.ArgumentParser(prog="folklore-eval")
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--doc")
    p = commands.add_parser("freeze-prompt")
    p.add_argument("--target", choices=["archive", "regions"], default="archive")
    p.add_argument("--prompt-version", choices=PROMPT_VERSIONS)
    p = commands.add_parser("predict")
    p.add_argument("--doc")
    p.add_argument("--model")
    p.add_argument("--phase", choices=["development", "evaluation"], default="development")
    p.add_argument("--target", choices=["archive", "regions"], default="archive")
    p.add_argument("--prompt-version", choices=PROMPT_VERSIONS)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-resume", action="store_true")
    p = commands.add_parser("evaluate")
    p.add_argument("--prompt-version", choices=PROMPT_VERSIONS)
    p.add_argument("--doc")
    p.add_argument("--model")
    p.add_argument("--phase", choices=["development", "evaluation"], default="evaluation")
    p.add_argument("--target", choices=["archive", "regions"], default="archive")
    p = commands.add_parser("report")
    p.add_argument("--prompt-version", choices=PROMPT_VERSIONS)
    p.add_argument("--phase", choices=["development", "evaluation"], default="evaluation")
    p.add_argument("--target", choices=["archive", "regions"], default="archive")
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.doc)
    elif args.command == "freeze-prompt":
        result = freeze_prompt(args.target, args.prompt_version)
    elif args.command == "predict":
        result = predict(args.doc, args.model, args.phase, args.dry_run, not args.no_resume, args.target, args.prompt_version)
    elif args.command == "evaluate":
        result = evaluate_archive(args.phase, args.doc, args.model, args.prompt_version) if args.target == "archive" else evaluate(args.phase, args.doc, args.model, args.prompt_version)
    else:
        result = report_archive(args.phase, args.prompt_version) if args.target == "archive" else report(args.phase, args.prompt_version)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
