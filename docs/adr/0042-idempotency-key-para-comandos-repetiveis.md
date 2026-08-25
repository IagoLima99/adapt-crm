---
status: accepted
---

# Idempotency-Key para comandos repetíveis

Comandos POST relevantes aceitam `Idempotency-Key` escopada por operação e Actor; depois que existe TenantContext, o Tenant também compõe o escopo. Provisioning usa escopo de plataforma antes da criação e vincula o registro idempotente ao Tenant criado. A mesma chave com o mesmo payload retorna o resultado original; reutilização com payload diferente retorna conflito.
