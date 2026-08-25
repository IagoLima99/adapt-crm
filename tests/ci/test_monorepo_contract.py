from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import tomllib

PROJECT_ROOT = Path(__file__).parents[2]

APPLICATIONS = {
    "api": PROJECT_ROOT / "apps" / "api",
    "web": PROJECT_ROOT / "apps" / "web",
    "worker": PROJECT_ROOT / "apps" / "worker",
}

PYTHON_APP_MODULES = {
    "api": {"adaptcrm_worker"},
    "worker": {"adaptcrm_api"},
}

TYPESCRIPT_CROSS_APP_IMPORT = re.compile(
    r"(?:from\s+|import\s*\()\s*['\"](?:@adaptcrm/(?:api|worker)|(?:\.\./)+(?:api|worker)(?:/|['\"]))"
)


def read_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def read_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as file:
        return tomllib.load(file)


def imported_python_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module)
    return modules


def test_monorepo_tree_and_workspace_members_are_explicit() -> None:
    assert all(path.is_dir() for path in APPLICATIONS.values())
    assert (PROJECT_ROOT / "packages" / "python").is_dir()
    assert (PROJECT_ROOT / "packages" / "typescript").is_dir()

    node_workspace = read_json(PROJECT_ROOT / "package.json")
    python_workspace = read_toml(PROJECT_ROOT / "pyproject.toml")

    assert node_workspace["workspaces"] == ["apps/web"]
    tools = python_workspace["tool"]
    assert isinstance(tools, dict)
    uv = tools["uv"]
    assert isinstance(uv, dict)
    assert uv["workspace"] == {"members": ["apps/api", "apps/worker"]}


def test_runtime_and_package_manager_versions_are_pinned() -> None:
    root_package = read_json(PROJECT_ROOT / "package.json")
    node_version = (PROJECT_ROOT / ".node-version").read_text(encoding="utf-8").strip()
    python_version = (
        (PROJECT_ROOT / ".python-version").read_text(encoding="utf-8").strip()
    )

    assert re.fullmatch(r"22\.\d+\.\d+", node_version)
    assert root_package["packageManager"] == "npm@10.9.8"
    assert root_package["engines"] == {
        "node": ">=22.13.0 <23",
        "npm": ">=10.9.0 <11",
    }
    npm_config = (PROJECT_ROOT / ".npmrc").read_text(encoding="utf-8")
    assert npm_config.strip().splitlines() == ["engine-strict=true", "save-exact=true"]
    assert python_version == "3.13"

    for app in ("api", "worker"):
        manifest = read_toml(APPLICATIONS[app] / "pyproject.toml")
        project = manifest["project"]
        assert isinstance(project, dict)
        assert project["requires-python"] == ">=3.13,<3.14"


def test_python_applications_do_not_import_each_other() -> None:
    violations: list[str] = []
    for app, forbidden_modules in PYTHON_APP_MODULES.items():
        for path in APPLICATIONS[app].rglob("*.py"):
            for module in imported_python_modules(path):
                if any(
                    module == forbidden or module.startswith(f"{forbidden}.")
                    for forbidden in forbidden_modules
                ):
                    violations.append(
                        f"{path.relative_to(PROJECT_ROOT)} imports {module}"
                    )

    assert violations == []


def test_web_does_not_import_backend_applications() -> None:
    violations: list[str] = []
    for pattern in ("*.js", "*.jsx", "*.ts", "*.tsx", "*.mjs"):
        for path in APPLICATIONS["web"].rglob(pattern):
            if TYPESCRIPT_CROSS_APP_IMPORT.search(path.read_text(encoding="utf-8")):
                violations.append(str(path.relative_to(PROJECT_ROOT)))

    assert violations == []
