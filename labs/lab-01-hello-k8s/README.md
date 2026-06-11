# 🧪 Lab 01 — Hello K8s: Your First Cluster

> **Objective:** Create a local Kubernetes cluster with kind, run your first Pod, explore it with kubectl, and understand the difference between imperative and declarative modes.

> **Prerequisite:** Docker installed and running. Verify with `docker version`.

> **Estimated time:** 30 minutes

---

## 📋 What you'll practice

- [x] Install kind and kubectl
- [x] Create and destroy local Kubernetes clusters
- [x] Run Pods imperatively and declaratively
- [x] Use `kubectl` to inspect, log, and access Pods
- [x] Understand `port-forward` to access services in the browser

---

## 🔬 Exercise 1: Tool Installation

### Step 1 — Install kind

```bash
# macOS (via Homebrew)
brew install kind

# Linux
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Windows (via Chocolatey)
choco install kind
```

### Step 2 — Install kubectl

```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/kubectl

# Windows
choco install kubernetes-cli
```

### Step 3 — Verify

```bash
kind version
# → kind v0.25.0 ...

kubectl version --client
# → Client Version: v1.31.x
```

> 💡 If both commands returned a version, you're ready!

---

## 🔬 Exercise 2: Your First Cluster

### Step 1 — Create the cluster

```bash
kind create cluster --name hello-k8s
```

Expected output:
```
Creating cluster "hello-k8s" ...
 ✓ Ensuring node image (kindest/node:v1.31.0) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-hello-k8s"
```

### Step 2 — Verify the cluster

```bash
# Cluster info
kubectl cluster-info
# → Kubernetes control plane is running at https://127.0.0.1:xxxxx

# List nodes
kubectl get nodes
# → NAME                     STATUS   ROLES           AGE   VERSION
# → hello-k8s-control-plane  Ready    control-plane   30s   v1.31.0
```

### Step 3 — Peek under the hood

```bash
# kind created a Docker container! See:
docker ps --filter "name=hello-k8s"
# → CONTAINER ID   IMAGE                  NAMES
# → abc123def456   kindest/node:v1.31.0   hello-k8s-control-plane
```

> 💡 **Reflection:** Your entire Kubernetes cluster is running inside a Docker container. It's "Kubernetes inside Docker" — simple and lightweight!

### Step 4 — Explore cluster components

```bash
# View all system Pods (Control Plane)
kubectl get pods -n kube-system
# → NAME                                             READY   STATUS
# → coredns-xxx                                      1/1     Running
# → etcd-hello-k8s-control-plane                     1/1     Running
# → kube-apiserver-hello-k8s-control-plane            1/1     Running
# → kube-controller-manager-hello-k8s-control-plane   1/1     Running
# → kube-scheduler-hello-k8s-control-plane            1/1     Running
# → kindnet-xxx                                       1/1     Running
# → kube-proxy-xxx                                    1/1     Running
```

> 🧠 **Notice:** The API Server, etcd, Scheduler, and Controller Manager we learned about in the documentation are all there, running as Pods in the `kube-system` namespace!

---

## 🔬 Exercise 3: First Pod (Imperative Mode)

### Step 1 — Create an Nginx Pod

```bash
kubectl run meu-nginx --image=nginx:1.27 --port=80
# → pod/meu-nginx created
```

### Step 2 — Verify

```bash
kubectl get pods
# → NAME        READY   STATUS    RESTARTS   AGE
# → meu-nginx   1/1     Running   0          10s
```

### Step 3 — Access in the browser via port-forward

```bash
# Create tunnel: port 8080 on your computer → port 80 on the Pod
kubectl port-forward pod/meu-nginx 8080:80
# → Forwarding from 127.0.0.1:8080 -> 80
```

Open another terminal and test:
```bash
curl http://localhost:8080
# → <!DOCTYPE html>... Welcome to nginx! ...
```

Or open in the browser: **http://localhost:8080** — Welcome to nginx! 🎉

Press `Ctrl+C` in the port-forward terminal to stop.

### Step 4 — Explore the Pod

```bash
# Full Pod details (events, IPs, node, status)
kubectl describe pod meu-nginx

# Nginx logs
kubectl logs meu-nginx

# Enter the Pod (interactive shell)
kubectl exec -it meu-nginx -- bash

# Inside the Pod:
hostname
# → meu-nginx

cat /etc/os-release
# → Debian GNU/Linux 12 (bookworm)

curl localhost:80
# → Welcome to nginx!

exit
```

### Step 5 — Test auto-healing (or lack thereof!)

```bash
# Delete the Pod
kubectl delete pod meu-nginx

# Verify
kubectl get pods
# → No Pods! 😱
```

> ⚠️ **Lesson:** Pods created directly (`kubectl run`) **are not recreated** when they die. For auto-healing, we need Deployments — topic of Lab 02!

---

