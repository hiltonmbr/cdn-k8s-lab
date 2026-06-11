# 📖 04 — Deployments and ReplicaSets

> **Objective:** Understand why we never create "loose" Pods in production, and how Deployments manage replicas, updates, and rollbacks automatically. By the end, you'll master the most important K8s resource for stateless applications.

---

## 🤔 Why Not Use Pods Directly?

In the previous module, we created Pods with `kubectl run` and `kubectl apply`. But "loose" Pods have a fatal problem:

```bash
# Create a Pod
kubectl run minha-api --image=python:3.12-slim

# Simulate a failure: delete the Pod
kubectl delete pod minha-api

# Verify
kubectl get pods
# → No Pods! 😱 K8s did not recreate it automatically.
```

**Loose Pods have no auto-healing!** When they die, they're gone forever.

> 💡 **Golden rule:** Never create Pods directly in production. Use **Deployments** — they guarantee your Pods are recreated automatically.

---

## 🔄 ReplicaSet: Guaranteeing N Replicas

The **ReplicaSet** is the resource that ensures a specific number of identical Pods is always running:

```
┌──────────────────────────────────────────────────┐
│              ReplicaSet (replicas: 3)             │
│                                                  │
│  "I guarantee there will ALWAYS be 3 active Pods" │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Pod #1  │  │  Pod #2  │  │  Pod #3  │       │
│  │  nginx   │  │  nginx   │  │  nginx   │       │
│  └──────────┘  └──────────┘  └──────────┘       │
│                                                  │
│  If Pod #2 dies → creates Pod #4 automatically   │
└──────────────────────────────────────────────────┘
```

In practice, **you never create ReplicaSets directly** — the Deployment does that for you. But it's important to understand that the Deployment manages ReplicaSets, which in turn manage Pods:

```
Deployment → creates → ReplicaSet → creates → Pod, Pod, Pod
```

---

## 🚀 Deployment: The Main Resource

The **Deployment** is the most used resource in Kubernetes. It manages ReplicaSets and adds:
- ✅ Rolling updates (update without downtime)
- ✅ Rollback (revert to a previous version)
- ✅ Scaling (increase/decrease replicas)
- ✅ Auto-healing (recreates Pods that fail)

### Anatomy of a Deployment

```yaml
# deployment-api.yaml
apiVersion: apps/v1           # API group "apps" version 1
kind: Deployment              # Type: Deployment
metadata:
  name: api-vendas            # Deployment name
  labels:
    app: api-vendas
spec:
  replicas: 3                 # Keep 3 Pods always active

  selector:                   # How the Deployment finds its Pods
    matchLabels:
      app: api-vendas         # "I manage all Pods with label app=api-vendas"

  template:                   # Pod template (how each Pod will be created)
    metadata:
      labels:
        app: api-vendas       # ⚠️ MUST match the selector above!
    spec:
      containers:
      - name: api
        image: python:3.12-slim
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

### Resource hierarchy

```
┌──────────────────────────────────────────────────────────┐
│                    Deployment                             │
│                   (api-vendas)                            │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │               ReplicaSet                           │  │
│  │        (api-vendas-7d8f9b6c5)                     │  │
│  │                                                    │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐     │  │
│  │  │   Pod      │ │   Pod      │ │   Pod      │     │  │
│  │  │ api-vendas │ │ api-vendas │ │ api-vendas │     │  │
│  │  │ -7d8f-abc │ │ -7d8f-def │ │ -7d8f-ghi │     │  │
│  │  └────────────┘ └────────────┘ └────────────┘     │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## ⚙️ Essential Commands for Deployments

```bash
# ── Create / Update ──
kubectl apply -f deployment-api.yaml            # Create or update

# ── Query ──
kubectl get deployments                          # List Deployments
kubectl get rs                                   # List ReplicaSets
kubectl get pods                                 # List created Pods
kubectl describe deployment api-vendas           # Full details

# ── Scale ──
kubectl scale deployment api-vendas --replicas=5  # Scale to 5 replicas
kubectl scale deployment api-vendas --replicas=1  # Scale down to 1 replica

# ── Update image ──
kubectl set image deployment/api-vendas \
  api=python:3.13-slim                           # Update image version

# ── Rollout (status and history) ──
kubectl rollout status deployment api-vendas     # Check update progress
kubectl rollout history deployment api-vendas    # View version history

# ── Rollback ──
kubectl rollout undo deployment api-vendas       # Revert to previous version
kubectl rollout undo deployment api-vendas \
  --to-revision=2                                # Revert to a specific revision

# ── Delete ──
kubectl delete deployment api-vendas             # Remove Deployment + RS + Pods
kubectl delete -f deployment-api.yaml            # Remove via file
```

