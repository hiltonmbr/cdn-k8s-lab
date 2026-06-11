# 📖 03 — Pods and Containers

> **Objective:** Understand the Pod — the atomic unit of Kubernetes. Learn the anatomy of a YAML file, lifecycle, Labels, Selectors, and resource limits. By the end, you'll know how to create, inspect, and manage Pods with confidence.

---

## 🫛 What is a Pod?

In Docker, the basic unit is the **container**. In Kubernetes, the basic unit is the **Pod**.

> **Pod** = a wrapper that encapsulates one or more containers sharing the same network (IP) and storage (volumes).

### Analogy

Think of a Pod as an **apartment**:
- The **apartment** (Pod) has a unique IP address
- The **residents** (containers) share the same address, the same kitchen (volumes), and the same WiFi (local network)
- If the apartment is demolished (Pod deleted), the residents go together
- The condominium (K8s cluster) builds a new apartment automatically

### Pod vs Container

| Aspect | Docker Container | Kubernetes Pod |
|---|---|---|
| **What it is** | Isolated process | Group of 1+ containers |
| **Networking** | Own IP per container | Shared IP within the Pod |
| **Internal communication** | Via Docker network | Via `localhost` (same Pod) |
| **Who manages it** | Docker Engine | kubelet (K8s agent) |
| **Ephemeral?** | Yes, but without auto-healing | Yes, with auto-healing via Deployment |

> 💡 **In practice:** 90% of Pods contain only **one container**. Multi-container Pods exist for advanced patterns like sidecar (logging, proxy).

---

## 📝 Anatomy of a Pod YAML

Every resource in Kubernetes is defined by a YAML file with 4 required sections:

```yaml
# pod-nginx.yaml
apiVersion: v1                # 1. K8s API version for this resource
kind: Pod                     # 2. Resource type (Pod, Deployment, Service...)
metadata:                     # 3. Metadata (name, labels, namespace)
  name: meu-nginx             #    Unique Pod name within the namespace
  labels:                     #    Labels: key-value pairs for organization
    app: nginx
    env: lab
spec:                         # 4. Specification (what the Pod should contain)
  containers:                 #    List of containers inside the Pod
  - name: nginx               #    Container name
    image: nginx:1.27         #    Docker image to use
    ports:
    - containerPort: 80       #    Port the container exposes
```

### The 4 fundamental sections

```
┌─────────────────────────────────────────────────────┐
│                   Pod YAML                           │
│                                                     │
│  ┌─────────────┐                                    │
│  │ apiVersion  │  "Which API to use?" → v1, apps/v1 │
│  └─────────────┘                                    │
│  ┌─────────────┐                                    │
│  │    kind     │  "What type of resource?" → Pod    │
│  └─────────────┘                                    │
│  ┌─────────────┐                                    │
│  │  metadata   │  "Who are you?" → name, labels     │
│  └─────────────┘                                    │
│  ┌─────────────┐                                    │
│  │    spec     │  "What do you contain?" → containers│
│  └─────────────┘                                    │
└─────────────────────────────────────────────────────┘
```

### Create and apply

```bash
# Create a Pod from the YAML
kubectl apply -f pod-nginx.yaml

# Verify
kubectl get pods
# → NAME        READY   STATUS    RESTARTS   AGE
# → meu-nginx   1/1     Running   0          10s

# Full details
kubectl describe pod meu-nginx

# Logs
kubectl logs meu-nginx

# Enter the Pod
kubectl exec -it meu-nginx -- bash

# Delete
kubectl delete pod meu-nginx
# or
kubectl delete -f pod-nginx.yaml
```

---

## 🔄 Pod Lifecycle

A Pod goes through defined states during its existence:

```
                    ┌──────────┐
    kubectl apply → │ Pending  │ ← Scheduler looking for a node
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ Running  │ ← Containers running
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              │                     │
         ┌────▼─────┐         ┌────▼─────┐
         │Succeeded │         │  Failed  │
         │(Completed)│        │ (Error)  │
         └──────────┘         └──────────┘
```

| State | Meaning |
|---|---|
| **Pending** | Pod accepted by the cluster, but not yet running (downloading image, waiting for resources) |
| **Running** | Pod is executing on a node. At least one container is active |
| **Succeeded** | All containers terminated successfully (exit code 0) |
| **Failed** | At least one container terminated with error (exit code ≠ 0) |
| **CrashLoopBackOff** | Container is restarting repeatedly after consecutive failures |

### Investigating issues

```bash
# General status
kubectl get pods

# If the Pod is in Pending or CrashLoopBackOff, investigate:
kubectl describe pod <pod-name>
# → The "Events" section shows exactly what happened

# If the Pod is in Error, check the logs:
kubectl logs <pod-name>

# Logs of the crashed container (previous):
kubectl logs <pod-name> --previous
```

---

## 🏷️ Labels and Selectors

Labels are **key-value pairs** attached to resources. They are the main organization mechanism of Kubernetes.

### Why Labels matter?

Imagine a cluster with 200 Pods. How does K8s know which Pods belong to which application? **Labels!**

```yaml
metadata:
  name: api-vendas-abc123
  labels:
    app: api-vendas        # ← Which application
    env: producao          # ← Which environment
    team: dados            # ← Which team
    version: "2.1"         # ← Which version
```

### Selectors — Filtering by Labels

Selectors allow you to **select** resources by their Labels:

```bash
# List all Pods from "api-vendas" application
kubectl get pods -l app=api-vendas

# List production Pods
kubectl get pods -l env=producao

# List data team Pods in production
kubectl get pods -l team=dados,env=producao

# Delete all test Pods
kubectl delete pods -l env=teste
```

