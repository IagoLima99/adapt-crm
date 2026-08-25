# Contrato do monorepo

Este documento implementa o contrato estrutural de `EL-30`. O repositório contém um único produto versionado, com aplicações implantáveis separadamente e sem dependências diretas entre elas.

## Árvore autorizada

```text
/
├── apps/
│   ├── api/       # processo HTTP Python
│   ├── web/       # aplicação React/TypeScript
│   └── worker/    # processo Python para coordenação assíncrona
├── packages/
│   ├── python/    # bibliotecas técnicas Python explicitamente compartilhadas
│   └── typescript/# bibliotecas técnicas TypeScript explicitamente compartilhadas
├── docs/          # domínio, ADRs, operação e desenvolvimento
├── scripts/       # automação do repositório
└── tests/         # contratos e testes que atravessam o repositório
```

Diretórios de build, caches, ambientes virtuais, dependências instaladas e secrets locais não pertencem à árvore versionada.

## Ownership

| Caminho | Responsabilidade | Pode depender de |
| --- | --- | --- |
| `apps/api` | Bootstrap e processo da API HTTP | Dependências declaradas no próprio `pyproject.toml` e futuros pacotes em `packages/python` |
| `apps/worker` | Bootstrap e processo do worker | Dependências declaradas no próprio `pyproject.toml` e futuros pacotes em `packages/python` |
| `apps/web` | Bootstrap e aplicação web | Dependências declaradas no próprio `package.json` e futuros pacotes em `packages/typescript` |
| `packages/python` | Primitivas técnicas Python estáveis e reutilizáveis | Somente dependências declaradas pelo próprio pacote |
| `packages/typescript` | Primitivas técnicas TypeScript estáveis e reutilizáveis | Somente dependências declaradas pelo próprio pacote |
| `scripts` | Automação local e de CI | Contratos publicados do repositório |
| `tests` | Validação de contratos externos | Interfaces públicas e artefatos publicados |

## Regras de dependência

1. Uma aplicação em `apps/` não importa código-fonte de outra aplicação.
2. Dependências compartilhadas passam por pacote explicitamente versionado em `packages/python` ou `packages/typescript`; não usam caminhos relativos atravessando aplicações.
3. Pacotes compartilhados não possuem capacidade de negócio, dados tenant-owned, regras de Module ou orquestração de infraestrutura.
4. Regras e dados de domínio permanecem no Module proprietário. Um pacote compartilhado não vira atalho para o Shared Kernel crescer sem decisão explícita.
5. Cada dependência externa é declarada no manifesto do consumidor. A raiz coordena workspaces e ferramentas, mas não oculta dependências de Runtime das aplicações.
6. API, web e worker usam a mesma versão do produto, embora possam gerar artefatos de implantação distintos da mesma revisão.
7. Integração em Runtime ocorre por contratos publicados — HTTP, persistência autorizada ou mensageria — e não por import entre processos.

O CI executa `tests/ci/test_monorepo_contract.py` para preservar a árvore, os workspaces, as versões de Runtime e a proibição de imports diretos entre aplicações.

## Gerenciadores e versões

| Ecossistema | Gerenciador | Contrato |
| --- | --- | --- |
| Python | `uv` | Workspace raiz com `apps/api` e `apps/worker`; resolução imutável em `uv.lock`; versão em `.python-version` |
| Node.js | `npm` | Workspace raiz com `apps/web`; resolução imutável em `package-lock.json`; versões em `.node-version` e `packageManager` |

Instalação reproduzível atual:

```shell
uv sync --locked --all-packages --dev
npm ci
```

Os comandos integrados de desenvolvimento e o passo a passo completo de clone limpo pertencem a `EL-94`.

## Fora de escopo deste contrato

- Implementação FastAPI e health endpoint (`EL-91`).
- Aplicação React/Vite e API client (`EL-92`).
- Processo worker e Temporal client (`EL-93`).
- Comandos unificados, env e README de bootstrap (`EL-94`).
- Modules ou regras de negócio.

## Rastreabilidade

- ADR-0019 — grafo de dependências entre Modules.
- ADR-0020 — comunicação por contratos de Module.
- ADR-0021 — Shared Kernel mínimo.
- ADR-0027 — versionamento único do produto.
- ADR-0050 — monólito modular e código-fonte único.
