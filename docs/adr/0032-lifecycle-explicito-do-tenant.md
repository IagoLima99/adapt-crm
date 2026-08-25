---
status: accepted
---

# Lifecycle explícito do Tenant

Tenant segue `provisioning → active ↔ suspended → deprovisioning → deleted`, sendo `deleted` terminal. Suspensão bloqueia operações normais e novas execuções sem remover dados; deprovisioning permite exportação e aplica retenção antes da purga. A API comum não oferece hard delete direto.

