---
status: accepted
---

# Provisionamento de Tenant com Temporal

Provisionamento é um workflow Temporal idempotente que cria o Tenant em `provisioning`, valida Entitlements e Template, cria a Membership administrativa, aplica configuração e somente então promove o Tenant a `active`. Falhas não expõem estado parcialmente ativo, e retries retomam etapas concluídas de forma segura.

