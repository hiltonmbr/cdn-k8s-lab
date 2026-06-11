# 🧪 Lab 02 — Deployments in Practice

> **Objective:** Create Deployments, scale replicas, perform rolling updates and rollbacks. This lab demonstrates why Deployments are the most important K8s resource for stateless applications.

> **Prerequisite:** `k8s-lab` cluster running (Lab 01). Docker installed.

> **Estimated time:** 30 minutes

---

## 📋 What you will practice

- [x] Build a Docker image and load it into the kind cluster
- [x] Create a Deployment with 3 replicas
- [x] Test auto-healing (delete Pods and watch recreation)
- [x] Scale replicas manually
- [x] Expose the Deployment via a NodePort Service
- [x] Perform a rolling update (update API version)
- [x] Rollback to the previous version

---

## 🔬 Exercise 1: Preparation — Build the Image

### Step 1 — Build the API Docker image

```bash
# From the root of cdn-k8s-lab
cd labs/lab-02-deployments/app

# Build the image version 1.0
docker build -t api-vendas:1.0 .
# → Successfully tagged api-vendas:1.0
```

### Step 2 — Load the image into the kind cluster

kind uses its own image registry. We need to **load** the local image into the cluster:

```bash
# Load image into the kind cluster
kind load docker-image api-vendas:1.0 --name k8s-lab
# → Image: "api-vendas:1.0" with ID "sha256:..." loaded
```

> 💡 **Why is this necessary?** The kind cluster runs inside Docker containers. It doesn't have direct access to images on your host Docker Engine. The `kind load` command copies the image into the cluster nodes.

### Step 3 — Verify

```bash
# Go back to the lab root
cd ../../..
```

---

## 🔬 Exercise 2: First Deployment

### Step 1 — Create the Deployment

```bash
kubectl apply -f labs/lab-02-deployments/manifests/api-deployment.yaml
# → deployment.apps/api-vendas created
```

### Step 2 — Watch the creation in real time

```bash
# In a separate terminal, watch the Pods being created:
kubectl get pods --watch
# → NAME                         READY   STATUS              RESTARTS   AGE
# → api-vendas-7d8f9b6c5-abc12   0/1     ContainerCreating   0          1s
# → api-vendas-7d8f9b6c5-def34   0/1     ContainerCreating   0          1s
# → api-vendas-7d8f9b6c5-ghi56   0/1     ContainerCreating   0          1s
# → api-vendas-7d8f9b6c5-abc12   1/1     Running             0          3s
# → api-vendas-7d8f9b6c5-def34   1/1     Running             0          4s
# → api-vendas-7d8f9b6c5-ghi56   1/1     Running             0          4s
# Ctrl+C to stop
```

### Step 3 — Inspect the hierarchy

```bash
# Deployment
kubectl get deployments
# → NAME         READY   UP-TO-DATE   AVAILABLE   AGE
# → api-vendas   3/3     3            3           30s

# ReplicaSet (created automatically by the Deployment)
kubectl get replicasets
# → NAME                    DESIRED   CURRENT   READY   AGE
# → api-vendas-7d8f9b6c5   3         3         3       30s

# Pods (created automatically by the ReplicaSet)
kubectl get pods -o wide
# → Observe: the Pods are distributed across the Worker Nodes!
```

> 🧠 **Hierarchy:** Deployment → ReplicaSet → Pods. You only created the Deployment, and it created everything else automatically!

---

## 🔬 Exercise 3: Auto-Healing

### Step 1 — Delete a Pod and observe

```bash
# Get the name of one of the Pods
POD_NAME=$(kubectl get pods -l app=api-vendas -o jsonpath='{.items[0].metadata.name}')

# Delete the Pod
kubectl delete pod $POD_NAME
# → pod "api-vendas-7d8f9b6c5-abc12" deleted

# IMMEDIATELY check:
kubectl get pods
# → A new Pod is being created! 🎉
# → api-vendas-7d8f9b6c5-xyz99   0/1   ContainerCreating   0   2s
# → api-vendas-7d8f9b6c5-def34   1/1   Running             0   2m
# → api-vendas-7d8f9b6c5-ghi56   1/1   Running             0   2m
```

> 💡 **This is auto-healing!** The ReplicaSet noticed there were 2 Pods (desired: 3) and created a new one automatically. No human intervention.

### Step 2 — Test extreme resilience

```bash
# Delete ALL Pods at once!
kubectl delete pods -l app=api-vendas

# Check immediately
kubectl get pods --watch
# → All being recreated automatically! K8s ALWAYS maintains 3 replicas.
```

---

## 🔬 Exercise 4: Scaling

### Step 1 — Scale to 5 replicas

```bash
kubectl scale deployment api-vendas --replicas=5

# Verify
kubectl get pods
# → Now there are 5 Pods!
```

### Step 2 — Reduce to 2 replicas

```bash
kubectl scale deployment api-vendas --replicas=2

# Verify: excess Pods being terminated
kubectl get pods --watch
# → 3 Pods in "Terminating" state
```

### Step 3 — Back to 3 replicas

```bash
kubectl scale deployment api-vendas --replicas=3
```

---

## 🔬 Exercise 5: Service — Exposing the API

### Step 1 — Create the Service

