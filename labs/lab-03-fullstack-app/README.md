# 🧪 Lab 03 — Fullstack App: K8s + External DB

> **Objective:** Create a complete application with a Python API running on the K8s cluster and PostgreSQL running **outside** the cluster as a Docker container — simulating the real-world scenario of a managed database (AWS RDS, Google Cloud SQL, dedicated server).

> **Prerequisite:** `k8s-lab` cluster running (Lab 01). Docker installed.

> **Estimated time:** 40 minutes

---

## 📋 What you will practice

- [x] Set up PostgreSQL as an external Docker container (outside K8s)
- [x] Create a Namespace to isolate the project
- [x] Use Secrets to store database credentials
- [x] Create an ExternalName Service to access the external service
- [x] Deploy the Flask API with external database connection
- [x] Deploy pgAdmin to visually manage the database
- [x] Test resilience: delete Pods without losing data

---

## 🏗️ Lab Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Computer (Host)                     │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  K8s Cluster (kind)                                   │  │
│  │  Namespace: fullstack                                 │  │
│  │                                                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐  │  │
│  │  │ Pod: API   │  │ Pod: API   │  │ Pod: pgAdmin   │  │  │
│  │  │ Flask #1   │  │ Flask #2   │  │                │  │  │
│  │  └─────┬──────┘  └─────┬──────┘  └───────┬────────┘  │  │
│  │        │               │                  │           │  │
│  │  ┌─────▼───────────────▼──────────────────▼────────┐  │  │
│  │  │     Service: postgres (ExternalName)             │  │  │
│  │  │     → resolves to host.docker.internal           │  │  │
│  │  └─────────────────────┬───────────────────────────┘  │  │
│  └────────────────────────│──────────────────────────────┘  │
│                           │                                  │
│                    ┌──────▼───────┐                          │
│                    │ PostgreSQL   │  ← Docker Container      │
│                    │ (external)   │     OUTSIDE the cluster   │
│                    │ port: 5432   │                          │
│                    └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

> 💡 **Why this pattern?** In production, databases almost **never** run inside the K8s cluster. They run on managed services (AWS RDS, Cloud SQL) or dedicated servers. This separates **stateless** (API, which scales easily) from **stateful** (database, which needs special data care).

---

## 🔬 Exercise 1: Start the External PostgreSQL

### Step 1 — Start PostgreSQL via Docker (outside the cluster)

```bash
docker run -d \
  --name postgres-externo \
  -e POSTGRES_PASSWORD=senha123 \
  -e POSTGRES_DB=escola \
  -p 5432:5432 \
  postgres:16
```

### Step 2 — Verify it's running

```bash
docker ps --filter "name=postgres-externo"
# → STATUS: Up X seconds

# Test connection directly
docker exec -it postgres-externo psql -U postgres -d escola -c "SELECT 1"
# → 1
```

> 🧠 **Notice:** PostgreSQL is running as a regular **Docker** container, outside the K8s cluster. It doesn't know K8s exists. It's an independent database server.

---

## 🔬 Exercise 2: Prepare the K8s Resources

### Step 1 — Build the API image

```bash
cd labs/lab-03-fullstack-app/app

docker build -t api-escola:1.0 .
kind load docker-image api-escola:1.0 --name k8s-lab

cd ../../..
```

### Step 2 — Create the Namespace

```bash
kubectl apply -f labs/lab-03-fullstack-app/manifests/namespace.yaml
# → namespace/fullstack created

# Verify
kubectl get namespaces
# → NAME          STATUS   AGE
# → default       Active   ...
# → fullstack     Active   5s  ← Our namespace!
# → kube-system   Active   ...
```

### Step 3 — Create the Secret with credentials

```bash
kubectl apply -f labs/lab-03-fullstack-app/manifests/postgres-secret.yaml
# → secret/postgres-secret created

# Verify (content is Base64, not plain text)
kubectl get secret postgres-secret -n fullstack -o yaml
```

### Step 4 — Create the ExternalName Service

```bash
kubectl apply -f labs/lab-03-fullstack-app/manifests/postgres-external-service.yaml
# → service/postgres created

# Verify
kubectl get svc -n fullstack
# → NAME       TYPE           CLUSTER-IP   EXTERNAL-IP              PORT(S)   AGE
# → postgres   ExternalName   <none>       host.docker.internal     <none>    5s
```

> 💡 **What happened?** We created a "DNS alias" inside the cluster. When any Pod in the `fullstack` namespace accesses the hostname `postgres`, K8s DNS resolves it to `host.docker.internal`, which is your computer's IP — where PostgreSQL is running!

---

## 🔬 Exercise 3: Deploy the API

### Step 1 — Apply the API Deployment and Service

```bash
kubectl apply -f labs/lab-03-fullstack-app/manifests/api-deployment.yaml
kubectl apply -f labs/lab-03-fullstack-app/manifests/api-service.yaml
```

### Step 2 — Verify the Pods

```bash
kubectl get pods -n fullstack
# → NAME                         READY   STATUS    RESTARTS   AGE
# → api-escola-xxx-abc12         1/1     Running   0          10s
# → api-escola-xxx-def34         1/1     Running   0          10s
```

