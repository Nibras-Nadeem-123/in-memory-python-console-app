#!/usr/bin/env python
"""
Demonstration of the Spec-Driven Development System.

This script shows the complete SDD workflow:
1. Intent parsing
2. Specification generation
3. Plan generation
4. Implementation guide generation
"""

from src.intelligence.sdd import get_sdd_engine, SDDContext


def demo_basic_workflow():
    """Demonstrate basic SDD workflow."""
    print("\n" + "=" * 70)
    print("SDD System Demonstration: Todo Application")
    print("=" * 70 + "\n")

    # Get the SDD engine
    engine = get_sdd_engine()

    # User input
    user_input = "Create a todo application with task management, priorities, and persistence"
    print(f"User Input: {user_input}\n")

    # Create context
    context = SDDContext(user_input)

    print("Starting SDD pipeline...\n")

    # Execute Stage 1: Intent Parsing
    print("Stage 1: Parsing Intent...")
    try:
        intent_agent = engine.get_agent("intent")
        intent = intent_agent.execute(context, user_input)
        print(f"✓ Intent Type: {intent.type.value}")
        print(f"✓ Confidence: {intent.confidence:.2f}\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return

    # Execute Stage 2: Specification Generation
    print("Stage 2: Generating Specification...")
    try:
        spec_agent = engine.get_agent("spec")
        spec = spec_agent.execute(context)
        print(f"✓ Spec Title: {spec.title}")
        print(f"✓ Requirements: {len(spec.requirements)} found\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return

    # Execute Stage 3: Plan Generation
    print("Stage 3: Generating Implementation Plan...")
    try:
        plan_agent = engine.get_agent("plan")
        plan = plan_agent.execute(context)
        print(f"✓ Plan Title: {plan.title}")
        print(f"✓ Architecture: {plan.architecture}")
        print(f"✓ Tasks: {len(plan.tasks)} generated\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return

    # Execute Stage 4: Guide Generation
    print("Stage 4: Generating Implementation Guide...")
    try:
        guide_agent = engine.get_agent("guide")
        guide = guide_agent.execute(context)
        print(f"✓ Guide Title: {guide.title}")
        print(f"✓ Implementation Order: {guide.implementation_order}\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return

    # Show summary
    print("=" * 70)
    print("SDD Pipeline Complete!")
    print("=" * 70)
    print(f"\nGenerated Artifacts:")
    print(f"  - Intent: {intent.type.value}")
    print(f"  - Specification: {len(spec.requirements)} requirements")
    print(f"  - Plan: {len(plan.tasks)} tasks")
    print(f"  - Guide: Implementation guidance")
    print(f"\nWorkflow Events: {len(context.events)}")
    print(f"Workflow State: {context.workflow_state}")


def demo_full_pipeline():
    """Demonstrate full pipeline execution using engine."""
    print("\n" + "=" * 70)
    print("SDD System Demonstration: Full Pipeline")
    print("=" * 70 + "\n")

    engine = get_sdd_engine()

    user_input = "Build a REST API for user authentication with JWT tokens"
    print(f"User Input: {user_input}\n")

    print("Executing full pipeline (intent → spec → plan → guide)...\n")

    try:
        results = engine.execute(
            user_input,
            start_stage="intent",
            end_stage="guide"
        )

        print("✓ Pipeline completed successfully!\n")
        print("Results:")
        print(f"  - Intent Type: {results['intent']['type']}")
        print(f"  - Confidence: {results['intent']['confidence']:.2f}")
        print(f"  - Artifacts Generated: {len(results['artifacts'])}")
        print(f"  - Workflow State: {results['workflow_state']}")
        print(f"\nArtifacts:")
        for name, artifact in results['artifacts'].items():
            print(f"  - {name}: {len(str(artifact['content']))} chars")

    except Exception as e:
        print(f"✗ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys

    # Choose demo based on argument
    if len(sys.argv) > 1 and sys.argv[1] == "full":
        demo_full_pipeline()
    else:
        demo_basic_workflow()
