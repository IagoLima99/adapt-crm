# Contrato de execução do agente

Este é o contrato operacional enxuto do repositório. O Jira EL-124 é a fonte
oficial de DoR, DoD, labels e Stop Conditions; este documento explica como
aplicá-lo sem copiar sua política.

## Ordem mínima de leitura

1. `git status` e `git diff` para preservar o estado real do working tree.
2. EL-124 e a issue atual no Jira.
3. Parent e blockers estruturados da issue atual.
4. Documentos em `docs/agents/` explicitamente referenciados pela issue.
5. Comandos públicos do bootstrap em `scripts/repo.py` e `README.md`.
6. Somente os paths/componentes autorizados e necessários à issue.

Não carregue o backlog, todos os ADRs ou a arquitetura inteira para uma task
comum. Se a solução já existir no working tree, retome-a pelo diff e preserve-a;
não reexplore nem reconstrua o trabalho.

## Readiness e labels

`validado` significa especificação revisada e não autoriza implementação.
`agent-ready` significa DoR satisfeita e implementação autorizada.
`spec-gap` significa definição necessária ausente ou ambígua.
`evidence-pending` significa implementação concluída, mas evidência final incompleta.

Antes de editar qualquer arquivo, declare `READY: YES` somente quando a issue
estiver `agent-ready`, a DoR do EL-124 estiver completa, os blockers estiverem
concluídos e a fase estiver liberada. Caso contrário, declare `READY: NO`, liste
os gaps objetivos e encerre sem editar código ou documentação.

## Execução

- Implemente somente o escopo da issue e os critérios de aceite verificáveis.
- Use testes focados durante Implement; deixe suíte completa, lint global,
  typecheck global, build e demais gates canônicos para a validação final na CI.
- Use os comandos públicos do EL-94 como fonte de verdade: `install`, `dev`,
  `test`, `lint`, `build` e `smoke`, definidos em `scripts/repo.py` e descritos
  no `README.md`.
- Selecione trabalho apenas por fase liberada, blockers concluídos e
  `agent-ready`; entre candidatos elegíveis, respeite a prioridade e a sequência
  explícita no parent.
- Ao concluir uma task, encerre no handoff dela. Não selecione automaticamente
  nem implemente outro PBI.

## Stop Conditions

Aplique integralmente as `STOP-01` a `STOP-08` do EL-124. Pare e registre
`SPEC_GAP` ou `BLOCKED` quando uma decisão de segurança, contrato público,
persistência, tenancy, deploy ou arquitetura não estiver fechada; quando o path
estiver fora do escopo; quando um gate baseline falhar; quando não houver prova
objetiva; quando faltar dependência externa autorizada; ou quando a complexidade
deixar de caber na issue.

## Evidência e retomada

Registre issue, commit, arquivos alterados, validações, resultados e riscos
residuais. Mapeie cada critério de aceite para uma evidência verificável e só
remova `evidence-pending` quando o conjunto estiver completo.

Na retomada, repita apenas `git status` + `git diff`, leia o handoff/Execution
Packet da issue e continue dos gaps existentes. Não repita discovery encerrado.

## Navegação rápida

- Governança: `AGENTS.md`, este contrato e Jira EL-124.
- Bootstrap/comandos: `scripts/repo.py`, `README.md`, `.env.example`.
- Aplicações: `apps/api`, `apps/web`, `apps/worker`.
- Conformance e testes de CI: `scripts/check_architecture.py`, `tests/ci` e
  `.github/workflows/ci.yml`.

## Cenários de preflight

- A: issue com `agent-ready`, DoR completa, blockers concluídos e fase liberada →
  `READY: YES`; implementar conforme o escopo.
- B: issue somente `validado`, com definição ausente, blocker aberto ou fase não
  liberada → `READY: NO`; registrar o gap e não implementar.
