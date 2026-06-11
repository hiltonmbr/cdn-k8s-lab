# 📖 05 — Services and Networking

> **Objective:** Understand how Pods communicate with each other and with the outside world. Learn about Service types, internal DNS, and Ingress. By the end, you'll know how to expose applications securely and reliably.

---

## 🤔 The Problem: Pods Are Ephemeral

You learned that Pods can be destroyed and recreated at any time. When that happens, they receive **new IPs**:

```bash
# Create a Deployment with 3 replicas
kubectl apply -f deployment-api.yaml

# View Pod IPs
kubectl get pods -o wide
# → NAME                     IP            NODE
# → api-abc123   10.244.1.5   worker-1
# → api-def456   10.244.2.3   worker-2
# → api-ghi789   10.244.1.7   worker-1

# Delete a Pod (K8s recreates it automatically)
kubectl delete pod api-abc123

# View IPs again
kubectl get pods -o wide
# → api-xyz999   10.244.2.8   worker-2  ← NEW IP!
# → api-def456   10.244.2.3   worker-2
# → api-ghi789   10.244.1.7   worker-1
```

**Problem:** If another service needs to access this API, which IP does it point to? The IP changes every time it's recreated!

> 💡 **Analogy:** Imagine if your colleagues' phone numbers changed every time they switched devices. It would be impossible to call anyone. The **Service** is like a "phonebook" with a fixed number that never changes.

---

## 🌐 Service: Stable Virtual Address

A **Service** creates a fixed virtual address (**Cluster IP**) that routes traffic to the correct Pods, regardless of how many exist or which IPs they have:

```yaml
# service-api.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-vendas           # Service name (and DNS entry!)
spec:
  selector:
    app: api-vendas           # "Route traffic to Pods with this label"
  ports:
  - port: 80                  # Service port
    targetPort: 8000           # Container port on the Pods
  type: ClusterIP              # Type (default): accessible only inside the cluster
```

```
              ┌──────────────────────────────────────────┐
              │         Service: api-vendas               │
              │      ClusterIP: 10.96.45.123              │
              │      DNS: api-vendas.default.svc           │
              │                                           │
              │      selector: app=api-vendas              │
              └──────────┬───────────┬───────────┬────────┘
                         │           │           │
                   Load balancing (round-robin)
                         │           │           │
                  ┌──────▼──┐  ┌─────▼───┐  ┌───▼───────┐
                  │ Pod #1  │  │ Pod #2  │  │  Pod #3   │
                  │10.244.  │  │10.244.  │  │10.244.    │
                  │ 1.5     │  │ 2.3     │  │ 1.7       │
                  └─────────┘  └─────────┘  └───────────┘
```

---

## 🏷️ Service Types

### 1. ClusterIP (default) — Internal access

Creates a virtual IP accessible **only within the cluster**. Ideal for inter-service communication:

```yaml
spec:
  type: ClusterIP    # Default — can omit
  ports:
  - port: 80
    targetPort: 8000
```

```
┌─────────────────────────────────────────────────┐
│                   K8s Cluster                    │
│                                                  │
│  Pod A ──► api-vendas:80 ──► Pod B (api-vendas) │
│                                                  │
│  ✅ Works inside the cluster                      │
│  ❌ NOT accessible from your browser              │
└─────────────────────────────────────────────────┘
```

### 2. NodePort — Access via node port

Exposes the Service on a fixed port (30000-32767) on **all cluster nodes**:

```yaml
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 8000
    nodePort: 30001    # Port on the node (30000-32767)
```

