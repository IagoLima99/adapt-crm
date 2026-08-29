# AdaptCRM

Monorepo do AdaptCRM com aplicação web React/Vite, API FastAPI e worker
Temporal. Esta fundação ainda não contém fluxos de CRM ou workflows de
negócio.

## Pré-requisitos

- Python 3.13 e `uv` compatível com o lockfile.
- Node.js 22.23.2 e npm 10.9.x.
- Endpoint PostgreSQL local com uma URL válida.
- Servidor Temporal local acessível pelo worker.

As versões de runtime estão fixadas em `.python-version`, `.node-version` e
`package.json`. Dockerfiles e Docker Compose pertencem ao EL-25/EL-40 e não
fazem parte deste bootstrap.

## Preparar um clone limpo

```shell
git clone https://github.com/IagoLima99/adapt-crm.git
cd adapt-crm
```

Crie a configuração local sem alterar o exemplo versionado:

```powershell
Copy-Item .env.example .env
```

Em shells POSIX, use `cp .env.example .env`. Revise os endpoints locais antes
de continuar. O arquivo `.env` é ignorado pelo Git e exclusivo de
desenvolvimento.

Instale todas as dependências travadas:

`python scripts/repo.py install`

Esse comando executa `uv sync --locked --all-packages --dev` e `npm ci`,
interrompendo no primeiro erro.

## Configuração local

| Variável | Consumidor | Obrigatória | Finalidade |
| --- | --- | --- | --- |
| `APP_ENV` | API e worker | Sim | Profile tipado do processo; use `local` neste fluxo. |
| `API_HOST` | comando `dev` | Não | Interface de escuta da API; padrão `127.0.0.1`. |
| `API_PORT` | comando `dev` | Não | Porta HTTP da API; padrão `8000`. |
| `DATABASE_URL` | API | Sim | Endpoint PostgreSQL externo ao processo. |
| `TEMPORAL_ADDRESS` | worker | Sim | Endpoint do servidor Temporal. |
| `TEMPORAL_NAMESPACE` | worker | Sim | Namespace utilizado pelo worker. |
| `TEMPORAL_TASK_QUEUE` | worker | Sim | Task queue técnica registrada no startup. |
| `VITE_API_BASE_URL` | web | Sim | Destino HTTP do proxy `/api` usado no desenvolvimento. |

Variáveis já definidas no ambiente do processo têm precedência sobre o
arquivo `.env`. Valores ausentes ou em branco impedem o startup seguro.

## Desenvolvimento

Com PostgreSQL e Temporal disponíveis nos endpoints configurados, inicie os
três processos:

`python scripts/repo.py dev`

O supervisor inicia API, worker e web. `Ctrl+C` encerra os processos filhos;
se um deles falhar, os demais também são encerrados e o exit code é propagado.
Use `python scripts/repo.py dev --env-file outro.env` para selecionar outro
arquivo local.

Endpoints padrão:

- Web: `http://localhost:5173`
- API: `http://localhost:8000`
- Health da API: `http://localhost:8000/health`

A conexão e as migrations funcionais do PostgreSQL pertencem ao EL-24. A
containerização das dependências e aplicações pertence ao EL-25/EL-40.

## Qualidade e build

- `python scripts/repo.py test` executa as suítes Python e web.
- `python scripts/repo.py lint` executa Ruff, formatação, mypy, arquitetura,
  ESLint e TypeScript.
- `python scripts/repo.py build` gera o build web de produção.
- `python scripts/repo.py smoke` valida o contrato público `/health` da API
  através do proxy `/api` do servidor web.

## Validação do bootstrap

Para reproduzir a validação sem depender de arquivos locais não versionados:

1. Extraia ou clone a revisão em um diretório vazio.
2. Copie `.env.example` para `.env` e ajuste somente endpoints locais.
3. Execute `python scripts/repo.py install`.
4. Execute `python scripts/repo.py lint`, `python scripts/repo.py test` e
   `python scripts/repo.py build`.
5. Inicie os processos com `python scripts/repo.py dev` e, em outro terminal,
   execute `python scripts/repo.py smoke`.

## Troubleshooting

- Falha imediata do worker: confirme `TEMPORAL_ADDRESS` e se o servidor
  Temporal está acessível.
- Erro de configuração da API: confira `APP_ENV` e a sintaxe de
  `DATABASE_URL`.
- Versão Node incompatível: use exatamente a versão de `.node-version`; o npm
  está configurado com `engine-strict=true`.
