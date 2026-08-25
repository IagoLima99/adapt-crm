---
status: accepted
---

# Upgrade de Template por diff de três vias

Upgrades comparam a versão originalmente aplicada, a nova versão e a configuração atual do Tenant. O plano classifica adições seguras, customizações locais, conflitos e mudanças destrutivas; um administrador resolve conflitos e confirma antes da aplicação. Um snapshot anterior permite rollback da configuração, impedindo que upgrades sobrescrevam silenciosamente decisões do Tenant.

