---
status: accepted
---

# Baseline operacional managed

Serviços emitem logs JSON sem PII ou secrets, traces OpenTelemetry e métricas sem `tenant_id` como label de alta cardinalidade. Liveness verifica o processo e readiness somente dependências críticas do componente. Produção managed usa backup criptografado off-host por no mínimo 30 dias, PostgreSQL com recuperação para um ponto no tempo, RPO de até 15 minutos, RTO de até 4 horas e restore drill trimestral. Imagens OCI são imutáveis e identificadas por SemVer e commit SHA; deploy promove somente instâncias ready, e rollback troca o artefato sem reverter schema. Revisões de capacidade usam saturação sustentada, p95 e backlog, e Kubernetes só é adotado quando múltiplas réplicas, HA e automação operacional justificarem o custo.

