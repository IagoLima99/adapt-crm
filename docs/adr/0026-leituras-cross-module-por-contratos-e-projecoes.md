---
status: accepted
---

# Leituras cross-module por contratos e projeções

Composições simples consultam query services públicos dos Modules. Busca, timeline, relatórios e paginação cross-module usam read models ou projeções que podem duplicar dados, mas nunca são fonte de verdade. Joins diretos em tabelas de outro Module são proibidos para preservar ownership e permitir evolução independente dos modelos de escrita.

