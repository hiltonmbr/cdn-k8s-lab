# 🧪 Lab 04 — Spark on K8s: Big Data on the Cluster

> **Objective:** Run Apache Spark inside the Kubernetes cluster — deploy Spark Master + Workers, submit processing jobs, and observe scalability. This is the direct link between K8s and the Big Data world.

> **Prerequisite:** `k8s-lab` cluster running (Lab 01). 8 GB free RAM recommended.

> **Estimated time:** 35 minutes

---

## 📋 What you will practice

- [x] Create an isolated namespace for Spark
- [x] Configure RBAC (permissions) for Spark
- [x] Deploy Spark Master and Workers on K8s
- [x] Access the Spark Master Web UI
- [x] Submit a PySpark job (WordCount)
- [x] Scale Workers and observe the impact
- [x] Monitor Pods with kubectl

---

## 🏗️ Lab Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  K8s Cluster (kind) — Namespace: spark                       │
│                                                              │
│  ┌────────────────────┐                                      │
│  │   Spark Master     │  ← Coordinates jobs and Workers       │
│  │   (Pod)            │                                      │
│  │   Port: 7077       │  ← Communication with Workers         │
│  │   Web UI: 8080     │  ← Spark Dashboard                   │
│  └────────┬───────────┘                                      │
│           │                                                  │
│     ┌─────┴──────┐                                           │
│     │            │                                           │
│  ┌──▼──────┐  ┌──▼──────┐                                   │
│  │ Worker  │  │ Worker  │  ← Execute job tasks                │
│  │  #1     │  │  #2     │                                    │
│  │ 512m    │  │ 512m    │  ← Allocated memory                 │
│  │ 1 core  │  │ 1 core  │  ← Allocated CPU                   │
│  └─────────┘  └─────────┘                                    │
│                                                              │
│  Scalable: kubectl scale deployment spark-worker --replicas=4 │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔬 Exercise 1: Prepare the Environment

### Step 1 — Create the Namespace

```bash
kubectl apply -f labs/lab-04-spark-on-k8s/manifests/spark-namespace.yaml
# → namespace/spark created
```

### Step 2 — Configure RBAC

```bash
kubectl apply -f labs/lab-04-spark-on-k8s/manifests/spark-rbac.yaml
# → serviceaccount/spark created
# → role.rbac.authorization.k8s.io/spark-role created
# → rolebinding.rbac.authorization.k8s.io/spark-role-binding created
```

> 💡 **RBAC (Role-Based Access Control)** defines who can do what in the cluster. Spark needs permission to create and manage Executor Pods dynamically.

---

## 🔬 Exercise 2: Deploy Spark Master

### Step 1 — Create the Master

```bash
kubectl apply -f labs/lab-04-spark-on-k8s/manifests/spark-master.yaml
# → deployment.apps/spark-master created
# → service/spark-master created
```

### Step 2 — Verify

```bash
kubectl get pods -n spark
# → NAME                            READY   STATUS    RESTARTS   AGE
# → spark-master-xxx-abc12          1/1     Running   0          20s
```

### Step 3 — Access the Spark Web UI

```bash
kubectl port-forward svc/spark-master -n spark 4040:8080
# → Forwarding from 127.0.0.1:4040 -> 8080
```

Open: **http://localhost:4040** — Spark Master UI! 🎉

You will see:
- **Workers:** 0 (none yet)
- **Applications:** None running
- **Status:** ALIVE

> Keep this port-forward running in a separate terminal.

---

## 🔬 Exercise 3: Deploy Workers

### Step 1 — Create the Workers

```bash
kubectl apply -f labs/lab-04-spark-on-k8s/manifests/spark-worker.yaml
# → deployment.apps/spark-worker created
```

### Step 2 — Verify

```bash
kubectl get pods -n spark
# → NAME                            READY   STATUS    RESTARTS   AGE
# → spark-master-xxx-abc12          1/1     Running   0          1m
# → spark-worker-xxx-def34          1/1     Running   0          10s
# → spark-worker-xxx-ghi56          1/1     Running   0          10s
```

### Step 3 — Verify in the Web UI

Reload **http://localhost:4040**:
- **Workers:** 2 ← Workers registered with the Master!
- **Cores in use:** 2
- **Memory in use:** 1.0 GiB

### Step 4 — See the distribution across nodes

```bash
kubectl get pods -n spark -o wide
# → NAME              NODE
# → spark-master-...  k8s-lab-worker
# → spark-worker-...  k8s-lab-worker2  ← Distributed by the Scheduler!
# → spark-worker-...  k8s-lab-worker
```

