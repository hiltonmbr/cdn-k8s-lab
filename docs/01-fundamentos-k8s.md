# 📖 01 — Fundamentos do Kubernetes

> **Objetivo:** Entender por que o Kubernetes existe, como ele se relaciona com o Docker, e conhecer a arquitetura do cluster antes de tocar no terminal. Ao final, você terá uma visão clara do "grande quadro" da orquestração.

---

## 🤔 Por que Kubernetes?

No Docker Lab, você aprendeu a empacotar aplicações em contêineres e orquestrá-las com Docker Compose. Isso funciona muito bem para **um único servidor**. Mas e quando a escala muda?

Imagine que sua empresa processa dados de vendas de 500 lojas em tempo real. O pipeline inclui:
- 3 instâncias de API de ingestão
- 5 workers Spark para processamento
- 2 réplicas de PostgreSQL
- 1 cluster Kafka com 3 brokers
- 1 dashboard Jupyter

São **14+ contêineres** distribuídos em **vários servidores**. Agora pergunte-se:

| Problema | Docker Compose resolve? |
|---|---|
| Um worker Spark falhou às 3h da manhã. Quem reinicia? | ❌ Não — alguém precisa intervir manualmente |
| Pico de Black Friday — preciso de 20 workers em vez de 5 | ❌ Não — preciso parar, editar o YAML e reiniciar |
| O servidor #2 pegou fogo. Os contêineres dele precisam migrar | ❌ Não — Compose gerencia apenas um host |
| Quero atualizar a API sem interromper os usuários | ❌ Difícil — `docker compose up --build` causa downtime |
| Preciso distribuir contêineres entre 10 servidores | ❌ Compose não conhece múltiplos hosts |

### A Resposta: Orquestração

O **Kubernetes (K8s)** é um sistema de orquestração de contêineres que resolve todos esses problemas automaticamente:

| Capacidade | Como o K8s resolve |
|---|---|
| **Auto-healing** | Pod falhou? K8s detecta e cria um novo automaticamente |
| **Scaling** | `kubectl scale --replicas=20` — ou escala automática com HPA |
| **Distribuição** | O Scheduler decide em qual nó cada Pod roda, otimizando recursos |
| **Rolling updates** | Atualiza versões gradualmente, sem downtime |
| **Service Discovery** | Pods se encontram por nome via DNS interno |

> 💡 **Analogia:** Se o Docker Compose é o **maestro de uma banda** (gerencia poucos músicos em um palco), o Kubernetes é o **maestro de uma orquestra sinfônica** (gerencia centenas de músicos em múltiplos palcos, substituindo automaticamente quem desafina).

---

## 🏛️ A Origem do Kubernetes

O Kubernetes nasceu da experiência do Google com seu sistema interno chamado **Borg**, que orquestrava milhões de contêineres nos datacenters do Google desde 2003.

**Timeline:**
```
2003 ─── Google cria o Borg (orquestração interna)
  │
2013 ─── Google cria o Omega (evolução do Borg)
  │
2014 ─── Google doa o Kubernetes à comunidade open-source
  │
2015 ─── CNCF (Cloud Native Computing Foundation) assume a governança
  │
2024 ─── K8s é o padrão da indústria:
         - AWS (EKS), Google Cloud (GKE), Azure (AKS)
         - 96% das empresas usam ou avaliam K8s (CNCF Survey)
```

O nome "Kubernetes" vem do grego **κυβερνήτης** (kubernétēs) — **timoneiro**, aquele que pilota um navio. A abreviação **K8s** conta as 8 letras entre o "K" e o "s".

---

## 📐 Arquitetura do Kubernetes

