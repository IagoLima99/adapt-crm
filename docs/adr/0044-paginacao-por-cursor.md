---
status: accepted
---

# Paginação por cursor

APIs de negócio usam cursor opaco, ordenação estável e limite máximo. Offset é permitido apenas em consultas administrativas pequenas e explicitamente limitadas. Nenhum endpoint retorna coleção potencialmente ilimitada, preservando estabilidade sob mutações e crescimento de volume.