---

## 🔄 Rolling Update: Zero-Downtime Update

When you update a Deployment's image, K8s performs a **gradual update** (rolling update):

```
Initial state: 3 Pods with image v1

Step 1: Creates 1 Pod v2, keeps 3 v1         (4 Pods total)
Step 2: Pod v2 is Ready → Removes 1 v1       (3 Pods total)
Step 3: Creates another Pod v2, keeps 2 v1    (4 Pods total)
Step 4: Pod v2 is Ready → Removes 1 v1       (3 Pods total)
Step 5: Creates last Pod v2, keeps 1 v1      (4 Pods total)
Step 6: Pod v2 is Ready → Removes last v1    (3 Pods total)

Final state: 3 Pods with image v2 ✅
```

```
v1 ████████████████████░░░░░░░░░░ → gradually dying
v2 ░░░░░░░░░░████████████████████ → gradually being born

Users NEVER go without service! There are always Pods responding.
```

### Configuring the strategy

```yaml
spec:
  strategy:
    type: RollingUpdate       # Default — updates gradually
    rollingUpdate:
      maxSurge: 1             # Maximum extra Pods during the update
      maxUnavailable: 0       # No Pod can be unavailable
```

| Strategy | Behavior | When to use |
|---|---|---|
| **RollingUpdate** (default) | Updates gradually, without downtime | Most cases |
| **Recreate** | Kills all v1 Pods, then creates all v2 | When v1 and v2 cannot coexist |

---

## ↩️ Rollback: Going Back

Deployed a buggy version? Rollback in seconds:

```bash
# View revision history
kubectl rollout history deployment api-vendas
# → REVISION  CHANGE-CAUSE
# → 1         <none>
# → 2         <none>
# → 3         <none>

# Revert to previous revision (2 → 1 step back)
kubectl rollout undo deployment api-vendas

# Revert to a specific revision
kubectl rollout undo deployment api-vendas --to-revision=1

# Verify the rollback was applied
kubectl rollout status deployment api-vendas
```

> 💡 **How it works:** K8s keeps old ReplicaSets (with replicas=0). On rollback, it simply scales the old ReplicaSet back up and scales the new one down to zero. Fast and safe.

---

## 📈 Horizontal Pod Autoscaler (HPA)

The HPA **automatically** scales the number of replicas based on metrics:

```bash
# Auto-scale between 2 and 10 replicas,
# keeping the average CPU usage at 50%
kubectl autoscale deployment api-vendas \
  --min=2 \
  --max=10 \
  --cpu-percent=50
```

```
                    CPU Usage
                        │
     High demand ──►   │  ████████ 80%  → HPA: scale to 8 replicas
                        │  ████████
     Normal demand ──►  │  ████     50%  → HPA: keep 5 replicas
                        │  ████
     Low demand ──►     │  ██       20%  → HPA: scale down to 2 replicas
                        │  ██
                        └──────────────
                          Replicas
```

> ⚠️ **Prerequisite:** HPA needs the **Metrics Server** installed in the cluster to read Pod CPU and memory metrics.

---

## 📝 Summary

| Concept | Definition |
|---|---|
| **Deployment** | Manages ReplicaSets and Pods. Main resource for stateless applications |
| **ReplicaSet** | Ensures N replicas of a Pod are always active. Created automatically by the Deployment |
| **Rolling Update** | Gradual image update, without downtime |
| **Rollback** | Revert to a previous Deployment version |
| **Scaling** | Increase/decrease replicas manually or via HPA |
| **HPA** | Horizontal Pod Autoscaler — scales replicas based on metrics (CPU, memory) |
| **Strategy** | RollingUpdate (gradual, no downtime) or Recreate (kill all, recreate all) |

---

**Next:** [05 — Services and Networking](05-services-and-networking.md) →