```bash
kubectl apply -f labs/lab-02-deployments/manifests/api-service.yaml
# → service/api-vendas created
```

### Step 2 — Verify

```bash
kubectl get services
# → NAME         TYPE       CLUSTER-IP     PORT(S)        AGE
# → api-vendas   NodePort   10.96.xx.xx    80:30001/TCP   5s
```

### Step 3 — Access the API

```bash
# Access via NodePort
curl http://localhost:30001
# → {"app":"API de Vendas","hostname":"api-vendas-7d8f9b6c5-abc12","version":"1.0",...}

# Call multiple times — notice the hostname changing!
for i in {1..6}; do curl -s http://localhost:30001 | python3 -m json.tool | grep hostname; done
# → "hostname": "api-vendas-7d8f9b6c5-abc12"
# → "hostname": "api-vendas-7d8f9b6c5-def34"  ← Different Pod!
# → "hostname": "api-vendas-7d8f9b6c5-ghi56"  ← Another Pod!
# → "hostname": "api-vendas-7d8f9b6c5-abc12"
# → ...
```

> 🧠 **Load Balancing!** The Service distributes requests across the 3 Pods automatically (round-robin). Each response comes from a different Pod!

### Step 4 — View sales data

```bash
curl http://localhost:30001/vendas | python3 -m json.tool
# → { "vendas": [...], "total": 6650.0 }

curl http://localhost:30001/health | python3 -m json.tool
# → { "status": "healthy", "version": "1.0" }
```

---

## 🔬 Exercise 6: Rolling Update

Let's update the API from version 1.0 to 2.0 **without downtime**!

### Step 1 — Build version 2.0

Edit the file `labs/lab-02-deployments/app/app.py` and change the `VERSION` variable:

```python
VERSION = os.environ.get("APP_VERSION", "2.0")  # ← Change from 1.0 to 2.0
```

And add a new endpoint:

```python
@app.route("/v2/info")
def info_v2():
    return jsonify({"message": "Endpoint novo da v2!", "pod": socket.gethostname()})
```

```bash
# Rebuild with new tag
cd labs/lab-02-deployments/app
docker build -t api-vendas:2.0 .

# Load into the cluster
kind load docker-image api-vendas:2.0 --name k8s-lab

cd ../../..
```

### Step 2 — Trigger rolling update

```bash
# In one terminal, watch the Pods:
kubectl get pods --watch

# In another terminal, update the image:
kubectl set image deployment/api-vendas api=api-vendas:2.0
```

### Step 3 — Observe the rolling update

```bash
# Update status
kubectl rollout status deployment api-vendas
# → Waiting for rollout to finish: 1 out of 3 new replicas have been updated...
# → Waiting for rollout to finish: 2 out of 3 new replicas have been updated...
# → deployment "api-vendas" successfully rolled out ✅

# Verify the version
curl http://localhost:30001 | python3 -m json.tool
# → "version": "2.0" ← Updated!
```

### Step 4 — View the history

```bash
kubectl rollout history deployment api-vendas
# → REVISION  CHANGE-CAUSE
# → 1         <none>
# → 2         <none>
```

---

## 🔬 Exercise 7: Rollback

Oops! Version 2.0 has a bug. Let's revert to 1.0:

### Step 1 — Execute rollback

```bash
kubectl rollout undo deployment api-vendas
# → deployment.apps/api-vendas rolled back
```

### Step 2 — Verify

```bash
# Wait for rollback to complete
kubectl rollout status deployment api-vendas

# Test
curl http://localhost:30001 | python3 -m json.tool
# → "version": "1.0" ← Back to version 1.0! 🎉
```

> 💡 **How it works:** K8s keeps the old ReplicaSets (with 0 replicas). On rollback, it scales the old ReplicaSet back up. Pods from version 2.0 are terminated and those from 1.0 are recreated. All automatic!

```bash
# Verify: two ReplicaSets exist
kubectl get replicasets
# → NAME                    DESIRED   CURRENT   READY
# → api-vendas-7d8f9b6c5   3         3         3     ← v1.0 (active)
# → api-vendas-a1b2c3d4e   0         0         0     ← v2.0 (inactive)
```

---

## 🧹 Cleanup

```bash
# Remove Deployment and Service
kubectl delete -f labs/lab-02-deployments/manifests/

# Verify
kubectl get all
# → Only system services

# (Optional) Remove images
docker rmi api-vendas:1.0 api-vendas:2.0
```

---

## ✅ What we learned

| Concept | Command |
|---|---|
| Build + load to kind | `docker build -t img:tag .` + `kind load docker-image img:tag` |
| Create Deployment | `kubectl apply -f deployment.yaml` |
| View hierarchy | `kubectl get deploy,rs,pods` |
| Auto-healing | Delete Pod → K8s recreates automatically |
| Scale | `kubectl scale deployment app --replicas=N` |
| Expose via Service | `kubectl apply -f service.yaml` (NodePort) |
| Load balancing | Service distributes traffic across Pods |
| Rolling update | `kubectl set image deployment/app container=img:new-tag` |
| View rollout | `kubectl rollout status deployment app` |
| Rollback | `kubectl rollout undo deployment app` |
| History | `kubectl rollout history deployment app` |

---

**Next:** [Lab 03 — Fullstack App (K8s + External DB)](../lab-03-app-fullstack/README.md) →