---

## 🔬 Exercise 4: Submit a PySpark Job

### Step 1 — Copy the job into the Master

```bash
# Get the Master Pod name
MASTER_POD=$(kubectl get pods -n spark -l app=spark-master -o jsonpath='{.items[0].metadata.name}')

# Copy the wordcount.py script into the Pod
kubectl cp labs/lab-04-spark-on-k8s/jobs/wordcount.py spark/$MASTER_POD:/tmp/wordcount.py
```

### Step 2 — Submit the job via spark-submit

```bash
kubectl exec -it $MASTER_POD -n spark -- \
  spark-submit \
    --master spark://spark-master:7077 \
    /tmp/wordcount.py
```

### Step 3 — Observe the execution

The output will show the WordCount processing:

```
============================================================
🚀 WordCount — Spark on Kubernetes
============================================================

📊 Top 15 most frequent words:
----------------------------------------
+-------------+-----+
|word         |count|
+-------------+-----+
|kubernetes   |6    |
|de           |6    |
|spark        |5    |
|dados        |5    |
|contêineres  |3    |
|docker       |3    |
|em           |3    |
|...          |...  |
+-------------+-----+

📈 Total words: 73
📈 Unique words: 38
============================================================
```

> 🧠 **What happened?** The Spark Driver ran inside the Master Pod, distributed tasks to the 2 Workers, processed data in parallel, and aggregated results. All inside Kubernetes!

---

## 🔬 Exercise 5: Scale Workers

### Step 1 — Scale to 4 Workers

```bash
kubectl scale deployment spark-worker --replicas=4 -n spark

# Verify
kubectl get pods -n spark
# → 4 Workers running!
```

### Step 2 — Verify in the Web UI

Reload http://localhost:4040:
- **Workers:** 4 ← Scaled!
- **Cores:** 4
- **Memory:** 2.0 GiB

### Step 3 — Submit the job again and compare

```bash
kubectl exec -it $MASTER_POD -n spark -- \
  spark-submit \
    --master spark://spark-master:7077 \
    /tmp/wordcount.py
```

### Step 4 — Reduce Workers

```bash
kubectl scale deployment spark-worker --replicas=1 -n spark

# Verify: excess Pods terminating
kubectl get pods -n spark --watch
```

> 💡 **This is the power of Spark on K8s!** In real environments, the Horizontal Pod Autoscaler (HPA) would automatically scale Workers based on workload. No manual provisioning.

---

## 🔬 Exercise 6: Monitor with kubectl

### View logs in real time

```bash
# Master logs
kubectl logs -f $(kubectl get pods -n spark -l app=spark-master -o jsonpath='{.items[0].metadata.name}') -n spark

# Worker logs
kubectl logs -f $(kubectl get pods -n spark -l app=spark-worker -o jsonpath='{.items[0].metadata.name}') -n spark
```

### View resource usage

```bash
# Pod details (events, resources)
kubectl describe pod $MASTER_POD -n spark

# View all resources in the spark namespace
kubectl get all -n spark
```

---

## 🧹 Cleanup

```bash
# Stop port-forward (Ctrl+C)

# Remove everything from the spark namespace
kubectl delete namespace spark

# Verify
kubectl get all -n spark
# → "No resources found" ✅
```

---

## ✅ What we learned

| Concept | What we did |
|---|---|
| **Namespace** | Spark environment isolation (`spark`) |
| **RBAC** | Permissions for Spark to create Executor Pods |
| **Spark Master** | Spark cluster coordinator, running as a Pod |
| **Spark Workers** | Task executors, managed as a Deployment |
| **spark-submit** | Submitting PySpark jobs inside the K8s cluster |
| **Scaling** | Scale Workers from 2 to 4 and back with one command |
| **Web UI** | Spark Dashboard accessible via port-forward |
| **kubectl cp** | Copy files into Pods |

### 🔗 Big Data Relationship

| Before (YARN/Hadoop) | Now (Spark on K8s) |
|---|---|
| Fixed, pre-allocated cluster | Pods created on demand |
| Idle capacity during jobless periods | Resources released when jobs finish |
| Difficult to scale (add machines) | `kubectl scale` or automatic HPA |
| Separate infrastructure per tool | Spark, Kafka, Airflow on the same K8s cluster |

---

**Next:** [Lab 05 — Dashboard and Monitoring](../lab-05-dashboard-e-monitoring/README.md) →
