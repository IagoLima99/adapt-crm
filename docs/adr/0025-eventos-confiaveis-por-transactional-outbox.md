---
status: accepted
---

# Eventos confiáveis por transactional outbox

Todo evento cross-module ou externo é persistido em transactional outbox no mesmo commit da mudança proprietária. A entrega oferece semântica `at-least-once`, e consumidores devem ser idempotentes; o sistema não promete `exactly-once`. Essa escolha evita perda entre commit e publicação, aceitando possíveis duplicatas.

