# Documentação de domínio

Este repositório usa o layout single-context.

## Antes de explorar o código

Leia, quando existirem:

- `CONTEXT.md`, na raiz;
- ADRs relevantes em `docs/adr/`.

Se esses arquivos ainda não existirem, prossiga silenciosamente. A skill de modelagem de domínio deve criá-los quando termos ou decisões forem efetivamente definidos.

## Estrutura

```text
/
├── CONTEXT.md
├── docs/
│   └── adr/
└── apps/
    ├── web/
    ├── api/
    └── worker/
```

## Vocabulário

Ao nomear conceitos de domínio em código, testes, issues ou propostas, use os termos definidos no glossário de `CONTEXT.md`.

Evite introduzir sinônimos para conceitos já definidos. Conceitos ausentes devem ser avaliados pela skill de modelagem de domínio.

## Conflitos com ADRs

Se uma proposta contrariar um ADR existente, sinalize explicitamente o conflito. Não substitua silenciosamente uma decisão arquitetural registrada.
