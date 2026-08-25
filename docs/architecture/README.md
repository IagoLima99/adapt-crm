# Arquitetura do AdaptCRM

Este diretório orienta a implementação da fundação. O vocabulário canônico está em [`CONTEXT.md`](../../CONTEXT.md), e o índice das decisões aceitas está em [`docs/adr/README.md`](../adr/README.md).

## Relação com o Jira

O Jira permanece a fonte de verdade para sequência, dependências, status e evidências de execução. Aceitar um ADR não conclui nem movimenta automaticamente uma issue.

- PostgreSQL e migrations: ADRs 0013, 0016, 0034 e 0051.

## Evidências dos tickets arquiteturais

| Ticket | Contrato verificável | Evidências aceitas |
| --- | --- | --- |
| `EL-28` | Catálogo e grafo acíclico de Modules, contratos cross-module, Shared Kernel mínimo, transação restrita ao Module proprietário, outbox, projeções e versionamento único | ADRs 0004, 0017, 0019–0021, 0024–0027 e 0050 |
| `EL-86` | TenantContext derivado de rota e Membership, identidade no control plane, lifecycles, RBAC, RLS transacional, isolamento por Isolation Mode e administração cross-tenant auditada | ADRs 0002, 0005, 0009–0010, 0016, 0030–0039 e 0054 |
| `EL-87` | Dimensões de Deployment, API stateless, responsabilidades operacionais, configuração, secrets, storage, retenção, baseline managed e evolução de Runtime | ADRs 0012, 0014, 0018, 0045–0049 e 0053 |
| `EL-88` | Critério entre request síncrona, transação local, job curto e Workflow Temporal; determinismo, Activities, retries, timers, outbox e provisionamento | ADRs 0006, 0025, 0029 e 0052 |

Os quatro conjuntos foram revisados contra o vocabulário canônico. A automação desta verificação pertence a `EL-268`, bloqueada por `EL-31`.

## Restrições centrais

- Um código-fonte e uma versão do produto; nenhum fork por Tenant.
- Modules são limites de capacidade, regras e ownership de dados dentro de um monólito modular.
- Tenant é independente do Deployment e de seu Runtime.
- Shared production exige RLS validado; antes desse gate, produção opera em dedicated.
- Templates são declarativos, versionados e nunca concedem Entitlements.
- Temporal é reservado a coordenação durável; transações locais permanecem no PostgreSQL.
- Configuração, secrets, database e storage são externalizados por profile.

## Pendências deliberadas

- A matriz quantitativa de deployment, custos e responsabilidades pertence a `EL-14`.
- NFRs e gates de saída completos pertencem a `EL-44`.
- As issues arquiteturais continuam no status atual do Jira até que evidências e critérios de aceite sejam verificados.