### Step 3 — Test the API

```bash
# Access via NodePort
curl http://localhost:30002 | python3 -m json.tool
# → {
# →   "app": "API Escola — K8s Lab",
# →   "database": "host.docker.internal:5432/escola",
# →   "endpoints": ["/alunos", "/alunos/<id>", "/health"],
# →   ...
# → }

# Health check (verifies database connection)
curl http://localhost:30002/health | python3 -m json.tool
# → {"database": "connected", "status": "healthy"}

# List students (pre-inserted data)
curl http://localhost:30002/alunos | python3 -m json.tool
# → {"alunos": [...], "total": 5}
```

### Step 4 — Insert a new student via API

```bash
curl -X POST http://localhost:30002/alunos \
  -H "Content-Type: application/json" \
  -d '{"nome": "Kubernetes Aluno", "email": "k8s@lab.com", "nota": 9.9}'
# → {"id": 6, "nome": "Kubernetes Aluno", "email": "k8s@lab.com", "nota": "9.90"}

# Verify it was inserted
curl http://localhost:30002/alunos | python3 -m json.tool
# → total: 6 ← New student appears!
```

---

## 🔬 Exercise 4: Deploy pgAdmin

### Step 1 — Apply the pgAdmin Deployment

```bash
kubectl apply -f labs/lab-03-fullstack-app/manifests/pgadmin-deployment.yaml
```

### Step 2 — Wait (pgAdmin is heavy, may take a while)

```bash
kubectl get pods -n fullstack --watch
# Wait until the pgAdmin Pod is "Running"
```

### Step 3 — Access pgAdmin

```bash
# Port-forward to access in the browser
kubectl port-forward svc/pgadmin -n fullstack 5050:80
# → Forwarding from 127.0.0.1:5050 -> 80
```

Open: **http://localhost:5050**

- **Email:** admin@lab.com
- **Password:** admin123

### Step 4 — Connect to PostgreSQL in pgAdmin

1. Click **"Add New Server"**
2. In **General** tab: Name = `PostgreSQL Externo`
3. In **Connection** tab:
   - **Host:** `host.docker.internal`
   - **Port:** `5432`
   - **Database:** `escola`
   - **Username:** `postgres`
   - **Password:** `senha123`
4. Click **Save**

Now you can browse tables, view student data, and run SQL queries directly!

---

## 🔬 Exercise 5: Testing Resilience

### Test 1 — Delete API Pods (data persists!)

```bash
# Delete ALL API Pods
kubectl delete pods -l app=api-escola -n fullstack

# Verify: K8s recreates automatically
kubectl get pods -n fullstack --watch

# Test: the database data is intact!
curl http://localhost:30002/alunos | python3 -m json.tool
# → The student "Kubernetes Aluno" is still there! 🎉
```

> 🧠 **Why?** The database is **outside** the cluster. Deleting API Pods does not affect the database. New Pods reconnect automatically.

### Test 2 — Scale the API

```bash
# Scale to 5 replicas
kubectl scale deployment api-escola --replicas=5 -n fullstack

# Verify
kubectl get pods -n fullstack -l app=api-escola
# → 5 Pods running!

# Test load balancing
for i in {1..5}; do curl -s http://localhost:30002 | python3 -m json.tool | grep pod; done
# → Different hostnames each request (load balancing)

# Back to 2 replicas
kubectl scale deployment api-escola --replicas=2 -n fullstack
```

### Test 3 — Stop and restart PostgreSQL

```bash
# Stop the external database
docker stop postgres-externo

# Test the API
curl http://localhost:30002/health
# → {"status": "unhealthy", "error": "..."} ← API detects the failure!

# Restart the database
docker start postgres-externo

# Test again
curl http://localhost:30002/health
# → {"status": "healthy", "database": "connected"} ← Automatic reconnection!

# Did the data persist?
curl http://localhost:30002/alunos | python3 -m json.tool
# → All students are still there (including "Kubernetes Aluno") ✅
```

---

## 🧹 Cleanup

```bash
# Remove ALL resources from the fullstack namespace
kubectl delete namespace fullstack
# → This removes: Deployment, Service, Secret, Pods — everything!

# Remove the external PostgreSQL
docker rm -f postgres-externo

# Verify
kubectl get all -n fullstack
# → "No resources found" ✅
```

---

## ✅ What we learned

| Concept | What we did |
|---|---|
| **External PostgreSQL** | Database running outside the cluster (production pattern) |
| **Namespace** | Logical resource isolation (`fullstack`) |
| **Secret** | Database credentials securely stored |
| **ExternalName Service** | DNS alias inside K8s for external services |
| **Stateless/stateful separation** | API scales on K8s, database stays protected outside |
| **Resilience** | Pods die and recreate without losing database data |
| **pgAdmin** | Visual interface to manage the database from inside the cluster |

---

**Next:** [Lab 04 — Spark on K8s](../lab-04-spark-on-k8s/README.md) →
