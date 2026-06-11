# 📖 06 — Volumes, ConfigMaps, and Secrets

> **Objective:** Learn how to persist data, externalize configurations, and manage sensitive information in Kubernetes. By the end, you'll understand PVs, PVCs, ConfigMaps, and Secrets — the mechanisms that separate data and configuration from code.

---

## 💾 The Problem: Ephemeral Data

Just like in Docker, everything written inside a K8s container is **ephemeral** — when the Pod dies, the data dies with it:

```bash
# Create a Pod with PostgreSQL
kubectl run pg --image=postgres:16 --env="POSTGRES_PASSWORD=password"

# Create data in the database...

# Delete the Pod (K8s recreates via Deployment)
kubectl delete pod pg

# New Pod created automatically — but without the data! 😱
```

To persist data, we need **Volumes**.

---

## 📦 Volumes in Kubernetes vs Docker

| Docker | Kubernetes |
|---|---|
| `docker run -v pgdata:/var/lib/...` | PersistentVolumeClaim (PVC) |
| Volume managed by Docker Engine | Volume managed by the cluster |
| Exists on the host filesystem | Can be local disk, NFS, EBS, etc. |
| Simple and direct | Decoupled: PV → PVC → Pod |

### Volume Architecture in K8s

```
┌───────────────────────────────────────────────────────────┐
│                                                           │
│  Administrator                    Developer                │
│  (provisions storage)            (requests storage)       │
│                                                           │
│  ┌──────────────────┐      ┌──────────────────────┐      │
│  │ PersistentVolume │ ◄──► │ PersistentVolumeClaim│      │
│  │      (PV)        │ bind │       (PVC)           │      │
│  │                  │      │                       │      │
│  │ Capacity: 10Gi   │      │ I need: 5Gi          │      │
│  │ Type: hostPath   │      │ Access: ReadWriteOnce│      │
│  └──────────────────┘      └───────────┬──────────┘      │
│                                         │                 │
│                                    mounted on             │
│                                         │                 │
│                                    ┌────▼─────┐          │
│                                    │   Pod    │          │
│                                    │ /data ◄──│── volume │
│                                    └──────────┘          │
└───────────────────────────────────────────────────────────┘
```

---

## 💾 PersistentVolume (PV) and PersistentVolumeClaim (PVC)

### PersistentVolume (PV) — The "disk"

Storage resource **provisioned by the administrator** (or automatically via StorageClass):

```yaml
# pv-local.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-dados
spec:
  capacity:
    storage: 5Gi               # Total capacity
  accessModes:
    - ReadWriteOnce             # One Pod can read/write at a time
  hostPath:
    path: /data/k8s-volumes     # Path on the node (dev/kind only)
```

### PersistentVolumeClaim (PVC) — The "request"

Storage request **made by the developer**:

```yaml
# pvc-dados.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dados-postgres
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi             # "I need at least 2 GiB"
```

### Using the PVC in a Pod

```yaml
# pod-com-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: postgres
spec:
  containers:
  - name: postgres
    image: postgres:16
    env:
    - name: POSTGRES_PASSWORD
      value: "senha123"
    volumeMounts:
    - name: pg-storage
      mountPath: /var/lib/postgresql/data  # Where to mount the volume
  volumes:
  - name: pg-storage
    persistentVolumeClaim:
      claimName: dados-postgres            # PVC name
```

### Access Modes

| Mode | Abbreviation | Description |
|---|---|---|
| **ReadWriteOnce** | RWO | A single node can read/write |
| **ReadOnlyMany** | ROX | Multiple nodes can read (read-only) |
| **ReadWriteMany** | RWX | Multiple nodes can read/write (NFS, Ceph) |

> 💡 **On kind:** We use `hostPath` as the storage backend — simple and functional for learning. In production, the backend would be AWS EBS, GCP Persistent Disk, or Ceph.

---

## ⚡ StorageClass: Dynamic Provisioning

Instead of manually creating PVs, **StorageClass** automatically provisions volumes when a PVC is created:

```yaml
# kind already comes with a default StorageClass called "standard"
# Just create the PVC — the PV is created automatically!

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dados-auto
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  # storageClassName: standard   ← Default in kind, can omit
```

