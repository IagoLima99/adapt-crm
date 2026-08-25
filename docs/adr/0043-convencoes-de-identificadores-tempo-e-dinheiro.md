---
status: accepted
---

# Convenções de identificadores, tempo e dinheiro

Entidades de domínio expostas usam UUIDv7 armazenado como `uuid`, sem sequências públicas. Timestamps são timezone-aware em UTC e persistidos como `timestamptz`; APIs usam ISO 8601. Valores monetários combinam decimal e código ISO da moeda, nunca ponto flutuante, evitando exposição de cardinalidade e inconsistência numérica.

