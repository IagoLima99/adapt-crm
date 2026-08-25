# Responsabilidades por dimensões de Deployment

Este documento implementa `EL-90`. As três dimensões abaixo são ortogonais: escolher um Operations Mode não altera Isolation Mode ou Runtime, e nenhuma combinação cria variante do produto.

## Dimensões

| Dimensão | Valores | Decide | Não decide |
| --- | --- | --- | --- |
| Isolation Mode | `shared`, `dedicated` | Isolamento e topologia da persistência tenant-owned | Quem opera ou qual orquestrador executa o produto |
| Operations Mode | `managed`, `self-hosted` | Responsabilidade por infraestrutura e operação | Regras de domínio, schema ou mecanismo de isolamento |
| Runtime | `local`, `VPS/Compose`, `Kubernetes` | Empacotamento e orquestração dos processos | Responsabilidade comercial ou ownership dos dados |

## Operations Mode

| Responsabilidade | Managed | Self-hosted | Entrega permanente do produto |
| --- | --- | --- | --- |
| Host, rede e sistema operacional | Operador AdaptCRM | Organização operadora | Requisitos mínimos e runbook vendor-neutral |
| PostgreSQL e pooling | Operador AdaptCRM | Organização operadora | Migrations, compatibilidade, health e diagnóstico |
| Object storage | Operador AdaptCRM | Organização operadora | Contrato S3-compatible, validações e documentação |
| Secrets e rotação | Operador AdaptCRM | Organização operadora | Interface de provider e lista de secrets requeridos |
| DNS e TLS | Operador AdaptCRM | Organização operadora | Requisitos de hostname, HTTPS e renovação segura |
| Backup, PITR e restore drill | Operador AdaptCRM | Organização operadora | Procedimento, compatibilidade e validação da aplicação |
| Logs, métricas, traces e alertas | Operador AdaptCRM | Organização operadora | Sinais emitidos, dashboards de referência e diagnóstico |
| Deploy e rollback de artefato | Operador AdaptCRM | Organização operadora | OCI imutável, SemVer, commit SHA, migrations e release notes |
| Patches de infraestrutura | Operador AdaptCRM | Organização operadora | Matriz de versões suportadas e avisos de segurança |
| Incidente de infraestrutura | Operador AdaptCRM como responsável primário | Organização operadora como responsável primário | Suporte de produto e análise de defeito reproduzível |
| Incidente de produto | Operador AdaptCRM coordena operação e engenharia | Organização opera; produto fornece correção e orientação | Correção, advisory, diagnóstico e artefato versionado |

No modo self-hosted, suporte não possui acesso permanente ao host, database, storage ou secrets. Acesso excepcional deve ser solicitado pela organização, ter escopo e prazo definidos, usar menor privilégio, produzir auditoria e ser revogado ao final.

## Isolation Mode

| Aspecto | Shared | Dedicated |
| --- | --- | --- |
| Dados tenant-owned | Database e schema compartilhados, sempre com `tenant_id` | Database exclusivo, preservando `tenant_id` e o mesmo schema |
| Defesa de isolamento | TenantContext transacional, scoping centralizado e RLS | Roteamento para database exclusivo mais TenantContext e scoping |
| Produção | Condicionada ao gate verde de RLS e testes negativos | Referência inicial para produção antes do gate shared |
| Control plane | Pode compartilhar a infraestrutura PostgreSQL | Pode permanecer central enquanto dados dos Modules usam database exclusivo |
| Migrations | Uma linha de schema versionada para todos os Tenants | A mesma migration aplicada de forma controlada a cada database |
| Backup e restore | Restore global; recuperação seletiva exige procedimento próprio | Backup e restore podem ser isolados por database do Tenant |
| Custo relativo | Menor custo unitário, maior exigência de isolamento | Maior custo e operação, maior isolamento de infraestrutura |

Isolation Mode nunca transfere ownership das entidades entre Modules e não altera regras de domínio.

## Runtime

| Runtime | Requisitos | Uso previsto | Limites |
| --- | --- | --- | --- |
| Local | Configuração local, dependências reproduzíveis e dados descartáveis; Compose quando útil | Desenvolvimento e testes | Não é ambiente produtivo nem referência de durabilidade |
| VPS/Compose | Mesmos artefatos OCI, configuração e secrets externos, volumes/storage persistentes, health checks, backup e rollback | Primeira operação managed ou self-hosted | Escala e HA exigem procedimentos explícitos; não simula Kubernetes |
| Kubernetes | Artefatos OCI idênticos, probes, shutdown gracioso, múltiplas réplicas, secret provider e persistência externa | Futuro, após gate baseado em evidência | Não é mantido antecipadamente; cluster não substitui database, backup ou observabilidade |

Runtime não redefine quem responde por TLS, backup, upgrades ou incidentes; essas responsabilidades continuam derivadas do Operations Mode.

## Configurações de referência

Os estados abaixo indicam direção arquitetural, não disponibilidade comercial atual.

| Referência | Isolation | Operations | Runtime | Estado | Observação |
| --- | --- | --- | --- | --- | --- |
| Desenvolvimento local | `shared` lógico | Não aplicável; responsabilidade do desenvolvedor | `local` | Fundação | Pode usar infraestrutura única e dados descartáveis |
| Produção managed inicial | `dedicated` | `managed` | `VPS/Compose` | Alvo inicial | Evita shared antes do gate de RLS e não exige Kubernetes |
| Managed compartilhado | `shared` | `managed` | `VPS/Compose` | Condicional | Permitido somente após RLS e testes negativos verdes |
| Self-hosted inicial | `dedicated` | `self-hosted` | `VPS/Compose` | Alvo | Organização opera infraestrutura com artefatos e runbooks do produto |
| Self-hosted compartilhado | `shared` | `self-hosted` | `VPS/Compose` | Condicional | Operador assume o isolamento; requer o mesmo gate de RLS |
| Managed com Kubernetes | `shared` ou `dedicated` | `managed` | `Kubernetes` | Futuro | Depende dos gatilhos de capacidade, HA e automação |
| Self-hosted com Kubernetes | `shared` ou `dedicated` | `self-hosted` | `Kubernetes` | Futuro | Produto não opera o cluster nem recebe secrets permanentes |

## Contrato comum a todas as combinações

- Um único código-fonte, uma versão do produto e as mesmas regras de domínio.
- Artefatos OCI imutáveis identificados por SemVer e commit SHA.
- Configuração de processo fornecida externamente; configuração de Tenant permanece no Platform Access.
- Secrets vêm de provider externo e nunca entram em logs, Templates, auditoria ou respostas de API.
- PostgreSQL usa o mesmo schema lógico; `tenant_id` permanece nos registros tenant-owned inclusive em dedicated.
- Storage produtivo é externo e S3-compatible; filesystem do container não é persistência de negócio.
- Migrations, backup, restore, observabilidade, health checks e rollback têm responsáveis explícitos.
- O contrato é vendor-neutral: nenhum fornecedor cloud, registry, database gerenciado ou secret store é obrigatório.

## Rastreabilidade

- ADR-0012 — Deployment em dimensões ortogonais.
- ADR-0016 — isolamento PostgreSQL por Isolation Mode.
- ADR-0018 — responsabilidades managed e self-hosted.
- ADR-0045 — configuração de processo e Tenant separadas.
- ADR-0046 — secrets por provider externo.
- ADR-0047 — object storage S3-compatible.
- ADR-0054 — identidade global no control plane.
- `EL-29` — consolidação das combinações e capacidade.