Um cluster Kubernetes é dividido em dois tipos de nós:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CLUSTER KUBERNETES                               │
│                                                                         │
│  ┌──────────────────────────────────────┐                               │
│  │        🧠 CONTROL PLANE              │                               │
│  │     (Nó Mestre — o cérebro)          │                               │
│  │                                      │                               │
│  │  ┌──────────┐  ┌───────────────┐     │                               │
│  │  │API Server│  │   Scheduler   │     │  ← Decide onde rodar cada Pod │
│  │  │ (kube-   │  │               │     │                               │
│  │  │ apiserver│  └───────────────┘     │                               │
│  │  └──────────┘  ┌───────────────┐     │                               │
│  │  ┌──────────┐  │  Controller   │     │  ← Mantém o estado desejado   │
│  │  │  etcd    │  │   Manager     │     │                               │
│  │  │(banco de │  └───────────────┘     │                               │
│  │  │ dados)   │                        │                               │
│  │  └──────────┘                        │                               │
│  └──────────────────────────────────────┘                               │
│                          │                                              │
│                   API (HTTPS)                                           │
│            ┌─────────────┼──────────────┐                               │
│            ▼             ▼              ▼                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                     │
│  │ 🏗️ WORKER #1 │ │ 🏗️ WORKER #2 │ │ 🏗️ WORKER #3 │                     │
│  │              │ │              │ │              │                     │
│  │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │                     │
│  │ │ kubelet  │ │ │ │ kubelet  │ │ │ │ kubelet  │ │  ← Agente no nó    │
│  │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │                     │
│  │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │                     │
│  │ │kube-proxy│ │ │ │kube-proxy│ │ │ │kube-proxy│ │  ← Rede do nó      │
│  │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │                     │
│  │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │                     │
│  │ │container │ │ │ │container │ │ │ │container │ │  ← containerd       │
│  │ │ runtime  │ │ │ │ runtime  │ │ │ │ runtime  │ │                     │
│  │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │                     │
│  │              │ │              │ │              │                     │
│  │ [Pod][Pod]   │ │ [Pod][Pod]   │ │ [Pod]        │  ← Suas aplicações  │
│  └──────────────┘ └──────────────┘ └──────────────┘                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 🧠 Control Plane (Nó Mestre)

O Control Plane é o "cérebro" do cluster. Ele nunca executa suas aplicações — apenas **toma decisões** sobre onde e como executá-las.

| Componente | Função | Analogia |
|---|---|---|
| **API Server** | Ponto central de comunicação. Todo comando `kubectl` passa por ele. | Recepcionista do hotel — todo pedido passa por ela |
| **etcd** | Banco de dados distribuído que armazena **todo** o estado do cluster. | Livro de registros do hotel — quem está em qual quarto |
| **Scheduler** | Decide em qual Worker Node cada novo Pod será executado. | Recepcionista que atribui quartos aos hóspedes |
| **Controller Manager** | Monitora o estado atual e o compara com o desejado. Corrige desvios. | Gerente que verifica se todas as regras estão sendo seguidas |

### 🏗️ Worker Nodes (Nós de Trabalho)

Os Workers são as máquinas que **realmente executam** suas aplicações (Pods).

| Componente | Função | Analogia |
|---|---|---|
| **kubelet** | Agente que roda em cada Worker. Recebe instruções do API Server e gerencia os Pods locais. | Gerente de andar do hotel — cuida dos quartos no seu andar |
| **kube-proxy** | Gerencia as regras de rede no nó. Roteia tráfego para os Pods corretos. | Porteiro que direciona visitantes ao quarto certo |
| **Container Runtime** | Motor de contêineres (containerd, CRI-O). Cria e executa os contêineres reais. | Infraestrutura do hotel — encanamento, eletricidade |

---

## 📝 A Filosofia Declarativa

O Kubernetes usa uma abordagem **declarativa**: você descreve o **estado desejado** em um arquivo YAML, e o K8s trabalha continuamente para alcançar e manter esse estado.

### Imperativo vs Declarativo

```
🔧 IMPERATIVO (Docker / comandos manuais):
   "Execute 3 contêineres Nginx"
   "Se um morrer, crie outro"
   "Se precisar de mais, crie manualmente"
   → Você diz COMO fazer, passo a passo

📝 DECLARATIVO (Kubernetes):
   "Eu quero 3 réplicas de Nginx rodando"
   → K8s garante que SEMPRE haverá 3
   → Se uma morrer, K8s cria automaticamente
   → Você diz O QUE quer, K8s decide como fazer
```

### Exemplo Prático

```yaml
# deployment-nginx.yaml — "Eu quero 3 réplicas de Nginx"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: meu-nginx
spec:
  replicas: 3          # ← Estado desejado: 3 Pods
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
```

Quando você aplica esse YAML:

```bash
kubectl apply -f deployment-nginx.yaml
```

O K8s entra em um **loop de reconciliação** contínuo:

```
     ┌────────────────────────────────────────┐
     │        Loop de Reconciliação K8s       │
     │                                        │
     │   Estado Desejado: 3 Pods Nginx        │
     │   Estado Atual:    ? Pods rodando      │
     │                                        │
     │   ┌──────────────────────────────┐     │
     │   │ Atual < Desejado?           │     │
     │   │   SIM → Criar Pods faltantes│     │
     │   │   NÃO → Tudo OK, monitorar  │     │
     │   │                              │     │
     │   │ Atual > Desejado?           │     │
     │   │   SIM → Remover excesso     │     │
     │   └──────────────────────────────┘     │
     │                                        │
     │   🔄 Repete a cada poucos segundos     │
     └────────────────────────────────────────┘
```

Se você deletar um Pod manualmente, o K8s percebe que o estado atual (2 Pods) difere do desejado (3 Pods) e cria um novo automaticamente. Isso é **auto-healing**.

---

## 🌐 O Ecossistema CNCF

O Kubernetes é o projeto central de um ecossistema chamado **Cloud Native Computing Foundation (CNCF)**, que inclui centenas de ferramentas complementares:

| Categoria | Ferramenta | Para que serve |
|---|---|---|
| **Orquestração** | Kubernetes | Gerenciar contêineres em escala |
| **Service Mesh** | Istio, Linkerd | Comunicação segura entre serviços |
| **Monitoramento** | Prometheus + Grafana | Métricas e dashboards |
| **Logging** | Fluentd, Loki | Coleta centralizada de logs |
| **CI/CD** | Argo CD, Flux | Deploy contínuo via GitOps |
| **Armazenamento** | Rook (Ceph) | Storage distribuído |
| **Segurança** | Falco, OPA | Detecção de ameaças e políticas |

> 💡 **Para o estudante de dados:** As ferramentas que você já conhece — Spark, Kafka, Airflow, Jupyter — todas têm integrações nativas com Kubernetes. Aprender K8s é investir no futuro da sua carreira em dados.

---

## 📝 Resumo

| Conceito | Definição |
|---|---|
| **Kubernetes (K8s)** | Sistema de orquestração de contêineres — gerencia, escala e auto-recupera aplicações |
| **Cluster** | Conjunto de máquinas (nós) gerenciadas pelo K8s |
| **Control Plane** | Cérebro do cluster — API Server, etcd, Scheduler, Controller Manager |
| **Worker Node** | Máquina que executa Pods — kubelet, kube-proxy, container runtime |
| **Filosofia Declarativa** | Você descreve o estado desejado em YAML; K8s mantém automaticamente |
| **Auto-healing** | K8s recria Pods que falham, sem intervenção humana |
| **CNCF** | Fundação que governa o K8s e seu ecossistema de ferramentas |

---

**Próximo:** [02 — Instalação (kind, kubectl e ferramentas)](02-instalacao-kind.md) →
