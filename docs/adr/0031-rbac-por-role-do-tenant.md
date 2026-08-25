---
status: accepted
---

# RBAC por Role do Tenant

Permissions seguem `<module>.<resource>.<action>`, são agrupadas em Roles pertencentes ao Tenant e chegam ao User por Memberships. O modelo é default deny e usa apenas concessões positivas; Roles padrão são copiadas no provisionamento e podem ser adaptadas. RBAC complementa, mas nunca substitui, Module Entitlement e Module Activation.
