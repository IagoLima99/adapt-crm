import re
from pathlib import Path
from typing import Any

import yaml

WORKFLOW_PATH = Path(__file__).parents[2] / ".github" / "workflows" / "ci.yml"


def load_workflow() -> dict[str, Any]:
    workflow = yaml.load(
        WORKFLOW_PATH.read_text(encoding="utf-8"), Loader=yaml.BaseLoader
    )

    assert isinstance(workflow, dict)
    return workflow


def workflow_steps() -> list[dict[str, Any]]:
    jobs = load_workflow().get("jobs")

    assert isinstance(jobs, dict)
    steps: list[dict[str, Any]] = []
    for job in jobs.values():
        assert isinstance(job, dict)
        job_steps = job.get("steps")
        assert isinstance(job_steps, list)
        assert all(isinstance(step, dict) for step in job_steps)
        steps.extend(job_steps)

    return steps


def test_ci_keeps_required_quality_gates() -> None:
    workflow = load_workflow()
    steps = workflow_steps()
    commands = "\n".join(str(step["run"]) for step in steps if "run" in step)

    required_commands = (
        "uv run ruff check .",
        "uv run ruff format --check .",
        'uv run mypy "${targets[@]}"',
        "uv run pytest -q",
        "npm run test --workspace @adaptcrm/web",
        "npm run lint --workspace @adaptcrm/web",
        "npm run typecheck --workspace @adaptcrm/web",
    )

    triggers = workflow.get("on")
    assert isinstance(triggers, dict)
    assert "pull_request" in triggers
    assert all("continue-on-error" not in step for step in steps)
    assert all(command in commands for command in required_commands)


def test_ci_pins_external_actions_to_commits() -> None:
    action_references = [
        str(step["uses"]) for step in workflow_steps() if "uses" in step
    ]

    assert action_references
    assert all(re.fullmatch(r"[^@]+@[0-9a-f]{40}", ref) for ref in action_references)


def test_ci_build_is_traceable_to_version_and_commit() -> None:
    steps = workflow_steps()
    commands = "\n".join(str(step["run"]) for step in steps if "run" in step)
    artifacts = [
        step
        for step in steps
        if str(step.get("uses", "")).startswith("actions/upload-artifact@")
    ]

    assert "git archive" in commands
    assert "node apps/web/scripts/build-metadata.mjs" in commands
    assert len(artifacts) == 1
    assert artifacts[0]["with"]["path"] == "build/"
