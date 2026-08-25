---
status: accepted
---

# Runtime evolui sem Helm prematuro

Desenvolvimento local e a primeira operação em VPS usam os mesmos artefatos OCI e configuração externa, orquestrados por Compose quando aplicável. Kubernetes e Helm só serão introduzidos quando o Runtime Kubernetes for aprovado por evidências operacionais; não serão mantidos antecipadamente como infraestrutura paralela. A portabilidade vem de imagens, health checks, configuração e storage externalizados, não de manifestos especulativos.
