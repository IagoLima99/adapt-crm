---
status: accepted
---

# RLS vinculado ao TenantContext transacional

Toda transação no modo shared executa `SET LOCAL app.tenant_id` antes de acessar dados tenant-owned. A role normal da aplicação não pode ignorar RLS, e pooling deve limpar contexto entre transações. Operações administrativas usam role, conexão e serviço separados, sempre auditados, reduzindo risco de vazamento por reutilização de conexão.

