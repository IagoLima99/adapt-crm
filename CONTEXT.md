# AdaptCRM

Plataforma de relacionamento multitemplate que permite a organizações operar um CRM configurado para seu contexto sem manter variantes do produto por cliente.

## Language

**Tenant**:
Organização que utiliza o AdaptCRM e constitui o limite de isolamento de seus dados e configurações.
_Avoid_: Cliente, conta, organização cliente

**Customer**:
Relacionamento comercial que um Tenant decide gerenciar com exatamente um Contact ou uma Company, desde o interesse inicial e ao longo de seu ciclo de vida.
_Avoid_: Cliente, conta, pessoa, organização

**Contact**:
Pessoa conhecida por um Tenant, independentemente de já possuir um relacionamento comercial ativo.
_Avoid_: Customer, cliente, usuário

**Company**:
Organização conhecida por um Tenant, independentemente de já possuir um relacionamento comercial ativo.
_Avoid_: Tenant, Customer, conta

**Affiliation**:
Vínculo historizado entre um Contact e uma Company, incluindo o papel exercido e seu período de validade.
_Avoid_: Emprego, associação informal, empresa do contato

**User**:
Pessoa autenticada dentro de um mesmo control plane que pode receber autorização para operar em um ou mais Tenants.
_Avoid_: Usuário do cliente, operador

**Identity**:
Credencial de autenticação vinculada a um User e identificada de forma única por seu provider e subject.
_Avoid_: User, email, Membership

**Membership**:
Vínculo que concede a um User papéis e permissões dentro de um Tenant específico.
_Avoid_: User do Tenant, perfil global, vínculo de usuário

**Role**:
Agrupamento de Permissions definido dentro de um Tenant e atribuído a Memberships.
_Avoid_: Perfil global, cargo, Entitlement

**Permission**:
Autorização para executar uma ação sobre um recurso de um Module dentro de um Tenant.
_Avoid_: Role, Entitlement, Module Activation

**Platform Operator**:
User com concessão administrativa da plataforma separada de Memberships e limitada a operações cross-tenant explicitamente autorizadas.
_Avoid_: Administrador do Tenant, suporte com acesso permanente, superusuário

**Template**:
Blueprint declarativo e versionado que define a configuração inicial de um Tenant sem impor alterações posteriores automaticamente.
_Avoid_: Tema, modelo visual, variante do produto

**Module**:
Capacidade coesa do produto que possui suas próprias regras e dados, podendo ser essencial ou opcional para um Tenant.
_Avoid_: Plugin, biblioteca, pacote, feature isolada

**Module Entitlement**:
Direito concedido a um Tenant para utilizar um Module.
_Avoid_: Ativação, permissão de usuário, feature flag

**Module Activation**:
Escolha de um Tenant por habilitar e configurar um Module para o qual possui Module Entitlement.
_Avoid_: Entitlement, instalação, feature flag

**Custom Field**:
Campo configurado por um Tenant para um tipo de entidade específico e pertencente ao Module que possui essa entidade.
_Avoid_: Coluna customizada, campo global, metadata sem owner

## Modules

**Platform Access**:
Module essencial que administra Tenants, identidades, Memberships, autorização, auditoria e disponibilidade de Modules.
_Avoid_: IAM externo, infraestrutura, shared kernel

**Relationships**:
Module essencial que administra Contacts, Companies, Customers, Affiliations e seu histórico de relacionamento.
_Avoid_: CRM Core, cadastro genérico

**Sales**:
Module opcional que administra o processo comercial do Tenant.
_Avoid_: Relationships, faturamento

**Scheduling**:
Module opcional que administra compromissos e disponibilidade de agenda.
_Avoid_: calendário externo, automação temporal

**Service Operations**:
Module opcional que administra ordens de serviço e sua execução operacional.
_Avoid_: suporte da plataforma, atendimento comercial

**Automation**:
Module opcional que administra automações configuradas pelo Tenant.
_Avoid_: worker, Temporal, cron

**Integrations**:
Module opcional que administra conexões e sincronizações com sistemas externos.
_Avoid_: API pública, biblioteca cliente
