from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parents[2]
CHECKER_PATH = PROJECT_ROOT / "scripts" / "check_architecture.py"


def copy_contract(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    (root / "docs" / "architecture").mkdir(parents=True)
    shutil.copy2(PROJECT_ROOT / "CONTEXT.md", root / "CONTEXT.md")
    shutil.copytree(PROJECT_ROOT / "docs" / "adr", root / "docs" / "adr")
    shutil.copy2(
        PROJECT_ROOT / "docs" / "architecture" / "conformance.yml",
        root / "docs" / "architecture" / "conformance.yml",
    )
    return root


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER_PATH), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


def load_policy(root: Path) -> tuple[Path, dict[str, object]]:
    path = root / "docs" / "architecture" / "conformance.yml"
    policy = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(policy, dict)
    return path, policy


def write_policy(path: Path, policy: dict[str, object]) -> None:
    path.write_text(
        yaml.safe_dump(policy, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


def test_published_architecture_contract_is_conformant(tmp_path: Path) -> None:
    result = run_checker(copy_contract(tmp_path))

    assert result.returncode == 0, result.stdout
    assert "Architecture conformance passed" in result.stdout


def test_accepted_adr_must_be_indexed(tmp_path: Path) -> None:
    root = copy_contract(tmp_path)
    (root / "docs" / "adr" / "9999-unindexed.md").write_text(
        "---\nstatus: accepted\n---\n\n# Unindexed\n", encoding="utf-8"
    )

    result = run_checker(root)

    assert result.returncode == 1
    assert "accepted ADR 9999 is not indexed" in result.stdout


def test_adr_requires_structured_metadata(tmp_path: Path) -> None:
    root = copy_contract(tmp_path)
    adr = root / "docs" / "adr" / "0001-templates-versionados-sem-heranca-automatica.md"
    adr.write_text("# Missing metadata\n", encoding="utf-8")

    result = run_checker(root)

    assert result.returncode == 1
    assert "missing YAML front matter" in result.stdout


def test_traceability_requires_valid_jira_keys_and_complete_coverage(
    tmp_path: Path,
) -> None:
    root = copy_contract(tmp_path)
    path, policy = load_policy(root)
    traceability = policy["traceability"]
    assert isinstance(traceability, dict)
    traceability["invalid"] = traceability.pop("EL-13")
    assert isinstance(traceability["invalid"], list)
    traceability["invalid"].remove("0001")
    write_policy(path, policy)

    result = run_checker(root)

    assert result.returncode == 1
    assert "invalid Jira key 'invalid'" in result.stdout
    assert "accepted ADR 0001 has no Jira traceability" in result.stdout


def test_invariants_reference_canonical_terms(tmp_path: Path) -> None:
    root = copy_contract(tmp_path)
    path, policy = load_policy(root)
    invariants = policy["invariants"]
    assert isinstance(invariants, list)
    assert isinstance(invariants[0], dict)
    invariants[0]["terms"] = ["Unknown Domain Term"]
    write_policy(path, policy)

    result = run_checker(root)

    assert result.returncode == 1
    assert "unknown canonical term 'Unknown Domain Term'" in result.stdout


def test_adr_status_cannot_control_jira_workflow(tmp_path: Path) -> None:
    root = copy_contract(tmp_path)
    path, policy = load_policy(root)
    jira = policy["jira"]
    assert isinstance(jira, dict)
    jira["adr_status_controls_issue_workflow"] = True
    write_policy(path, policy)

    result = run_checker(root)

    assert result.returncode == 1
    assert "ADR status must not control Jira issue workflow status" in result.stdout
