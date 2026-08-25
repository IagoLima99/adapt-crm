---
status: accepted
---

# Migrations por expand-and-contract

Mudanças destrutivas de schema usam expand-and-contract: adicionar estrutura compatível, migrar dados, publicar aplicação compatível e remover estrutura apenas em release posterior após validação operacional e backup. Rollback normal reverte a aplicação, não o schema; restauração de banco é mecanismo de desastre. A abordagem aumenta o número de etapas para reduzir indisponibilidade e risco de perda de dados.

