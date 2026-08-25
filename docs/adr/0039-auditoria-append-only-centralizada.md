---
status: accepted
---

# Auditoria append-only centralizada

Platform Access possui o audit log append-only, e cada Module publica eventos com Tenant, Actor, ação, alvo, resultado, timestamp, correlation ID e motivo quando exigido. Secrets, tokens e snapshots completos de dados sensíveis não são registrados. A centralização oferece trilha uniforme sem transferir ownership das ações de negócio.
