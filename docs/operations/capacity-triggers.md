# Métricas e gatilhos de capacidade

Este documento define os sinais e os gatilhos iniciais para evoluir a capacidade do AdaptCRM. Ele implementa o escopo de `EL-89` e fornece entrada para a matriz consolidada de `EL-29`.

Os valores são guardrails operacionais iniciais, não SLOs comerciais. Os NFRs e gates de fase continuam pertencendo a `EL-44`. Qualquer ajuste exige evidência versionada de teste de carga ou produção e não pode reduzir a margem de segurança sem justificativa.

## Modelo de medição

- Agregar sinais por componente, Runtime e Isolation Mode; `tenant_id` não deve ser label de métrica de alta cardinalidade.
- Calcular CPU, memória, pool e latência em janelas de 5 minutos.
- Considerar saturação sustentada quando o limite ocorrer em três janelas consecutivas, totalizando 15 minutos.
- Excluir janelas explicitamente marcadas de deploy, restore drill ou teste de carga da decisão automática, mantendo-as disponíveis para análise.
- Comparar latência e throughput com o baseline da versão atual sob carga reproduzível.
- Revisar tendência de storage e custo em janela móvel de 30 dias.
- Tratar OOM, corrupção, indisponibilidade de storage e esgotamento de conexões como incidentes imediatos, sem aguardar a janela sustentada.

## Sinais obrigatórios

| Sinal | Medição | Atenção | Ação de capacidade |
| --- | --- | --- | --- |
| CPU | Utilização e throttling por componente | CPU `>= 65%` ou throttling `>= 3%` por 15 min | CPU `>= 75%` ou throttling `>= 5%` por 15 min após eliminar regressão |
| Memória | Working set, limite, crescimento e restarts/OOM | Working set `>= 70%` do limite por 15 min ou crescimento contínuo por 30 min | Working set `>= 80%` por 15 min; qualquer OOM exige correção antes de escalar |
| Pool PostgreSQL | Conexões checked-out, espera p95 e orçamento total | Pool `>= 70%` ou espera p95 `>= 50 ms` por 15 min | Pool `>= 85%`, espera p95 `>= 100 ms` ou projeção acima de `80%` de `max_connections` |
| Latência | p95 por rota/classe de operação, sem `tenant_id` como label | p95 `>= 1,25x` o baseline da versão por 15 min | p95 `>= 1,5x` o baseline ou acima do NFR vigente por 15 min |
| Backlog | Profundidade, taxa de entrada/saída e idade da tarefa pronta mais antiga | Idade p95 ou profundidade cresce por 15 min e consumidores não recuperam o atraso | Idade p95 excede `2x` o objetivo configurado da fila por 15 min ou taxa de saída fica abaixo da entrada |
| Storage | Uso, crescimento diário, IOPS/latência e dias até esgotamento | Uso `>= 70%` ou previsão de esgotamento em menos de 30 dias | Uso `>= 80%`, previsão inferior a 14 dias ou latência de I/O acima do baseline por 15 min |
| Disponibilidade | Readiness, taxa de erro, restarts e impacto de manutenção | Falha de readiness ou erro acima do NFR por 5 min | Reincidência em duas janelas de 30 dias ou requisito aprovado de eliminar ponto único de falha |

Para backlog, mede-se espera por execução — por exemplo, schedule-to-start — e não a duração legítima de um Workflow de longa execução.

### Latência p95 por estágio

| Estágio | Método | Limiar de ação |
| --- | --- | --- |
| Local/teste de carga | Fixar versão, dataset, concorrência e hardware; registrar p95 por classe de rota | Regressão `>= 1,5x` contra o baseline impede promoção |
| VPS/Compose inicial | Medir p95 externo e interno por 5 min, comparando a mesma classe de operação | `>= 1,5x` o baseline ou acima do NFR vigente por 15 min inicia análise e scale-up |
| Componentes separados | Manter p95 end-to-end e por componente para localizar contenção | O mesmo limiar por 15 min no componente dominante inicia scale-up ou scale-out desse componente |
| Múltiplas réplicas/Kubernetes | Medir p95 agregado e por réplica, incluindo balanceamento e dependências | Exceder o NFR com uma réplica indisponível reprova capacidade e HA; Kubernetes não relaxa o alvo |

## Decisão por etapa

| Etapa | Entrar quando | Pré-condições | Sair quando |
| --- | --- | --- | --- |
| Scale-up | Um componente cruza um gatilho sustentado e o custo vertical ainda é aceitável | Regressões, queries, índices, leaks e configuração incorreta descartados | Margem volta abaixo do nível de atenção em carga de pico validada |
| Separação de componentes | API, worker ou coordenação consome `>= 60%` do recurso saturado em três revisões, ou backlog cresce enquanto a API permanece saudável | Contratos de processo, health checks e configuração externa permitem execução separada | Cada componente escala e falha de forma independente no Runtime atual |
| Scale-out | O componente separado continua acima do gatilho de ação, ou disponibilidade exige múltiplas réplicas | Processo stateless, sessões externas, readiness válida, operações idempotentes e orçamento de conexões PostgreSQL | Carga de pico validada com perda de uma réplica e margem abaixo do nível de atenção |
| Kubernetes | Scale-out e HA são necessidades recorrentes, e Compose/VPS não atende automação ou recuperação com custo aceitável | Critérios cumulativos abaixo e gate operacional aprovado | Runtime aprovado, automatizado e operável sem manter infraestrutura paralela especulativa |

## Gate para Runtime Kubernetes

Kubernetes só entra em decisão quando todos os itens abaixo possuem evidência:

1. Pelo menos dois componentes precisam de múltiplas réplicas de forma recorrente, ou existe requisito aprovado de HA que não pode ser atendido pelo Runtime atual.
2. Teste de carga demonstra que scale-up e separação de componentes não mantêm a margem definida neste documento.
3. Deploy, recuperação ou rebalanceamento em VPS/Compose consome mais de 4 horas operacionais por mês durante dois meses consecutivos, ou viola o RTO vigente.
4. Readiness, shutdown gracioso, configuração externa, secrets e storage externo já funcionam com os mesmos artefatos OCI.
5. O orçamento inclui operação do cluster, observabilidade, upgrades, backup e resposta a incidentes — não apenas custo de compute.
6. O gate responsável aprova explicitamente o Runtime; quantidade de Tenants, isoladamente, nunca satisfaz o critério.

## Regras de decisão

- O primeiro Tenant em produção usa VPS/Compose e não depende de Kubernetes.
- Otimização de código, query ou configuração precede aumento de infraestrutura quando houver regressão demonstrável.
- Scale-out da aplicação não pode esgotar `max_connections`; o orçamento considera todas as réplicas e reserva pelo menos 20% para operação e recuperação.
- Separar componentes não cria novos Modules nem altera ownership de domínio.
- Um Tenant adicional é somente contexto de carga; decisões usam consumo, latência, backlog, storage e disponibilidade observados.
- Toda decisão registra período, versão/commit, carga, baseline, sinais, ação escolhida, custo e resultado posterior.

## Rastreabilidade

- ADR-0049 — baseline operacional managed, p95, saturação sustentada, backlog e recuperação.
- ADR-0053 — evolução do Runtime sem Helm prematuro.
- `EL-44` — NFRs e gates de saída por fase.
- `EL-29` — consolidação na matriz de Deployment.
