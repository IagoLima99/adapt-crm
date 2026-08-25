---
status: accepted
---

# Configuração de processo e Tenant separadas

Configuração não sensível do processo vem de variáveis de ambiente tipadas e validadas no startup; `.env` é exclusivo do desenvolvimento. Configuração de Tenant pertence ao Platform Access e fica no database. Endpoints de database e storage são fornecidos externamente por profile, incluindo `DATABASE_URL`, sem recompilar o artefato. Ausência de configuração obrigatória impede startup seguro.
