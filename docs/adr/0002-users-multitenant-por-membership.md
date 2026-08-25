---
status: accepted
---

# Users multitenant por Membership

Um User pode operar em vários Tenants por meio de Memberships independentes. Roles pertencem ao Tenant e são atribuídas à Membership, que determina a autorização efetiva; cada operação ocorre sob um TenantContext explícito. Isso evita duplicar identidades e impede que autorizações sejam acumuladas ou reutilizadas entre Tenants, ao custo de exigir seleção e validação rigorosa de contexto.
