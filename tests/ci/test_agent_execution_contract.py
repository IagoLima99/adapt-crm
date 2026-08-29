from __future__ import annotations

from pathlib import Path

from scripts.repo import build_parser


PROJECT_ROOT = Path(__file__).parents[2]
CONTRACT_PATH = PROJECT_ROOT / "docs" / "agents" / "execution-contract.md"


def test_agent_contract_routes_to_authoritative_sources_and_public_commands() -> None:
    agents = (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    contract = CONTRACT_PATH.read_text(encoding="utf-8")

    assert "docs/agents/execution-contract.md" in agents
    assert "EL-124" in contract
    assert "scripts/repo.py" in contract
    assert "README.md" in contract
    for command in ("install", "dev", "test", "lint", "build", "smoke"):
        assert f"`{command}`" in contract
        assert build_parser().parse_args([command]).task == command


def test_agent_contract_covers_readiness_labels_and_preflight_scenarios() -> None:
    contract = CONTRACT_PATH.read_text(encoding="utf-8")

    for label in ("validado", "agent-ready", "spec-gap", "evidence-pending"):
        assert f"`{label}`" in contract
    assert "READY: YES" in contract
    assert "READY: NO" in contract
    assert "encerre sem editar código ou documentação" in contract
    assert "Não selecione automaticamente" in contract
    assert "issue com `agent-ready`, DoR completa, blockers concluídos e fase liberada" in contract
    assert "issue somente `validado`, com definição ausente, blocker aberto ou fase não" in contract


def test_agent_contract_keeps_navigation_and_validation_scope_explicit() -> None:
    contract = CONTRACT_PATH.read_text(encoding="utf-8")

    for path in (
        "apps/api",
        "apps/web",
        "apps/worker",
        "tests/ci",
        ".github/workflows/ci.yml",
    ):
        assert path in contract
    assert "STOP-01" in contract and "STOP-08" in contract
    assert "git status" in contract and "git diff" in contract
    assert "testes focados" in contract
    assert "suíte completa" in contract
