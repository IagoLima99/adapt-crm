---
status: accepted
---

# PostgreSQL como banco relacional oficial

PostgreSQL é o único banco relacional oficialmente suportado. A persistência usa SQLAlchemy 2 e Alembic como mecanismo exclusivo de evolução de schema em produção; `create_all` não substitui migrations. A plataforma não cria uma abstração de menor denominador comum para bancos alternativos, preservando acesso explícito a transações, `timestamptz`, `uuid`, RLS e recursos operacionais do PostgreSQL.

