---
status: accepted
---

# Transações gravam um único Module

Cada transação altera dados pertencentes a apenas um Module. Chamadas síncronas a outros Modules são limitadas a consultas ou validações por contrato público; mudanças coordenadas usam outbox e eventos ou Temporal quando exigem durabilidade. A restrição troca atomicidade cross-module por ownership explícito e evolução independente.

