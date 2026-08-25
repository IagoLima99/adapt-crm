---
status: accepted
---

# API sem estado autoritativo em memória

A API não mantém estado autoritativo de sessão, negócio ou job em memória. Estado durável pertence ao PostgreSQL, Temporal ou storage externo; pools e caches locais são permitidos apenas quando descartáveis e reconstruíveis. Reiniciar uma réplica não pode alterar comportamento nem perder trabalho confirmado, permitindo escalabilidade e recuperação previsíveis.
