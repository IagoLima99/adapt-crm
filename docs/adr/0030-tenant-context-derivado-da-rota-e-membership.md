---
status: accepted
---

# TenantContext derivado da rota e Membership

Rotas tenant-scoped carregam o identificador do Tenant no path. O backend combina esse identificador com a identidade autenticada e valida a Membership antes de criar o TenantContext; payloads nunca definem `tenant_id`. Operações de plataforma usam endpoints separados, sem Tenant fictício, reduzindo spoofing e tornando o escopo observável.

