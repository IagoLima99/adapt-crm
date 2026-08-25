---
status: accepted
---

# API REST versionada e OpenAPI autoritativo

APIs públicas usam `/api/v1`; mudanças aditivas permanecem na versão e incompatibilidades exigem nova major com transição. OpenAPI gerado pelo backend é a fonte de verdade, e consumidores internos usam clients ou types gerados. A decisão reduz drift de contratos ao custo de disciplinar compatibilidade e geração de artefatos.