### Labels in K8s — The Big Picture

```
                    Service
                 (app=api-vendas)
                       │
           Selects via Label ──► "app=api-vendas"
                       │
           ┌───────────┼───────────┐
           │           │           │
    ┌──────▼──┐  ┌─────▼───┐  ┌───▼───────┐
    │ Pod #1  │  │ Pod #2  │  │  Pod #3   │
    │app=     │  │app=     │  │app=       │
    │api-vendas  │api-vendas  │api-vendas │
    │env=prod │  │env=prod │  │env=prod   │
    └─────────┘  └─────────┘  └───────────┘
```

> 💡 **Fundamental concept:** Labels + Selectors are how K8s "glues" resources together. A Service finds its Pods by Labels. A Deployment manages its Pods by Labels. Understand this and you understand half of K8s.

---

## 📊 Resource Requests and Limits

In Docker, a container can use all of the host's CPU and memory. In K8s, you **declare** how much each Pod needs:

```yaml
spec:
  containers:
  - name: api
    image: python:3.12-slim
    resources:
      requests:          # Guaranteed minimum
        memory: "256Mi"  # 256 MiB of reserved RAM
        cpu: "250m"      # 0.25 CPU (250 millicores)
      limits:            # Maximum allowed
        memory: "512Mi"  # Up to 512 MiB (above that → OOMKilled)
        cpu: "500m"      # Up to 0.5 CPU (above that → throttling)
```

### Requests vs Limits

| | Request | Limit |
|---|---|---|
| **What it is** | Guaranteed minimum reservation | Maximum allowed ceiling |
| **What it's for** | Scheduler uses it to decide where to place the Pod | Prevents a Pod from consuming too many resources |
| **If exceeded** | N/A (it's already the minimum) | CPU: throttling / Memory: OOMKilled (Pod killed) |

### Units

| Resource | Format | Examples |
|---|---|---|
| **CPU** | millicores (m) | `100m` = 0.1 CPU, `1000m` = 1 CPU, `"2"` = 2 CPUs |
| **Memory** | Mi (Mebibytes), Gi (Gibibytes) | `256Mi`, `1Gi`, `2Gi` |

> ⚠️ **Best practice:** Always define requests and limits! Without them, a single Pod can consume all node memory and bring down other Pods.

---

## 📦 Multi-Container Pods (Sidecar Pattern)

Although most Pods have a single container, there are legitimate cases for multiple containers in the same Pod:

```yaml
# pod-com-sidecar.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-com-logger
spec:
  containers:
  # Main container — the application
  - name: app
    image: python:3.12-slim
    command: ["python", "-c", "import time; [print(f'Log {i}', flush=True) or time.sleep(2) for i in range(1000)]"]
    volumeMounts:
    - name: logs
      mountPath: /var/log/app

  # Sidecar — collects and processes logs
  - name: log-collector
    image: busybox:latest
    command: ["sh", "-c", "tail -f /var/log/app/*.log 2>/dev/null || sleep infinity"]
    volumeMounts:
    - name: logs
      mountPath: /var/log/app

  volumes:
  - name: logs
    emptyDir: {}    # Shared volume between containers
```

### Multi-Container Patterns

| Pattern | Description | Example |
|---|---|---|
| **Sidecar** | Complements the main container with auxiliary functionality | Logger, proxy, data synchronizer |
| **Ambassador** | Proxy that simplifies communication with external services | Proxy for multi-region database |
| **Adapter** | Adapts the main container's output to a standard format | Convert metrics to Prometheus format |

---

## 🆚 Creating Pods: Imperative vs Declarative

There are two ways to create Pods:

### Imperative (quick, for testing)

```bash
# Create Pod directly from the terminal
kubectl run meu-nginx --image=nginx:1.27 --port=80

# Create and expose in a single line
kubectl run meu-nginx --image=nginx:1.27 --port=80 --expose
```

### Declarative (recommended, for everything that matters)

```bash
# Create YAML file
cat <<EOF > pod-nginx.yaml
apiVersion: v1
kind: Pod
metadata:
  name: meu-nginx
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.27
    ports:
    - containerPort: 80
EOF

# Apply
kubectl apply -f pod-nginx.yaml
```

> 💡 **Golden rule:** Use imperative for quick tests. Use declarative for **everything else**. YAMLs go into Git, are versioned, reviewed, and reproducible.

### Tip — Generate YAML from an imperative command

```bash
# Generate YAML without creating the Pod (--dry-run + -o yaml)
kubectl run meu-nginx --image=nginx:1.27 --port=80 \
  --dry-run=client -o yaml > pod-nginx.yaml

# Now edit the generated YAML as needed
```

---

## 📝 Summary

| Concept | Definition |
|---|---|
| **Pod** | Smallest executable unit in K8s. Encapsulates 1+ containers with shared networking and volumes |
| **YAML** | Declarative format for defining resources. 4 sections: apiVersion, kind, metadata, spec |
| **Labels** | Key-value pairs for organizing and selecting resources |
| **Selectors** | Filters that select resources by Labels (`-l app=nginx`) |
| **Requests** | Minimum resource reservation guaranteed to the Pod |
| **Limits** | Maximum resource ceiling the Pod can consume |
| **Sidecar** | Auxiliary container in the same Pod that complements the main one |
| **`kubectl apply -f`** | Declarative (recommended) way to create resources |
| **`kubectl run`** | Imperative (quick) way to create Pods |

---

**Next:** [04 — Deployments and ReplicaSets](04-deployments-e-replicasets.md) →
