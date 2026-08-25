---
status: accepted
---

# User com múltiplas Identities

User representa a pessoa global, enquanto cada credencial é uma Identity identificada por `provider + subject`. Um User pode vincular Identities local e OIDC explicitamente; email verificado auxilia convites e recuperação, mas não realiza merge automático. Membership permanece independente do mecanismo de autenticação.