```
┌──────────────────────────────────────────────────────────┐
│  Your Browser                                            │
│     │                                                    │
│     │ http://localhost:30001                              │
│     ▼                                                    │
│  ┌─────────────────────────────────────────────────┐     │
│  │  Cluster Node (port 30001)                      │     │
│  │     │                                            │     │
│  │     ▼                                            │     │
│  │  Service (ClusterIP:80)                          │     │
│  │     │                                            │     │
│  │     ├──► Pod #1                                  │     │
│  │     ├──► Pod #2                                  │     │
│  │     └──► Pod #3                                  │     │
│  └─────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

### 3. LoadBalancer — Cloud load balancer

On cloud providers (AWS, GCP, Azure), automatically creates an external load balancer with a public IP:

```yaml
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
```

> ⚠️ **On kind:** The LoadBalancer type does not provision a real external IP (no cloud provider). Use **NodePort** or **port-forward** to access services locally.

### Type summary

| Type | Access | Typical use | Works on kind? |
|---|---|---|---|
| **ClusterIP** | Inside cluster only | Inter-service communication | ✅ Yes |
| **NodePort** | Node IP + port (30000-32767) | Development, testing | ✅ Yes |
| **LoadBalancer** | Public IP (cloud) | Cloud production | ⚠️ Partial |
| **ExternalName** | External DNS (CNAME) | Point to external services | ✅ Yes |

---

## 🌍 Kubernetes Internal DNS

K8s has an internal DNS server that resolves **Service names** to their ClusterIPs. Format:

```
<service-name>.<namespace>.svc.cluster.local
```

In practice, within the **same namespace**, you can use just the name:

```python
# Python — connect to the sales API (same namespace)
import requests
response = requests.get("http://api-vendas:80/health")

# Python — connect to the database in the "database" namespace
import psycopg2
conn = psycopg2.connect(host="postgres.database.svc.cluster.local", ...)
```

```
┌────────────────────────────────────────────────────────┐
│                    K8s Internal DNS                      │
│                                                         │
│  Short name (same namespace):                           │
│    api-vendas  →  10.96.45.123                          │
│                                                         │
│  Full name (different namespace):                       │
│    api-vendas.default.svc.cluster.local → 10.96.45.123 │
│                                                         │
│  Full name (database namespace):                        │
│    postgres.database.svc.cluster.local → 10.96.12.50   │
└────────────────────────────────────────────────────────┘
```

> 💡 **Comparison with Docker:** In Docker Compose, containers on the same network find each other by service name (`postgres`, `redis`). In K8s it's the same — but via **Service**, not via the Pod name.

---

## 🔀 ExternalName: Pointing Outside the Cluster

The **ExternalName** Service type does not route to Pods — it acts as a **DNS alias** for an external service:

```yaml
# postgres-external-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: fullstack
spec:
  type: ExternalName
  externalName: host.docker.internal   # Points to the host (where Docker/PostgreSQL runs)
```

```
┌────────────────────────────────────────────────────────┐
│  K8s Cluster                                           │
│                                                        │
│  Pod (API) ──► "postgres" ──► DNS resolves to          │
│                                host.docker.internal    │
│                                    │                   │
└────────────────────────────────────│───────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────┐
│  Host (your computer)                                  │
│                                                        │
│  PostgreSQL running via Docker (outside the cluster)   │
│  Port: 5432                                            │
└────────────────────────────────────────────────────────┘
```

> 💡 **Real use case:** Your company has a managed database on AWS RDS. The API runs on K8s. Use ExternalName so the API accesses the database by the name `postgres` inside the cluster — if you ever migrate the database into K8s, just change the Service type. The API code **doesn't change**.

---

## 🔌 Port-Forward: Quick Debug Access

The `kubectl port-forward` command creates a temporary tunnel from your computer to a Pod or Service:

```bash
# Forward Pod port
kubectl port-forward pod/api-vendas-abc123 8080:8000
# → http://localhost:8080 accesses the Pod directly

# Forward Service port (load balances across Pods)
kubectl port-forward svc/api-vendas 8080:80
# → http://localhost:8080 accesses via Service

# Forward to a Deployment
kubectl port-forward deployment/api-vendas 8080:8000
```

> ⚠️ **port-forward is for development/debug.** Don't use it in production — the tunnel closes when you stop the command (Ctrl+C). For permanent access, use NodePort or Ingress.

---

## 📝 Summary

| Concept | Definition |
|---|---|
| **Service** | Stable virtual address that routes traffic to Pods via Labels |
| **ClusterIP** | Default type — accessible only inside the cluster |
| **NodePort** | Exposes on the node's port (30000-32767) — external access |
| **LoadBalancer** | Creates a cloud load balancer with a public IP |
| **ExternalName** | DNS alias for services outside the cluster |
| **Internal DNS** | `<service>.<namespace>.svc.cluster.local` |
| **port-forward** | Temporary tunnel for local debugging |

---

**Next:** [06 — Volumes and ConfigMaps](06-volumes-and-configmaps.md) →
