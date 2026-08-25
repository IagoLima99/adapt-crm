---
status: accepted
---

# Retenção e purge por workflow

Cada Module define archival e purge de suas entidades dentro das restrições da plataforma. Exclusão definitiva é workflow assíncrono, idempotente e auditado, com plano de dependências e período de retenção configurável. Audit logs preservam evidência mínima sem PII desnecessária, e backups expiram por política própria documentada ao Tenant.
