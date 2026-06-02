# ☸️ Kubernetes Lab

### **Tutorial completo e prático de Kubernetes (K8s)**
Do Docker ao Kubernetes — orquestre contêineres como um profissional, com exemplos que você executa no seu computador.

![Kubernetes](https://img.shields.io/badge/Kubernetes-1.31-326CE5?logo=kubernetes&logoColor=white)
![kind](https://img.shields.io/badge/kind-0.25-326CE5?logo=kubernetes&logoColor=white)
![kubectl](https://img.shields.io/badge/kubectl-CLI-326CE5?logo=kubernetes&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-27.x-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 O que é este repositório?

Um **laboratório hands-on** para aprender Kubernetes na prática — a continuação natural do [Docker Lab](https://github.com/lemaufpb/cdn-docker-lab). Cada conceito é ensinado com:

- 📖 **Documentação rica** — explicações detalhadas com diagramas e analogias
- 🧪 **Labs práticos** — exercícios passo a passo que você executa no terminal
- 📄 **Manifests YAML reais** — arquivos de configuração prontos para aplicar no cluster
- 💻 **Código funcional** — aplicações Python que rodam em Pods K8s

> **Público-alvo:** Estudantes que já completaram o Docker Lab (ou têm conhecimento equivalente de Docker). Não é necessário experiência prévia com Kubernetes.

> **Ferramenta utilizada:** Usamos o **[kind](https://kind.sigs.k8s.io/)** (Kubernetes IN Docker) para rodar clusters K8s locais. O kind cria nós do cluster como contêineres Docker — leve, rápido e sem necessidade de VMs.

---

## ⚡ Quick Start (5 minutos)

Se você já tem Docker instalado, pode criar seu primeiro cluster K8s agora:

```bash
# 1. Instalar kind e kubectl
# macOS:
brew install kind kubectl

# Linux:
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind && sudo mv ./kind /usr/local/bin/kind
# kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/

# 2. Clone o repositório
git clone https://github.com/lemaufpb/cdn-k8s-lab.git
cd cdn-k8s-lab

# 3. Criar um cluster Kubernetes local
kind create cluster --name meu-primeiro-cluster

# 4. Verificar que o cluster está rodando
kubectl get nodes
# → NAME                                STATUS   ROLES           AGE   VERSION
# → meu-primeiro-cluster-control-plane  Ready    control-plane   30s   v1.31.0

# 5. Rodar seu primeiro Pod (Nginx)
kubectl run hello-nginx --image=nginx:latest --port=80

# 6. Verificar o Pod
kubectl get pods
# → NAME          READY   STATUS    RESTARTS   AGE
# → hello-nginx   1/1     Running   0          10s

# 7. Acessar no navegador via port-forward
kubectl port-forward pod/hello-nginx 8080:80
# Abra: http://localhost:8080 — Welcome to nginx! 🎉

# 8. Limpeza
# Ctrl+C para parar o port-forward
kubectl delete pod hello-nginx
kind delete cluster --name meu-primeiro-cluster
```

**Parabéns!** 🎉 Você acabou de criar um cluster Kubernetes e rodou uma aplicação nele.

---

## ⚙️ Pré-requisitos

| Requisito | Detalhes |
|---|---|
| **Docker** | [Instalar Docker Desktop](https://docs.docker.com/get-docker/) (Windows/macOS) ou Docker Engine (Linux) |
| **Docker Lab** | [Completar o cdn-docker-lab](https://github.com/lemaufpb/cdn-docker-lab) (ou conhecimento equivalente) |
| **Terminal** | PowerShell (Windows), Terminal.app (macOS) ou bash (Linux) |
| **RAM** | 8 GB livres (16 GB recomendado para Labs 04-05) |
| **CPU** | 4 cores mínimo |
| **Disco** | 10 GB livres para imagens Docker e nós do cluster |

Verifique a instalação:
```bash
docker version          # Docker Engine
kind version            # kind (Kubernetes IN Docker)
kubectl version --client  # kubectl (CLI do Kubernetes)
```

---

## 🗺️ Mapa de Aprendizagem

O conteúdo está organizado em **documentação conceitual** + **labs práticos**, seguindo uma progressão didática:

### 📖 Documentação

| # | Módulo | Tópicos | Link |
|---|---|---|---|
| 01 | **Fundamentos K8s** | Por que orquestrar, arquitetura, Control Plane, Workers, filosofia declarativa | [📖 Ler](docs/01-fundamentos-k8s.md) |
| 02 | **Instalação (kind)** | Instalação de kind, kubectl, k9s, criação de clusters, kind-config | [📖 Ler](docs/02-instalacao-kind.md) |
| 03 | **Pods e Containers** | Anatomia YAML, ciclo de vida, Labels, Selectors, resource limits | [📖 Ler](docs/03-pods-e-containers.md) |
| 04 | **Deployments** | ReplicaSets, rolling updates, rollback, scaling, HPA | [📖 Ler](docs/04-deployments-e-replicasets.md) |
| 05 | **Services e Rede** | ClusterIP, NodePort, LoadBalancer, DNS interno, Ingress | [📖 Ler](docs/05-services-e-networking.md) |
| 06 | **Volumes e Config** | PV, PVC, ConfigMaps, Secrets, StorageClass | [📖 Ler](docs/06-volumes-e-configmaps.md) |
| 07 | **kubectl Cheatsheet** | Referência rápida de todos os comandos essenciais | [📖 Ler](docs/07-kubectl-cheatsheet.md) |

### 🧪 Labs Práticos

| # | Lab | Abordagem | O que faz | Tempo | Link |
|---|---|---|---|---|---|
| 01 | **Hello K8s** | Primeiro cluster | kind, kubectl, Pods, port-forward | 30 min | [🧪 Ir](labs/lab-01-hello-k8s/README.md) |
| 02 | **Deployments** | Scaling e rollouts | Réplicas, rolling update, rollback, Services | 30 min | [🧪 Ir](labs/lab-02-deployments/README.md) |
| 03 | **App Fullstack** | K8s + Banco externo | API no K8s + PostgreSQL externo (Docker) + pgAdmin | 40 min | [🧪 Ir](labs/lab-03-app-fullstack/README.md) |
| 04 | **Spark on K8s** | Big Data no cluster | Spark Master + Workers, job WordCount, escalabilidade | 35 min | [🧪 Ir](labs/lab-04-spark-on-k8s/README.md) |
| 05 | **Dashboard** | Monitoramento visual | Kubernetes Dashboard, k9s, métricas do cluster | 25 min | [🧪 Ir](labs/lab-05-dashboard-e-monitoring/README.md) |

### 📍 Progressão Sugerida

```
📖 01 Fundamentos ──► 📖 02 Instalação ──► 🧪 Lab 01 (Hello K8s)
                                                │
📖 03 Pods ◄────────────────────────────────────┘
        │
        └──► 📖 04 Deployments ──► 🧪 Lab 02 (Deployments)
                                        │
📖 05 Services ◄───────────────────────┘
📖 06 Volumes & Config                  │
        │                                │
        └──────────────► 🧪 Lab 03 (Fullstack + Banco Externo)
                               │
                               ├──► 🧪 Lab 04 (Spark on K8s)
                               │
📖 07 Cheatsheet               └──► 🧪 Lab 05 (Dashboard)
```

---

## 📂 Estrutura do Repositório

```
cdn-k8s-lab/
│
├── 📖 docs/                                # Documentação conceitual
│   ├── 01-fundamentos-k8s.md              # O que é K8s, arquitetura, filosofia declarativa
│   ├── 02-instalacao-kind.md              # Instalação de kind, kubectl e ferramentas
│   ├── 03-pods-e-containers.md            # Pods, multi-container, Labels, ciclo de vida
│   ├── 04-deployments-e-replicasets.md    # Deployments, ReplicaSets, rollouts, scaling
│   ├── 05-services-e-networking.md        # Services, DNS interno, Ingress
│   ├── 06-volumes-e-configmaps.md         # PV/PVC, ConfigMaps, Secrets
│   └── 07-kubectl-cheatsheet.md           # Referência rápida de comandos
│
├── 🧪 labs/                                # Exercícios práticos
│   ├── lab-01-hello-k8s/                  # Primeiro cluster e primeiro Pod
│   │   └── README.md
│   ├── lab-02-deployments/                # Deployments, scaling, rollouts
│   │   ├── manifests/
│   │   └── README.md
│   ├── lab-03-app-fullstack/              # App K8s + Banco externo (Docker)
│   │   ├── app/
│   │   ├── manifests/
│   │   └── README.md
│   ├── lab-04-spark-on-k8s/               # Apache Spark no cluster K8s
│   │   ├── manifests/
│   │   ├── jobs/
│   │   └── README.md
│   └── lab-05-dashboard-e-monitoring/     # Dashboard e k9s
│       ├── manifests/
│       └── README.md
│
├── 📋 kind-config.yaml                    # Configuração do cluster (multi-node)
├── 📋 .gitignore
└── 📋 README.md                           # ← Você está aqui
```

---

## 🔑 Conceitos-Chave

| Conceito | Descrição |
| :--- | :--- |
| **☸️ Cluster** | Conjunto de máquinas (nós) que executam aplicações em contêineres gerenciadas pelo Kubernetes. Composto por Control Plane + Worker Nodes. |
| **🧠 Control Plane** | Cérebro do cluster. Contém API Server, Scheduler, Controller Manager e etcd. Toma todas as decisões sobre onde e como executar os Pods. |
| **🏗️ Worker Node** | Máquina que executa as cargas de trabalho. Contém kubelet (agente), kube-proxy (rede) e o container runtime (containerd). |
| **🫛 Pod** | Menor unidade executável do K8s. Encapsula um ou mais contêineres que compartilham rede e armazenamento. Efêmero — pode ser destruído e recriado a qualquer momento. |
| **🚀 Deployment** | Gerencia Pods de forma declarativa. Define quantas réplicas manter, estratégia de atualização e permite rollback automático. |
| **🌐 Service** | Endereço virtual estável que roteia tráfego para um conjunto de Pods. Resolve o problema de Pods efêmeros com IPs que mudam. |
| **💾 PersistentVolumeClaim** | Solicitação de armazenamento persistente. Garante que dados sobrevivam à destruição e recriação de Pods. |
| **🗝️ Secret** | Armazena dados sensíveis (senhas, tokens, certificados) de forma criptografada, separados do código da aplicação. |
| **📋 ConfigMap** | Armazena configurações não-sensíveis (URLs, flags, arquivos .conf) externalizadas dos contêineres. |
| **📝 YAML Declarativo** | No K8s, você descreve o **estado desejado** em YAML. O K8s continuamente trabalha para manter o cluster nesse estado. |

---

## 📝 Cheatsheet Rápido

```bash
# ── Cluster (kind) ──
kind create cluster --name lab                    # Criar cluster
kind create cluster --config kind-config.yaml     # Criar com configuração
kind get clusters                                 # Listar clusters
kind delete cluster --name lab                    # Deletar cluster

# ── Pods ──
kubectl run nginx --image=nginx:latest            # Criar Pod rápido
kubectl get pods                                  # Listar Pods
kubectl get pods -o wide                          # Listar com IPs e nós
kubectl describe pod nginx                        # Detalhes do Pod
kubectl logs nginx                                # Ver logs
kubectl logs -f nginx                             # Logs em tempo real
kubectl exec -it nginx -- bash                    # Entrar no Pod
kubectl delete pod nginx                          # Deletar Pod

# ── Deployments ──
kubectl apply -f deployment.yaml                  # Criar/atualizar Deployment
kubectl get deployments                           # Listar Deployments
kubectl scale deployment app --replicas=5         # Escalar
kubectl rollout status deployment app             # Status do rollout
kubectl rollout undo deployment app               # Rollback

# ── Services ──
kubectl expose deployment app --port=80 --type=NodePort  # Expor
kubectl get services                              # Listar Services
kubectl port-forward svc/app 8080:80              # Acessar localmente

# ── Recursos Gerais ──
kubectl get all                                   # Ver tudo no namespace
kubectl get all -A                                # Ver tudo em todos os namespaces
kubectl apply -f manifests/                       # Aplicar diretório inteiro
kubectl delete -f manifests/                      # Deletar tudo do diretório

# ── Debug ──
kubectl describe pod <nome>                       # Eventos e estado detalhado
kubectl logs <nome> --previous                    # Logs do contêiner anterior (crash)
kubectl get events --sort-by='.lastTimestamp'      # Eventos recentes do cluster
```

---

## 🔗 De Docker para Kubernetes

Se você veio do Docker Lab, esta tabela traduz os conceitos:

| Docker | Kubernetes | Observação |
|---|---|---|
| `docker run` | `kubectl run` / `kubectl apply` | K8s usa YAML declarativo |
| Contêiner | **Pod** | Pod = 1+ contêineres com rede compartilhada |
| `docker-compose.yml` | **Manifests YAML** (Deployment, Service, etc.) | Cada recurso tem seu próprio YAML |
| `docker compose up` | `kubectl apply -f manifests/` | Aplica todos os YAMLs de uma vez |
| `docker compose down` | `kubectl delete -f manifests/` | Remove todos os recursos |
| `docker ps` | `kubectl get pods` | Lista cargas de trabalho |
| `docker logs` | `kubectl logs` | Mesmo conceito |
| `docker exec -it` | `kubectl exec -it -- bash` | Note o `--` antes do comando |
| Volume nomeado | **PersistentVolumeClaim (PVC)** | Armazenamento gerenciado pelo cluster |
| `-e VAR=valor` | **ConfigMap** / **Secret** | Configuração externalizada |
| Rede bridge | **Service** + DNS interno | Comunicação entre Pods via nome |
| `-p 8080:80` | **NodePort** / **port-forward** | Acesso externo ao cluster |
| `docker compose scale` | `kubectl scale` / **HPA** | K8s escala automaticamente |
| Restart automático | **Auto-healing** | K8s recria Pods que falham |

---

## 📚 Referências

- [Kubernetes Documentation — Getting Started](https://kubernetes.io/docs/setup/)
- [kind — Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [kubectl Cheat Sheet — Oficial](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- Burns, B.; Beda, J.; Hightower, K. **Kubernetes: Up and Running**. 3ª ed. O'Reilly Media, 2022.
- Crepalde, N. **Big Data on Kubernetes**. Packt Publishing, 2024.
- Gomes, J. **Kubernetes: Tudo sobre orquestração de containers**. Casa do Código, 2022.

---

## 📄 Licença

Este material é de uso educacional. Criado para a disciplina de **Ciência de Dados para Negócios** — UFPB.

---

> **☸️ Docker empacota. Kubernetes orquestra. Domine ambos e domine a infraestrutura moderna.**
