---
status: accepted
---

# Comunicação por contratos de Module

Cada Module escreve somente em suas próprias tabelas por seus repositories. Interações síncronas cross-module por application services públicos são limitadas a consultas e validações; comandos que coordenam mudanças usam eventos após commit ou Temporal quando duráveis. Imports de ORM models, repositories ou serviços internos de outro Module são proibidos.
