---
status: accepted
---

# Erros por Problem Details

Respostas de erro usam `application/problem+json` com `type`, `title`, `status`, `detail`, `instance`, código estável da aplicação, `correlation_id` e erros de campo quando aplicável. Stack traces e detalhes internos nunca são expostos. O contrato uniforme permite tratamento consistente por UI, integrações e observabilidade.

