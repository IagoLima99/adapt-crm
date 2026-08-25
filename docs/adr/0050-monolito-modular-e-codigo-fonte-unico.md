---
status: accepted
---

# Monólito modular e código-fonte único

AdaptCRM evolui como monólito modular em um único repositório e uma única linha de produto, sem forks por Tenant. Web, API e worker podem gerar artefatos distintos da mesma revisão, mas Modules não são microservices nem se comunicam por rede internamente. Extração de serviço só será considerada quando houver contrato estável e evidência de necessidade independente de escala, disponibilidade, segurança ou ownership operacional.

