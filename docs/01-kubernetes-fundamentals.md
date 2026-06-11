# 📖 01 — Kubernetes Fundamentals

> **Objective:** Understand why Kubernetes exists, how it relates to Docker, and learn the cluster architecture before touching the terminal. By the end, you'll have a clear view of the "big picture" of orchestration.

---

## 🤔 Why Kubernetes?

In the Docker Lab, you learned to package applications into containers and orchestrate them with Docker Compose. This works very well for **a single server**. But what happens when the scale changes?

Imagine your company processes sales data from 500 stores in real time. The pipeline includes:
- 3 API ingestion instances
- 5 Spark workers for processing
- 2 PostgreSQL replicas
- 1 Kafka cluster with 3 brokers
- 1 Jupyter dashboard

That's **14+ containers** distributed across **multiple servers**. Now ask yourself:

| Problem | Docker Compose solve it? |
|---|---|
| A Spark worker failed at 3 AM. Who restarts it? | ❌ No — someone needs to intervene manually |
| Black Friday peak — I need 20 workers instead of 5 | ❌ No — I need to stop, edit the YAML, and restart |
| Server #2 caught fire. Its containers need to migrate | ❌ No — Compose manages only one host |
| I want to update the API without interrupting users | ❌ Hard — `docker compose up --build` causes downtime |
| I need to distribute containers across 10 servers | ❌ Compose doesn't know about multiple hosts |

### The Answer: Orchestration

**Kubernetes (K8s)** is a container orchestration system that solves all these problems automatically:

| Capability | How K8s solves it |
|---|---|
| **Auto-healing** | Pod failed? K8s detects it and creates a new one automatically |
| **Scaling** | `kubectl scale --replicas=20` — or auto-scaling with HPA |
| **Distribution** | The Scheduler decides which node each Pod runs on, optimizing resources |
| **Rolling updates** | Updates versions gradually, without downtime |
| **Service Discovery** | Pods find each other by name via internal DNS |

> 💡 **Analogy:** If Docker Compose is the **band conductor** (manages a few musicians on one stage), Kubernetes is the **symphony orchestra conductor** (manages hundreds of musicians on multiple stages, automatically replacing anyone who goes out of tune).

---

## 🏛️ The Origin of Kubernetes

Kubernetes was born from Google's experience with its internal system called **Borg**, which had been orchestrating millions of containers in Google's datacenters since 2003.

**Timeline:**
```
2003 ─── Google creates Borg (internal orchestration)
  │
2013 ─── Google creates Omega (evolution of Borg)
  │
2014 ─── Google donates Kubernetes to the open-source community
  │
2015 ─── CNCF (Cloud Native Computing Foundation) takes over governance
  │
2024 ─── K8s is the industry standard:
         - AWS (EKS), Google Cloud (GKE), Azure (AKS)
         - 96% of companies use or evaluate K8s (CNCF Survey)
```

The name "Kubernetes" comes from the Greek **κυβερνήτης** (kubernétēs) — **helmsman**, the one who pilots a ship. The abbreviation **K8s** counts the 8 letters between the "K" and the "s".

---

## 📐 Kubernetes Architecture

