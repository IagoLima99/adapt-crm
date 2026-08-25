import re
from pathlib import Path

WORKFLOW_PATH = Path(__file__).parents[2] / ".github" / "workflows" / "ci.yml"


def test_ci_keeps_required_quality_gates() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    required_commands = (
        "uv run ruff check .",
        "uv run ruff format --check .",
        'uv run mypy "${targets[@]}"',
        "uv run pytest -q",
        "npm run test --workspace @adaptcrm/web -- --passWithNoTests",
        "npm run lint --workspace @adaptcrm/web",
        "npm run web:build",
    )

    assert "pull_request:" in workflow
    assert "continue-on-error" not in workflow
    assert all(command in workflow for command in required_commands)


def test_ci_pins_external_actions_to_commits() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    action_references = re.findall(r"^\s*uses:\s+([^\s#]+)", workflow, re.MULTILINE)

    assert action_references
    assert all(re.fullmatch(r"[^@]+@[0-9a-f]{40}", ref) for ref in action_references)


def test_ci_records_version_and_commit_in_build_metadata() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "build/metadata.json" in workflow
    assert "version:p.version" in workflow
    assert "commit:process.env.GITHUB_SHA" in workflow
