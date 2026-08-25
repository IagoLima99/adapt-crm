---
status: accepted
---

# Sessões internas com autorização revalidada

Access tokens curtos identificam User, Identity e sessão, mas não carregam Permissions autoritativas; Membership, status do Tenant e RBAC são revalidados no backend. Refresh tokens são rotativos, armazenados como hash e revogáveis. Navegadores usam cookies `HttpOnly`, `Secure` e `SameSite`, e tokens OIDC são trocados por sessão interna.

