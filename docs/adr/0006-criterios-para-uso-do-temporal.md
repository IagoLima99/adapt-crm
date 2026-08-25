---
status: accepted
---

# Critérios para uso do Temporal

Temporal será usado quando um processo precisar sobreviver a reinícios ou coordenar espera durável, agendamento ou recorrência, múltiplas etapas externas, retries persistentes, intervenção humana ou compensação. Operações atômicas permanecem em transações locais, e tarefas curtas, idempotentes e reconstruíveis podem usar execução simples. A duração isolada não determina a escolha; durabilidade e coordenação determinam.

## Workflow e Activity

- Workflow contém somente orquestração determinística e replay-safe. I/O, acesso a database, rede, filesystem, relógio ou aleatoriedade não determinísticos são proibidos no Workflow e pertencem a Activities.
- Activity encapsula efeitos externos, deve ser idempotente e possuir timeout explícito. Activity longa emite heartbeat para permitir detecção de falha e cancelamento.
- Retry de Activity é declarado por política, com backoff, limite temporal ou de tentativas e classificação explícita de erros não retryable. Workflow não usa retry como substituto para corrigir falha determinística.
- Timers duráveis substituem sleeps de processo e cron ad hoc quando fazem parte do estado do fluxo.
- Mudanças em Workflow precisam preservar replay ou usar estratégia de versionamento compatível.

## Exemplos

- Follow-up para daqui a sete dias: Workflow aguarda timer durável e executa Activity idempotente de notificação.
- Recorrência mensal com estado, retries e cancelamento: Workflow durável.
- Uma transação PostgreSQL que cria um Customer: operação local, sem Temporal.
- Recalcular uma projeção reconstruível e curta: tarefa simples, sem Workflow durável.
- Uma única chamada externa isolada: Activity standalone ou adapter com retry delimitado; não exige Workflow apenas por ser assíncrona.

## Consequences

O Worker permanece separado da API, Activities são testadas como efeitos idempotentes e Workflows recebem testes de replay, timers e falhas. O ganho de durabilidade vem com custo operacional e disciplina de determinismo, por isso Temporal não é o executor padrão de toda tarefa em background.
