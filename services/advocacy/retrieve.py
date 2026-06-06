#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from signbridge_advocacy import AdvocacyPipeline, LocalRetriever


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Signbridge advocacy retrieval interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search verified source chunks")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=5)
    search_parser.add_argument("--policy-only", action="store_true")

    policy_parser = subparsers.add_parser("policy", help="Generate policy.card events")
    policy_parser.add_argument("text")
    policy_parser.add_argument("--session-id", default="demo-001")
    policy_parser.add_argument("--utterance-id", default="u-demo")
    policy_parser.add_argument("--limit", type=int, default=5)

    questions_parser = subparsers.add_parser("questions", help="Generate policy.card and question.prompt events")
    questions_parser.add_argument("text")
    questions_parser.add_argument("--session-id", default="demo-001")
    questions_parser.add_argument("--utterance-id", default="u-demo")

    args = parser.parse_args()
    if args.command == "search":
        retriever = LocalRetriever()
        results = retriever.search(args.query, limit=args.limit, policy_only=args.policy_only)
        print(
            json.dumps(
                [
                    {
                        "chunk_id": result.chunk.chunk_id,
                        "score": result.score,
                        "title": result.chunk.title,
                        "source_title": result.source.title,
                        "source_url": result.chunk.source_url,
                        "quote": result.chunk.quote,
                        "text": result.chunk.text,
                    }
                    for result in results
                ],
                indent=2,
            )
        )
    elif args.command == "policy":
        pipeline = AdvocacyPipeline()
        events = pipeline.run_turn(
            args.text,
            session_id=args.session_id,
            utterance_id=args.utterance_id,
            card_limit=args.limit,
            question_limit=0,
        )
        print(json.dumps(events["policy_cards"], indent=2))
    elif args.command == "questions":
        pipeline = AdvocacyPipeline()
        events = pipeline.run_turn(args.text, session_id=args.session_id, utterance_id=args.utterance_id)
        print(json.dumps(events, indent=2))


if __name__ == "__main__":
    main()
