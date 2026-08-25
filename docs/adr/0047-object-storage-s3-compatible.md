---
status: accepted
---

# Object storage S3-compatible

Anexos usam contrato S3-compatible; filesystem local é permitido somente em desenvolvimento. Objetos são isolados por Tenant e Module, e metadata e ownership permanecem no Module proprietário. Uploads aplicam limites, validação de tipo e quarentena; downloads exigem autorização e URL temporária, sem bucket público.

