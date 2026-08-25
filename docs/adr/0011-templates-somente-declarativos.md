---
status: accepted
---

# Templates são somente declarativos

Templates contêm apenas configuração declarativa versionada, como Modules desejados, custom fields, pipelines, defaults de papéis e permissões e referências a automações suportadas. Código executável, SQL, secrets, dados de Tenant, imagens e branches específicas são proibidos. Aplicações e upgrades devem ser validados, idempotentes e precedidos por diff, reduzindo flexibilidade arbitrária para preservar segurança e evolução uniforme.

