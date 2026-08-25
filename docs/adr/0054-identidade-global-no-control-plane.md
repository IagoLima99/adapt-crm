---
status: accepted
---

# Identidade global no control plane

User, Identity, Tenant, Membership, Role, Entitlement e Activation pertencem logicamente ao control plane. Em Local e shared, control plane e dados de negócio podem compartilhar a mesma infraestrutura PostgreSQL; no modo dedicated, dados tenant-owned dos Modules podem residir em database exclusivo enquanto identidade e roteamento permanecem no control plane. Cada instalação self-hosted possui seu próprio namespace de identidade, portanto User é global somente dentro do mesmo control plane.

## Considered Options

- Duplicar User em cada database dedicated foi rejeitado por quebrar Membership multitenant e tornar migrações de profile dependentes de reconciliação de identidade.
- Compartilhar todos os dados de negócio em um único database foi rejeitado porque impediria isolamento dedicated real.

## Consequences

Platform Access precisa separar contratos de control plane e dados tenant-owned desde o início, ainda que ambos usem a mesma instância local. Roteamento de conexão por Tenant torna-se responsabilidade explícita da persistência.
