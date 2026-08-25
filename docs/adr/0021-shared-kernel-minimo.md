---
status: accepted
---

# Shared Kernel mínimo

O Shared Kernel contém apenas primitivas estáveis: identificadores tipados, TenantContext, ActorContext, clock, contratos de transação e envelope de eventos. Entidades, regras de negócio, ORM models e DTOs específicos permanecem no Module proprietário. A restrição reduz duplicação técnica sem criar ownership compartilhado de domínio.

