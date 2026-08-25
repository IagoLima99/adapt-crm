---
status: accepted
---

# Lifecycle explícito de Module Activation

Module Activation segue `inactive`, `activating`, `active`, `deactivating` e `failed`; somente `active` aceita comandos. Perda de Entitlement bloqueia novos comandos e inicia desativação segura. Falhas mantêm o Module indisponível e recuperável, preservando dados e evitando estados parcialmente ativos.

