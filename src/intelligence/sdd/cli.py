"""CLI Commands for Spec-Driven Development.

Provides command-line interface for SDD system operations.
"""

import argparse
import sys
from typing import Dict, Any

from .context import SDDContext
from .engine import SDDEngine, get_sdd_engine
from .data_models import Intent, Spec, Plan, Guide
from ..utils import format_output


def create_parser() -> argparse.ArgumentParser:
    """Create SDD CLI argument parser.

    Returns:
        Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="sdd",
        description="Spec-Driven Development CLI - Transform intent into structured artifacts"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="Available Commands",
        required=True
    )

    # Parse intent command
    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse natural language into structured Intent"
    )
    parse_parser.add_argument(
        "input",
        help="Natural language input to parse"
    )
    parse_parser.add_argument(
        "--output", "-o",
        help="Output file for parsed intent (JSON)"
    )

    # Generate spec command
    spec_parser = subparsers.add_parser(
        "spec",
        help="Generate specification from intent"
    )
    spec_parser.add_argument(
        "input",
        help="Natural language input or intent description"
    )
    spec_parser.add_argument(
        "--output", "-o",
        help="Output file for spec (markdown)"
    )

    # Generate plan command
    plan_parser = subparsers.add_parser(
        "plan",
        help="Generate implementation plan from spec"
    )
    plan_parser.add_argument(
        "input",
        help="Specification file or description"
    )
    plan_parser.add_argument(
        "--output", "-o",
        help="Output file for plan (markdown)"
    )

    # Generate guide command
    guide_parser = subparsers.add_parser(
        "guide",
        help="Generate execution guide from plan"
    )
    guide_parser.add_argument(
        "input",
        help="Plan file or description"
    )
    guide_parser.add_argument(
        "--output", "-o",
        help="Output file for guide (markdown)"
    )

    # Full pipeline command
    pipeline_parser = subparsers.add_parser(
        "pipeline",
        help="Execute full SDD pipeline (intent -> spec -> plan -> guide)"
    )
    pipeline_parser.add_argument(
        "input",
        help="Natural language input to process"
    )
    pipeline_parser.add_argument(
        "--start", "-s",
        choices=["intent", "spec", "plan", "guide"],
        default="intent",
        help="Stage to start from (default: intent)"
    )
    pipeline_parser.add_argument(
        "--end", "-e",
        choices=["intent", "spec", "plan", "guide"],
        default="guide",
        help="Stage to end at (default: guide)"
    )
    pipeline_parser.add_argument(
        "--output-dir", "-d",
        help="Output directory for all artifacts"
    )

    # List agents command
    list_parser = subparsers.add_parser(
        "list",
        help="List registered SDD agents and skills"
    )
    list_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed information"
    )

    return parser


def handle_parse(args) -> None:
    """Handle 'parse' command.

    Args:
        args: Parsed command-line arguments.
    """
    print(f"Parsing intent: {args.input[:50]}...")

    # Create context and parse
    context = SDDContext(args.input)
    engine = get_sdd_engine()

    # Parse intent
    result = engine.can_handle(args.input)

    print("\n=== Intent Analysis ===")
    print(f"Intent Type: {result['intent_type']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Suggested Workflow: {' -> '.join(result['suggested_workflow'])}")

    # Output to file if requested
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nIntent saved to: {args.output}")


def handle_spec(args) -> None:
    """Handle 'spec' command.

    Args:
        args: Parsed command-line arguments.
    """
    print(f"Generating specification for: {args.input[:50]}...")

    # Create context and generate spec
    context = SDDContext(args.input)
    engine = get_sdd_engine()

    # Execute from intent to spec
    results = engine.execute(
        args.input,
        start_stage="intent",
        end_stage="spec"
    )

    # Extract spec artifact
    spec_artifact = results["artifacts"].get("spec")
    if spec_artifact:
        print("\n=== Specification Generated ===")
        print(spec_artifact["content"])

        # Output to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(spec_artifact["content"])
            print(f"\nSpecification saved to: {args.output}")
    else:
        print("\nNo specification artifact generated.")


def handle_plan(args) -> None:
    """Handle 'plan' command.

    Args:
        args: Parsed command-line arguments.
    """
    print(f"Generating implementation plan for: {args.input[:50]}...")

    # Create context and generate plan
    context = SDDContext(args.input)
    engine = get_sdd_engine()

    # Execute from spec to plan
    results = engine.execute(
        args.input,
        start_stage="intent",
        end_stage="plan"
    )

    # Extract plan artifact
    plan_artifact = results["artifacts"].get("plan")
    if plan_artifact:
        print("\n=== Implementation Plan Generated ===")
        print(plan_artifact["content"])

        # Output to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(plan_artifact["content"])
            print(f"\nPlan saved to: {args.output}")
    else:
        print("\nNo plan artifact generated.")


def handle_guide(args) -> None:
    """Handle 'guide' command.

    Args:
        args: Parsed command-line arguments.
    """
    print(f"Generating execution guide for: {args.input[:50]}...")

    # Create context and generate guide
    context = SDDContext(args.input)
    engine = get_sdd_engine()

    # Execute full pipeline to get guide
    results = engine.execute(
        args.input,
        start_stage="intent",
        end_stage="guide"
    )

    # Extract guide artifact
    guide_artifact = results["artifacts"].get("guide")
    if guide_artifact:
        print("\n=== Execution Guide Generated ===")
        print(guide_artifact["content"])

        # Output to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(guide_artifact["content"])
            print(f"\nGuide saved to: {args.output}")
    else:
        print("\nNo guide artifact generated.")


def handle_pipeline(args) -> None:
    """Handle 'pipeline' command.

    Args:
        args: Parsed command-line arguments.
    """
    print(f"Executing SDD pipeline: {args.input[:50]}...")
    print(f"Pipeline: {args.start} -> {args.end}")

    # Create context and execute
    engine = get_sdd_engine()
    results = engine.execute(
        args.input,
        start_stage=args.start,
        end_stage=args.end
    )

    # Display results
    print(f"\n=== Pipeline Complete ===")
    print(f"Workflow State: {results['workflow_state']}")
    print(f"Artifacts Generated: {len(results['artifacts'])}")

    # Output artifacts to directory if requested
    if args.output_dir:
        import os
        import json
        os.makedirs(args.output_dir, exist_ok=True)

        # Save each artifact
        for name, artifact in results["artifacts"].items():
            ext = "md" if name in ["spec", "plan", "guide"] else "json"
            filename = f"{args.output_dir}/{name}.{ext}"

            with open(filename, 'w') as f:
                if ext == "json":
                    json.dump(artifact, f, indent=2)
                else:
                    f.write(artifact["content"])

            print(f"  Saved: {filename}")

        # Save intent
        if "intent" in results:
            intent_file = f"{args.output_dir}/intent.json"
            with open(intent_file, 'w') as f:
                json.dump(results["intent"], f, indent=2)
            print(f"  Saved: {intent_file}")


def handle_list(args) -> None:
    """Handle 'list' command.

    Args:
        args: Parsed command-line arguments.
    """
    engine = get_sdd_engine()

    print("\n=== Registered SDD Agents ===")
    for agent_name in engine.get_registered_agents():
        print(f"  - {agent_name}")
        if args.verbose:
            agent = engine.get_agent(agent_name)
            print(f"    Description: {agent.description if hasattr(agent, 'description') else 'N/A'}")

    print("\n=== Registered SDD Skills ===")
    from ..skills.skill_registry import get_global_registry
    registry = get_global_registry()

    for skill_name in registry.list_names():
        print(f"  - {skill_name}")
        if args.verbose:
            metadata = registry.get_metadata(skill_name)
            print(f"    Description: {metadata.description}")
            print(f"    Version: {metadata.version}")


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Route to handler
    handlers = {
        "parse": handle_parse,
        "spec": handle_spec,
        "plan": handle_plan,
        "guide": handle_guide,
        "pipeline": handle_pipeline,
        "list": handle_list
    }

    handler = handlers.get(args.command)
    if handler:
        try:
            handler(args)
        except Exception as e:
            print(f"\nError: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
