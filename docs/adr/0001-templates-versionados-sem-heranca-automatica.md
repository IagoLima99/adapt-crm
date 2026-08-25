---
status: accepted
---

# Templates versionados sem herança automática

Um Template é um blueprint versionado aplicado para inicializar a configuração de um Tenant. Depois do provisionamento, o Tenant mantém configuração independente; novas versões do Template só são aplicadas por upgrade explícito, auditável e reversível. Essa decisão evita mudanças silenciosas em ambientes ativos e preserva autonomia, ao custo de exigir um processo de migração entre versões.

## Considered Options

- Herança contínua foi rejeitada porque alterações globais poderiam conflitar com customizações locais e modificar Tenants sem consentimento.
- Variantes ou forks por Tenant foram rejeitados porque fragmentariam o produto e inviabilizariam evolução uniforme.

## Consequences

- A origem e a versão do Template precisam permanecer identificáveis.
- Upgrades de Template devem declarar mudanças, validar compatibilidade e permitir rollback.
- Customizações de um Tenant não alteram o Template de origem nem outros Tenants.
