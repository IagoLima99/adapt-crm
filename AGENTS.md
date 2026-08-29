## Agent skills

### Issue tracker

Issues são gerenciadas no Jira, projeto Equipe Lua (`EL`), via MCP Atlassian. Consulte `docs/agents/issue-tracker.md`.

### Triage labels

Usamos os cinco labels canônicos de triagem. Consulte `docs/agents/triage-labels.md`.

### Domain docs

Este repositório usa documentação de domínio single-context. Consulte `docs/agents/domain.md`.

### Escopo de entrega

Implemente somente comportamento, opções CLI, arquivos e documentação solicitados
pelo ticket ou comprovadamente necessários para um critério de aceite. Trate
ergonomias, flags, automações e documentação adicionais como expansão de escopo e
peça direção antes de adicioná-las.

### Validação local

A CI é a autoridade para os gates completos do projeto. No desenvolvimento local,
execute apenas validações focadas diretamente necessárias para a alteração; deixe a
suíte completa, lint global, typecheck global, build e demais gates canônicos para a
CI.
