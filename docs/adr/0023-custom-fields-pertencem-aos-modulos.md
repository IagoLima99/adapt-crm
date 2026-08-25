---
status: accepted
---

# Custom Fields pertencem aos Modules

Cada Module possui as definições e os valores de Custom Fields de suas entidades, reutilizando apenas infraestrutura técnica comum. Templates referenciam campos pelo contrato `Module + Entity Type`; não existe um Module central proprietário de todos os campos. Isso preserva ownership e evita acoplamento do Relationships com entidades alheias.
