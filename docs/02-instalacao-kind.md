# 📖 02 — Installation: kind, kubectl, and Tools

> **Objective:** Install and configure all the necessary tools to run a local Kubernetes cluster on your computer. By the end, you'll have a functional K8s cluster with 3 nodes.

---

## 🧰 What We're Going to Install

| Tool | What it is | Why we need it |
|---|---|---|
| **[kind](https://kind.sigs.k8s.io/)** | Kubernetes IN Docker — creates K8s clusters using Docker containers as nodes | The lightest way to run K8s locally. No VMs! |
| **[kubectl](https://kubernetes.io/docs/tasks/tools/)** | Official Kubernetes CLI | To interact with the cluster (create, list, delete resources) |
| **[k9s](https://k9scli.io/)** | TUI (Terminal User Interface) for K8s | Visually manage the cluster interactively in the terminal |

### Why kind?

There are several ways to run K8s locally. We chose kind because it's the most suitable for learning:

| Tool | Pros | Cons |
|---|---|---|
| **kind** ✅ | Lightweight, fast, uses Docker you already have, easy multi-node | No native dashboard |
| minikube | Many features, ready addons | Heavy, uses VM by default |
| Docker Desktop K8s | One-click to enable | Single-node, limited |
| k3d | Lightweight, uses k3s | Less documentation |

> 💡 **kind uses Docker under the hood!** Each K8s cluster node is a Docker container. You can see the nodes with `docker ps`. This means **the only prerequisite is having Docker installed** — which you already have from the Docker Lab.

---

## 🍎 macOS Installation

### 1. kind

```bash
# Via Homebrew (recommended)
brew install kind

# Verify
kind version
# → kind v0.25.0 go1.23.x
```

### 2. kubectl

```bash
# Via Homebrew
brew install kubectl

# Verify
kubectl version --client
# → Client Version: v1.31.x
```

### 3. k9s (optional, but highly recommended)

```bash
# Via Homebrew
brew install k9s

# Verify
k9s version
```

---

## 🐧 Linux Installation

### 1. kind

```bash
# Download binary
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Verify
kind version
```

### 2. kubectl

```bash
# Download binary
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/kubectl

# Verify
kubectl version --client
```

### 3. k9s

```bash
# Via install script
curl -sS https://webi.sh/k9s | sh

# Or manual download: https://github.com/derailed/k9s/releases
```

---

## 🪟 Windows Installation

### 1. kind

```powershell
# Via Chocolatey
choco install kind

# Or via Scoop
scoop install kind

# Verify
kind version
```

### 2. kubectl

```powershell
# Via Chocolatey
choco install kubernetes-cli

# Verify
kubectl version --client
```

### 3. k9s

```powershell
# Via Chocolatey
choco install k9s

# Via Scoop
scoop install k9s
```

> ⚠️ **Windows:** Make sure Docker Desktop is running with **WSL 2** enabled. kind depends on the Docker Engine working.

---

## 🎯 Creating Your First Cluster

### Simple cluster (single-node)

The simplest cluster has only one node that does everything (Control Plane + Worker):

```bash
# Create cluster with default name "kind"
kind create cluster

# Verify the cluster was created
kubectl cluster-info
# → Kubernetes control plane is running at https://127.0.0.1:xxxxx

# List nodes
kubectl get nodes
# → NAME                 STATUS   ROLES           AGE   VERSION
# → kind-control-plane   Ready    control-plane   30s   v1.31.0
```

Done! You have a functional Kubernetes cluster. 🎉

```bash
# Delete when done
kind delete cluster
```

### Multi-node cluster (recommended for the Labs)

To simulate a more realistic environment, we use the `kind-config.yaml` from this repository:

```yaml
# kind-config.yaml — 1 Control Plane + 2 Workers
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30000
        hostPort: 30000
        protocol: TCP
      - containerPort: 30001
        hostPort: 30001
        protocol: TCP
  - role: worker
  - role: worker
```

```bash
# Create multi-node cluster
kind create cluster --name k8s-lab --config kind-config.yaml

# Verify: now there are 3 nodes!
kubectl get nodes
# → NAME                    STATUS   ROLES           AGE   VERSION
# → k8s-lab-control-plane   Ready    control-plane   45s   v1.31.0
# → k8s-lab-worker          Ready    <none>          30s   v1.31.0
# → k8s-lab-worker2         Ready    <none>          30s   v1.31.0
```

### What happened under the hood?

kind created **3 Docker containers** — each simulating a cluster node:

```bash
# See kind containers
docker ps
# → CONTAINER ID   IMAGE                  NAMES
# → abc123         kindest/node:v1.31.0   k8s-lab-control-plane
# → def456         kindest/node:v1.31.0   k8s-lab-worker
# → ghi789         kindest/node:v1.31.0   k8s-lab-worker2
```

```
┌───────────────────────────────────────────────────────┐
│                    Your Computer                       │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │              Docker Engine                       │  │
│  │                                                  │  │
│  │  ┌──────────────┐ ┌────────────┐ ┌────────────┐ │  │
│  │  │  Docker      │ │  Docker    │ │  Docker    │ │  │
│  │  │  Container   │ │  Container │ │  Container │ │  │
│  │  │  #1          │ │  #2        │ │  #3        │ │  │
│  │  │              │ │            │ │            │ │  │
│  │  │ ┌──────────┐ │ │ ┌────────┐ │ │ ┌────────┐ │ │  │
│  │  │ │Control   │ │ │ │Worker  │ │ │ │Worker  │ │ │  │
│  │  │ │Plane K8s │ │ │ │Node #1 │ │ │ │Node #2 │ │ │  │
│  │  │ │          │ │ │ │        │ │ │ │        │ │ │  │
│  │  │ │API Server│ │ │ │kubelet │ │ │ │kubelet │ │ │  │
│  │  │ │etcd      │ │ │ │Pods... │ │ │ │Pods... │ │ │  │
│  │  │ │Scheduler │ │ │ │        │ │ │ │        │ │ │  │
│  │  │ └──────────┘ │ │ └────────┘ │ │ └────────┘ │ │  │
│  │  └──────────────┘ └────────────┘ └────────────┘ │  │
│  └─────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

> 💡 **Elegance of kind:** Docker containers simulating K8s nodes that in turn run application containers. It's "container within a container" — but works perfectly for learning!

---

## 🔧 Managing kind Clusters

```bash
# List existing clusters
kind get clusters
# → k8s-lab

# View active cluster info
kubectl cluster-info

# View all nodes with details
kubectl get nodes -o wide

# Switch between clusters (if you have more than one)
kubectl config get-contexts
kubectl config use-context kind-k8s-lab

# Delete a cluster
kind delete cluster --name k8s-lab

# Delete ALL clusters
kind delete clusters --all
```

---

## 🔧 Configuring kubectl: Contexts

kubectl can manage multiple clusters. Each cluster is a **context**:

```bash
# View current context (active cluster)
kubectl config current-context
# → kind-k8s-lab

# List all contexts
kubectl config get-contexts
# → CURRENT   NAME           CLUSTER        AUTHINFO
# → *         kind-k8s-lab   kind-k8s-lab   kind-k8s-lab

# Switch context
kubectl config use-context kind-k8s-lab
```

> ⚠️ **Caution in production:** Always verify the context before running commands! Running `kubectl delete` on the wrong cluster can be catastrophic. The command `kubectl config current-context` is your best friend.

---

## 🖥️ k9s: The Turbo Terminal for K8s

**k9s** is an interactive terminal interface that makes cluster visualization and management much more productive:

```bash
# Start k9s (connects to the active cluster)
k9s
```

### Main k9s Commands

| Key | Action |
|---|---|
| `:pods` | Go to Pods screen |
| `:deploy` | Go to Deployments |
| `:svc` | Go to Services |
| `:nodes` | Go to Nodes |
| `:ns` | Go to Namespaces |
| `d` | Describe (details of selected resource) |
| `l` | Logs of selected Pod |
| `s` | Shell (exec -it) into Pod |
| `Ctrl+D` | Delete selected resource |
| `?` | Help |
| `Ctrl+C` | Exit |

> 💡 **Tip:** k9s is like "htop for Kubernetes". Very useful for monitoring Pods in real time during the Labs.

---

## ✅ Verification Checklist

Run these commands to confirm everything is installed correctly:

```bash
# 1. Docker is running
docker version
# ✅ Should show Client and Server

# 2. kind is installed
kind version
# ✅ Should show version (e.g. v0.25.0)

# 3. kubectl is installed
kubectl version --client
# ✅ Should show client version

# 4. Create a test cluster
kind create cluster --name teste
# ✅ Should create without errors

# 5. kubectl connects to the cluster
kubectl get nodes
# ✅ Should list the "teste-control-plane" node

# 6. (Optional) k9s works
k9s
# ✅ Should open the interface (Ctrl+C to exit)

# 7. Clean up
kind delete cluster --name teste
```

If all steps passed, your environment is ready! 🎉

---

## 📝 Summary

| Tool | Install command (macOS) | Verification |
|---|---|---|
| **kind** | `brew install kind` | `kind version` |
| **kubectl** | `brew install kubectl` | `kubectl version --client` |
| **k9s** | `brew install k9s` | `k9s version` |

| Action | Command |
|---|---|
| Create simple cluster | `kind create cluster` |
| Create multi-node cluster | `kind create cluster --name lab --config kind-config.yaml` |
| List clusters | `kind get clusters` |
| View nodes | `kubectl get nodes` |
| Delete cluster | `kind delete cluster --name lab` |

---

**Next:** [03 — Pods and Containers](03-pods-e-containers.md) →
