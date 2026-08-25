---
status: accepted
---

# Isolamento PostgreSQL por Isolation Mode

O modo `shared` usa database e schema compartilhados com `tenant_id`, scoping centralizado e RLS. O modo `dedicated` usa database exclusivo, mas preserva `tenant_id` e o mesmo schema para permitir portabilidade. Schema por Tenant não será suportado. Produção com organizações não relacionadas só poderá operar em `shared` depois que RLS e sua suíte de isolamento estiverem ativos.

## Considered Options

- Somente filtros na aplicação foram rejeitados por não oferecerem defesa em profundidade contra falhas de scoping.
- Schema por Tenant foi rejeitado pela complexidade de migrations, pooling e operação em escala.
- Database dedicado para todo Tenant foi rejeitado como única modalidade por elevar custo e limitar o modo shared.

## Consequences

Todas as entidades tenant-owned carregam `tenant_id`, inclusive no modo dedicated. Policies, pooling e caminhos administrativos exigem testes negativos próprios, e shared permanece indisponível em produção até esse gate estar verde.
