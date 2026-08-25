---
status: accepted
---

# Lifecycle de Membership

Membership segue `invited → active ↔ suspended → revoked`. Convites expiram, são de uso único e vinculados ao Tenant e a email verificado. Suspensão é reversível; revogação é terminal, e uma reentrada cria nova Membership para preservar histórico.