A Kubernetes cluster is divided into two types of nodes:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        KUBERNETES CLUSTER                               │
│                                                                         │
│  ┌──────────────────────────────────────┐                               │
│  │        🧠 CONTROL PLANE              │                               │
│  │     (Master Node — the brain)        │                               │
│  │                                      │                               │
│  │  ┌──────────┐  ┌───────────────┐     │                               │
│  │  │API Server│  │   Scheduler   │     │  ← Decides where each Pod runs│
│  │  │ (kube-   │  │               │     │                               │
│  │  │ apiserver│  └───────────────┘     │                               │
│  │  └──────────┘  ┌───────────────┐     │                               │
│  │  ┌──────────┐  │  Controller   │     │  ← Maintains desired state    │
│  │  │  etcd    │  │   Manager     │     │                               │
│  │  │(distributed│ └───────────────┘     │                               │
│  │  │  store)  │                        │                               │
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
│  │ │ kubelet  │ │ │ │ kubelet  │ │ │ │ kubelet  │ │  ← Node agent       │
│  │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │                     │
│  │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │                     │
│  │ │kube-proxy│ │ │ │kube-proxy│ │ │ │kube-proxy│ │  ← Node networking  │
│  │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │                     │
│  │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │                     │
│  │ │container │ │ │ │container │ │ │ │container │ │  ← containerd       │
│  │ │ runtime  │ │ │ │ runtime  │ │ │ │ runtime  │ │                     │
│  │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │                     │
│  │              │ │              │ │              │                     │
│  │ [Pod][Pod]   │ │ [Pod][Pod]   │ │ [Pod]        │  ← Your applications│
│  └──────────────┘ └──────────────┘ └──────────────┘                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 🧠 Control Plane (Master Node)

The Control Plane is the "brain" of the cluster. It never runs your applications — it only **makes decisions** about where and how to run them.

| Component | Function | Analogy |
|---|---|---|
| **API Server** | Central communication point. Every `kubectl` command goes through it. | Hotel receptionist — every request goes through her |
| **etcd** | Distributed database that stores **all** cluster state. | Hotel register book — who is in which room |
| **Scheduler** | Decides which Worker Node each new Pod will run on. | Receptionist who assigns rooms to guests |
| **Controller Manager** | Monitors current state and compares it with desired state. Corrects deviations. | Manager who checks that all rules are being followed |

### 🏗️ Worker Nodes

Workers are the machines that **actually run** your applications (Pods).

| Component | Function | Analogy |
|---|---|---|
| **kubelet** | Agent that runs on each Worker. Receives instructions from the API Server and manages local Pods. | Floor manager — takes care of rooms on their floor |
| **kube-proxy** | Manages networking rules on the node. Routes traffic to the correct Pods. | Doorman who directs visitors to the right room |
| **Container Runtime** | Container engine (containerd, CRI-O). Creates and runs the actual containers. | Hotel infrastructure — plumbing, electricity |

---

## 📝 The Declarative Philosophy

Kubernetes uses a **declarative** approach: you describe the **desired state** in a YAML file, and K8s continuously works to achieve and maintain that state.

### Imperative vs Declarative

```
🔧 IMPERATIVE (Docker / manual commands):
   "Run 3 Nginx containers"
   "If one dies, create another"
   "If you need more, create manually"
   → You tell HOW to do it, step by step

📝 DECLARATIVE (Kubernetes):
   "I want 3 Nginx replicas running"
   → K8s guarantees there will ALWAYS be 3
   → If one dies, K8s creates one automatically
   → You tell WHAT you want, K8s decides how to do it
```

### Practical Example

```yaml
# deployment-nginx.yaml — "I want 3 replicas of Nginx"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: meu-nginx
spec:
  replicas: 3          # ← Desired state: 3 Pods
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

When you apply this YAML:

```bash
kubectl apply -f deployment-nginx.yaml
```

K8s enters a continuous **reconciliation loop**:

```
     ┌────────────────────────────────────────┐
     │       K8s Reconciliation Loop          │
     │                                        │
     │   Desired State: 3 Nginx Pods          │
     │   Current State: ? Pods running        │
     │                                        │
     │   ┌──────────────────────────────┐     │
     │   │ Current < Desired?          │     │
     │   │   YES → Create missing Pods  │     │
     │   │   NO → All good, keep monitoring │
     │   │                              │     │
     │   │ Current > Desired?          │     │
     │   │   YES → Remove excess       │     │
     │   └──────────────────────────────┘     │
     │                                        │
     │   🔄 Repeats every few seconds         │
     └────────────────────────────────────────┘
```

If you delete a Pod manually, K8s notices that the current state (2 Pods) differs from the desired state (3 Pods) and creates a new one automatically. This is **auto-healing**.

---

## 🌐 The CNCF Ecosystem

Kubernetes is the central project of an ecosystem called the **Cloud Native Computing Foundation (CNCF)**, which includes hundreds of complementary tools:

| Category | Tool | What it's for |
|---|---|---|
| **Orchestration** | Kubernetes | Managing containers at scale |
| **Service Mesh** | Istio, Linkerd | Secure communication between services |
| **Monitoring** | Prometheus + Grafana | Metrics and dashboards |
| **Logging** | Fluentd, Loki | Centralized log collection |
| **CI/CD** | Argo CD, Flux | Continuous deployment via GitOps |
| **Storage** | Rook (Ceph) | Distributed storage |
| **Security** | Falco, OPA | Threat detection and policies |

> 💡 **For data students:** The tools you already know — Spark, Kafka, Airflow, Jupyter — all have native integrations with Kubernetes. Learning K8s is investing in the future of your data career.

---

## 📝 Summary

| Concept | Definition |
|---|---|
| **Kubernetes (K8s)** | Container orchestration system — manages, scales, and auto-heals applications |
| **Cluster** | Set of machines (nodes) managed by K8s |
| **Control Plane** | Brain of the cluster — API Server, etcd, Scheduler, Controller Manager |
| **Worker Node** | Machine that runs Pods — kubelet, kube-proxy, container runtime |
| **Declarative Philosophy** | You describe the desired state in YAML; K8s maintains it automatically |
| **Auto-healing** | K8s recreates Pods that fail, without human intervention |
| **CNCF** | Foundation that governs K8s and its ecosystem of tools |

---

**Next:** [02 — Installation (kind, kubectl, and tools)](02-installing-kind.md) →