## 🔬 Exercise 4: First Pod (Declarative Mode — YAML)

Now let's create the same Pod, but using a YAML file:

### Step 1 — Create the YAML file

Create the file `pod-nginx.yaml`:

```yaml
# pod-nginx.yaml — My first declarative Pod
apiVersion: v1
kind: Pod
metadata:
  name: nginx-declarativo
  labels:
    app: nginx
    lab: "01"
spec:
  containers:
  - name: nginx
    image: nginx:1.27
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "50m"
      limits:
        memory: "128Mi"
        cpu: "100m"
```

### Step 2 — Apply the YAML

```bash
kubectl apply -f pod-nginx.yaml
# → pod/nginx-declarativo created
```

### Step 3 — Verify

```bash
kubectl get pods
# → NAME                READY   STATUS    RESTARTS   AGE
# → nginx-declarativo   1/1     Running   0          5s

# View with labels
kubectl get pods --show-labels
# → NAME                LABELS
# → nginx-declarativo   app=nginx,lab=01
```

### Step 4 — Filter by labels

```bash
# List Pods with label app=nginx
kubectl get pods -l app=nginx
# → nginx-declarativo

# List Pods from Lab 01
kubectl get pods -l lab=01
# → nginx-declarativo
```

### Step 5 — Access

```bash
kubectl port-forward pod/nginx-declarativo 8080:80
# Open: http://localhost:8080
# Ctrl+C to stop
```

### Step 6 — Delete via YAML

```bash
kubectl delete -f pod-nginx.yaml
# → pod "nginx-declarativo" deleted
```

> 💡 **Declarative advantage:** The YAML can go to Git, be versioned, reviewed by peers, and applied to any cluster. It's reproducible!

---

## 🔬 Exercise 5: Multi-Node Cluster

Let's create a cluster with 3 nodes to simulate a more realistic environment:

### Step 1 — Delete the previous cluster

```bash
kind delete cluster --name hello-k8s
```

### Step 2 — Create a multi-node cluster

Use the `kind-config.yaml` file from the root of this repository:

```bash
# From the root of cdn-k8s-lab
kind create cluster --name k8s-lab --config kind-config.yaml
```

### Step 3 — Verify the 3 nodes

```bash
kubectl get nodes
# → NAME                    STATUS   ROLES           AGE   VERSION
# → k8s-lab-control-plane   Ready    control-plane   30s   v1.31.0
# → k8s-lab-worker          Ready    <none>          20s   v1.31.0
# → k8s-lab-worker2         Ready    <none>          20s   v1.31.0
```

### Step 4 — View the Docker containers

```bash
docker ps --filter "name=k8s-lab"
# → 3 containers! One for each cluster node.
```

### Step 5 — Create Pods and see distribution

```bash
# Create 3 Pods
kubectl run pod-1 --image=nginx:1.27
kubectl run pod-2 --image=nginx:1.27
kubectl run pod-3 --image=nginx:1.27

# See which node each Pod was assigned to
kubectl get pods -o wide
# → NAME    READY   STATUS    IP           NODE
# → pod-1   1/1     Running   10.244.1.2   k8s-lab-worker
# → pod-2   1/1     Running   10.244.2.3   k8s-lab-worker2
# → pod-3   1/1     Running   10.244.1.4   k8s-lab-worker
```

> 🧠 **Notice:** The K8s Scheduler distributed the Pods among the Workers automatically! It tries to balance the load across nodes.

---

## 🧹 Final Cleanup

```bash
# Delete the test Pods
kubectl delete pod pod-1 pod-2 pod-3

# Keep the k8s-lab cluster for the next Labs!
# Or, if you want to delete everything:
# kind delete cluster --name k8s-lab
```

> 💡 **Tip:** Keep the `k8s-lab` cluster running — you'll use it in the next Labs. If you need to recreate it, just run `kind create cluster --name k8s-lab --config kind-config.yaml` again.

---

## ✅ What we learned

| Concept | Command |
|---|---|
| Create kind cluster | `kind create cluster --name lab` |
| Create multi-node cluster | `kind create cluster --config kind-config.yaml` |
| View cluster nodes | `kubectl get nodes` |
| Create Pod (imperative) | `kubectl run nginx --image=nginx:1.27` |
| Create Pod (declarative) | `kubectl apply -f pod.yaml` |
| Access Pod in browser | `kubectl port-forward pod/name 8080:80` |
| View logs | `kubectl logs name` |
| Enter the Pod | `kubectl exec -it name -- bash` |
| Pod details | `kubectl describe pod name` |
| Filter by labels | `kubectl get pods -l app=nginx` |
| Delete Pod | `kubectl delete pod name` |
| Delete via YAML | `kubectl delete -f pod.yaml` |
| Delete cluster | `kind delete cluster --name lab` |

---

**Next:** [Lab 02 — Deployments in Practice](../lab-02-deployments/README.md) →
