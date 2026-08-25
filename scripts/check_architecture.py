from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ADR_FILENAME_PATTERN = re.compile(r"^(?P<id>\d{4})-[a-z0-9-]+\.md$")
INDEX_LINK_PATTERN = re.compile(r"\((?P<target>[^)\s]+\.md)\)")
JIRA_KEY_PATTERN = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")
TERM_PATTERN = re.compile(r"^\*\*(?P<term>[^*]+)\*\*:$", re.MULTILINE)


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path}: expected a YAML mapping")
    return data


def load_front_matter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML front matter")

    parts = text.split("---", maxsplit=2)
    if len(parts) != 3:
        raise ValueError(f"{path}: invalid YAML front matter")

    metadata = yaml.safe_load(parts[1])
    if not isinstance(metadata, dict):
        raise TypeError(f"{path}: front matter must be a YAML mapping")
    return metadata


def string_list(value: object, location: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{location}: expected a list of strings")
        return []
    return value


def validate_architecture(root: Path) -> list[str]:
    errors: list[str] = []
    policy_path = root / "docs" / "architecture" / "conformance.yml"
    adr_dir = root / "docs" / "adr"
    context_path = root / "CONTEXT.md"

    try:
        policy = load_yaml(policy_path)
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        return [str(exc)]

    adr_policy = policy.get("adr")
    if not isinstance(adr_policy, dict):
        return [f"{policy_path}: adr must be a mapping"]

    index_value = adr_policy.get("index")
    if not isinstance(index_value, str):
        errors.append("adr.index: expected a repository-relative path")
        index_value = "docs/adr/README.md"
    index_path = root / index_value

    required_metadata = string_list(
        adr_policy.get("required_metadata"), "adr.required_metadata", errors
    )
    accepted_status = adr_policy.get("accepted_status")
    if not isinstance(accepted_status, str):
        errors.append("adr.accepted_status: expected a string")
        accepted_status = "accepted"

    adr_files: dict[str, Path] = {}
    accepted_adrs: set[str] = set()
    for path in sorted(adr_dir.glob("*.md")):
        match = ADR_FILENAME_PATTERN.fullmatch(path.name)
        if match is None:
            continue

        adr_id = match.group("id")
        adr_files[adr_id] = path
        try:
            metadata = load_front_matter(path)
        except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))
            continue

        for field in required_metadata:
            if field not in metadata:
                errors.append(f"{path}: missing required metadata '{field}'")
        if metadata.get("status") == accepted_status:
            accepted_adrs.add(adr_id)

    try:
        index_text = index_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(str(exc))
        index_text = ""

    indexed_names = [
        Path(match.group("target")).name
        for match in INDEX_LINK_PATTERN.finditer(index_text)
    ]
    indexed_ids = {
        match.group("id")
        for name in indexed_names
        if (match := ADR_FILENAME_PATTERN.fullmatch(name)) is not None
    }
    for name, count in Counter(indexed_names).items():
        if count > 1:
            errors.append(f"{index_path}: duplicate ADR index entry '{name}'")
    for adr_id in sorted(accepted_adrs - indexed_ids):
        errors.append(f"accepted ADR {adr_id} is not indexed in {index_path}")
    for adr_id in sorted(indexed_ids - set(adr_files)):
        errors.append(f"{index_path}: indexed ADR {adr_id} does not exist")

    try:
        context_text = context_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(str(exc))
        context_text = ""
    canonical_terms = set(TERM_PATTERN.findall(context_text))

    jira = policy.get("jira")
    project_key: str | None = None
    if not isinstance(jira, dict):
        errors.append("jira: expected a mapping")
    else:
        configured_project_key = jira.get("project_key")
        if not isinstance(configured_project_key, str) or not re.fullmatch(
            r"[A-Z][A-Z0-9]+", configured_project_key
        ):
            errors.append("jira.project_key: expected an uppercase Jira project key")
        else:
            project_key = configured_project_key
        if jira.get("workflow_status_source") != "jira":
            errors.append("jira.workflow_status_source must be 'jira'")
        if jira.get("adr_status_controls_issue_workflow") is not False:
            errors.append("ADR status must not control Jira issue workflow status")

    traceability = policy.get("traceability")
    covered_adrs: set[str] = set()
    if not isinstance(traceability, dict):
        errors.append("traceability: expected a mapping")
    else:
        for issue_key, value in traceability.items():
            valid_key = (
                isinstance(issue_key, str)
                and JIRA_KEY_PATTERN.fullmatch(issue_key) is not None
                and (project_key is None or issue_key.startswith(f"{project_key}-"))
            )
            if not valid_key:
                errors.append(f"traceability: invalid Jira key '{issue_key}'")
            adr_ids = string_list(value, f"traceability.{issue_key}", errors)
            for adr_id in adr_ids:
                if adr_id not in accepted_adrs:
                    errors.append(
                        f"traceability.{issue_key}: ADR {adr_id} is not an accepted ADR"
                    )
                covered_adrs.add(adr_id)

    coverage = policy.get("coverage")
    if not isinstance(coverage, dict) or coverage.get("accepted_adrs") != "all":
        errors.append("coverage.accepted_adrs must be 'all'")
    else:
        for adr_id in sorted(accepted_adrs - covered_adrs):
            errors.append(f"accepted ADR {adr_id} has no Jira traceability")

    invariants = policy.get("invariants")
    if not isinstance(invariants, list):
        errors.append("invariants: expected a list")
    else:
        invariant_ids: set[str] = set()
        for position, invariant in enumerate(invariants):
            location = f"invariants[{position}]"
            if not isinstance(invariant, dict):
                errors.append(f"{location}: expected a mapping")
                continue
            invariant_id = invariant.get("id")
            if not isinstance(invariant_id, str) or not invariant_id:
                errors.append(f"{location}.id: expected a non-empty string")
            elif invariant_id in invariant_ids:
                errors.append(f"{location}.id: duplicate invariant '{invariant_id}'")
            else:
                invariant_ids.add(invariant_id)

            terms = string_list(invariant.get("terms"), f"{location}.terms", errors)
            for term in terms:
                if term not in canonical_terms:
                    errors.append(f"{location}: unknown canonical term '{term}'")

            adr_ids = string_list(invariant.get("adrs"), f"{location}.adrs", errors)
            for adr_id in adr_ids:
                if adr_id not in accepted_adrs:
                    errors.append(f"{location}: ADR {adr_id} is not an accepted ADR")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the architecture contract")
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).parents[1], help="repository root"
    )
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate_architecture(root)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Architecture conformance passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
