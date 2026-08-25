---
status: accepted
---

# Tenant independente de Deployment

Tenant é um limite lógico de negócio, não uma implantação física. Um Deployment pode hospedar um ou vários Tenants conforme seu profile, e um Tenant pode mudar de profile sem mudar de identidade. Essa separação permite evolução operacional sem contaminar o domínio, ao custo de exigir mecanismos de migração e isolamento consistentes entre profiles.

