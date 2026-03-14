"""Quick verification of Module 3 — Workflow Engine."""
import sys
sys.path.insert(0, r"d:\Antigravity\AG-Agent")

print("=== Antigravity Module 3 Verification ===\n")

try:
    from workflow_engine import WorkflowEngine, WorkflowStep, engine
    print("OK workflow_engine.py")
except Exception as e:
    print(f"FAIL workflow_engine.py: {e}")
    sys.exit(1)

try:
    from workflows.research_workflow import (
        build_research_workflow,
        build_slides_workflow,
        build_qa_workflow,
        register_all
    )
    print("OK workflows/research_workflow.py")
except Exception as e:
    print(f"FAIL workflows/research_workflow.py: {e}")
    sys.exit(1)

wf_list = engine.list_workflows()
print(f"OK Registered workflows: {wf_list}")

print("\nRunning dry-run test workflow...")

def hello_step(context: dict, name: str = "World") -> str:
    return f"Hello, {name}! Context keys: {list(context.keys())}"

def append_step(context: dict) -> str:
    prev = context.get("hello_step", "")
    return prev + " | Step 2 done."

test_steps = [
    WorkflowStep("Hello Step", hello_step, params={"name": "Antigravity"}),
    WorkflowStep("Append Step", append_step),
]

result = engine.run("Test Workflow", steps=test_steps, initial_context={"seed": "test"})
print(f"\nOK Workflow success: {result.success}")
print(f"OK Final context keys: {list(result.context.keys())}")
print(f"OK Output: {result.context.get('append_step', '')[:80]}")

try:
    import main
    print("\nOK main.py (v0.3)")
except Exception as e:
    print(f"FAIL main.py: {e}")

print("\n=== Done ===")