```bash
# View available StorageClasses
kubectl get storageclass
# → NAME                 PROVISIONER             AGE
# → standard (default)   rancher.io/local-path   1h
```

---

## 📋 ConfigMaps: Externalized Configurations

**ConfigMaps** store non-sensitive configurations outside of containers. Advantage: change the configuration **without rebuilding the Docker image**.

### Creating a ConfigMap

```yaml
# configmap-app.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: config-api
data:
  # Simple key-value pairs
  DATABASE_HOST: "postgres"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "vendas"
  LOG_LEVEL: "INFO"

  # Complete configuration file
  app.conf: |
    [server]
    host = 0.0.0.0
    port = 8000
    workers = 4
```

### Using ConfigMap as environment variables

```yaml
spec:
  containers:
  - name: api
    image: minha-api:1.0
    envFrom:
    - configMapRef:
        name: config-api        # All keys become environment variables
```

### Using ConfigMap as a mounted file

```yaml
spec:
  containers:
  - name: api
    image: minha-api:1.0
    volumeMounts:
    - name: config-volume
      mountPath: /app/config      # Mounts the ConfigMap as a directory
  volumes:
  - name: config-volume
    configMap:
      name: config-api
```

```bash
# Create ConfigMap via terminal
kubectl create configmap config-api \
  --from-literal=DATABASE_HOST=postgres \
  --from-literal=LOG_LEVEL=INFO

# Create ConfigMap from a file
kubectl create configmap config-app --from-file=app.conf
```

---

## 🗝️ Secrets: Sensitive Data

**Secrets** store sensitive data (passwords, tokens, certificates) encoded in Base64:

### Creating a Secret

```yaml
# secret-db.yaml
apiVersion: v1
kind: Secret
metadata:
  name: secret-postgres
type: Opaque
data:
  # Base64-encoded values
  # echo -n "senha123" | base64  →  c2VuaGExMjM=
  POSTGRES_PASSWORD: c2VuaGExMjM=
  POSTGRES_USER: cG9zdGdyZXM=
```

### Creating a Secret via terminal (more practical)

```bash
# kubectl encodes in Base64 automatically
kubectl create secret generic secret-postgres \
  --from-literal=POSTGRES_PASSWORD=senha123 \
  --from-literal=POSTGRES_USER=postgres
```

### Using Secret as environment variables

```yaml
spec:
  containers:
  - name: api
    image: minha-api:1.0
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: secret-postgres
          key: POSTGRES_PASSWORD
```

### Using Secret as a mounted volume

```yaml
spec:
  containers:
  - name: api
    volumeMounts:
    - name: secret-volume
      mountPath: /app/secrets
      readOnly: true              # Best practice: read-only
  volumes:
  - name: secret-volume
    secret:
      secretName: secret-postgres
```

> ⚠️ **Base64 is NOT encryption!** Secrets are Base64-encoded by default, which is reversible. In production, use solutions like **Sealed Secrets**, **Vault**, or **SOPS** for real encryption. And **never version Secrets in Git!**

---

## 🆚 ConfigMap vs Secret

| Aspect | ConfigMap | Secret |
|---|---|---|
| **Purpose** | Non-sensitive configurations | Sensitive data |
| **Encoding** | Plain text | Base64 |
| **Examples** | URLs, flags, .conf files | Passwords, tokens, SSH keys |
| **Maximum size** | 1 MiB | 1 MiB |
| **Git** | ✅ Can version | ❌ Never version |
| **Usage in Pods** | envFrom, volumeMount | env.valueFrom, volumeMount |

---

## 📝 Summary

| Concept | Definition |
|---|---|
| **PersistentVolume (PV)** | Storage resource provisioned in the cluster |
| **PersistentVolumeClaim (PVC)** | Storage request made by a Pod |
| **StorageClass** | Automatically provisions PVs when PVCs are created |
| **ConfigMap** | Stores externalized non-sensitive configurations |
| **Secret** | Stores sensitive data encoded in Base64 |
| **hostPath** | Volume backend using a node directory (dev only) |
| **envFrom** | Injects ConfigMap/Secret as environment variables |
| **volumeMount** | Mounts ConfigMap/Secret as a file in the filesystem |

---

**Next:** [07 — kubectl Cheatsheet](07-kubectl-cheatsheet.md) →
