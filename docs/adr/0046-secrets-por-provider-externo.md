---
status: accepted
---

# Secrets por provider externo

A aplicação obtém secrets por uma interface de provider. Desenvolvimento pode usar env ou arquivos locais ignorados, enquanto produção usa secret store externo ou mecanismo equivalente do Runtime. O database guarda apenas referência opaca e metadata de rotação; secrets são proibidos em logs, auditoria, Templates e respostas de API.

