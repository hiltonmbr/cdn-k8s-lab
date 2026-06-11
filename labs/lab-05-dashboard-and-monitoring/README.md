# 🧪 Lab 05 — Dashboard and Visual Monitoring

> **Objective:** Install and explore visual tools to monitor the Kubernetes cluster — the official web Dashboard and k9s (terminal TUI). Visualize Pods, Deployments, resource consumption, and cluster events in real time.

> **Prerequisite:** `k8s-lab` cluster running (Lab 01). k9s installed (optional, but recommended).

> **Estimated time:** 25 minutes

---

## 📋 What you will practice

- [x] Install the official Kubernetes Dashboard
- [x] Create a secure access token
- [x] Navigate the Dashboard in the browser
- [x] Explore k9s (interactive terminal interface)
- [x] Monitor Pods, Deployments, and events in real time
- [x] Compare visualization tools

---

## 🔬 Exercise 1: Kubernetes Dashboard

The **Kubernetes Dashboard** is an official web interface to manage and monitor the cluster.

### Step 1 — Install the Dashboard

```bash
# Install Dashboard v2 (official manifests)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
```

Expected output:
```
namespace/kubernetes-dashboard created
serviceaccount/kubernetes-dashboard created
service/kubernetes-dashboard created
deployment.apps/kubernetes-dashboard created
...
```

### Step 2 — Verify the installation

```bash
# Check Dashboard Pods
kubectl get pods -n kubernetes-dashboard
# → NAME                                         READY   STATUS
# → dashboard-metrics-scraper-xxx                1/1     Running
# → kubernetes-dashboard-xxx                     1/1     Running
```

### Step 3 — Create admin user for the Dashboard

```bash
kubectl apply -f labs/lab-05-dashboard-and-monitoring/manifests/dashboard.yaml
# → serviceaccount/admin-user created
# → clusterrolebinding.rbac.authorization.k8s.io/admin-user created
```

### Step 4 — Generate access token

```bash
# Generate temporary token (valid for 1 hour)
kubectl -n kubernetes-dashboard create token admin-user
# → eyJhbGciOiJSUzI1NiIs...  ← COPY this token!
```

> ⚠️ **Copy the entire token!** You will need it to log into the Dashboard.

### Step 5 — Access the Dashboard

```bash
# Create proxy for local access
kubectl proxy
# → Starting to serve on 127.0.0.1:8001
```

Open in the browser:

**http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/**

1. Select **Token**
2. Paste the token generated in Step 4
3. Click **Sign in**

### Step 6 — Explore the Dashboard

In the Dashboard, explore:

| Section | What it shows |
|---|---|
| **Cluster → Nodes** | Cluster nodes (control-plane, workers) |
| **Workloads → Pods** | All running Pods |
| **Workloads → Deployments** | Deployments and their status |
| **Discovery → Services** | Active Services |
| **Config → ConfigMaps** | Registered ConfigMaps |
| **Config → Secrets** | Secrets (protected content) |
| **Cluster → Events** | Recent cluster events |

#### Guided exercise in the Dashboard:

1. **Switch namespace:** At the top, select "All namespaces" to see everything
2. **Create a Pod:** Click "+" → Paste a simple Pod YAML → Create
3. **View logs:** Click a Pod → "Logs" icon 📄
4. **View events:** Go to Cluster → Events to see the activity timeline

> 💡 **Tip:** The Dashboard is great for **visualizing** the cluster, but prefer `kubectl` and YAMLs for **managing** resources (more reproducible and versionable).

---

## 🔬 Exercise 2: k9s — The Turbocharged Terminal

**k9s** is a terminal interface (TUI) that makes cluster interaction much more productive than plain `kubectl`.

### Step 1 — Start k9s

```bash
k9s
```

You will see an interactive terminal interface with all Pods listed!

### Step 2 — Navigate between resources

| Command | What it does |
|---|---|
| `:pods` + Enter | Go to Pods screen |
| `:deploy` + Enter | Go to Deployments |
| `:svc` + Enter | Go to Services |
| `:ns` + Enter | Go to Namespaces |
| `:nodes` + Enter | Go to Nodes |
| `:events` + Enter | View cluster events |
| `:secrets` + Enter | View Secrets |

### Step 3 — Interact with resources

Select a resource with the arrow keys and use:

| Key | Action |
|---|---|
| **Enter** | Enter/Select |
| **d** | Describe (full details) |
| **l** | Pod logs |
| **s** | Shell (exec -it) into the Pod |
| **Ctrl+K** | Delete selected resource |
| **/** | Search/Filter |
| **Esc** | Go back |
| **?** | Help |
| **Ctrl+C** | Exit k9s |

### Step 4 — Practical exercise in k9s

1. Type `:deploy` → View Deployments
2. Select a Deployment → Press **Enter** → View Pods
3. Select a Pod → Press **l** → View logs in real time
4. Press **Esc** → Go back
5. Select a Pod → Press **d** → View the full describe
6. Press **Esc** → Go back
7. Select a Pod → Press **s** → Open a shell in the Pod
8. Type `exit` to leave the shell

### Step 5 — Filter by namespace

```
# Inside k9s, press ":" and type:
:pods all       # View Pods from all namespaces
:pods spark     # View Pods from the spark namespace only
```

> 💡 **k9s vs Dashboard:** k9s is faster for frequent interactions (logs, shell, delete). The Dashboard is better for a panoramic view of the cluster. Use both!

---

## 🔬 Exercise 3: Monitoring with kubectl

Even without visual tools, kubectl offers excellent monitoring capabilities:

### Monitor Pods in real time

```bash
# Watch mode: auto-refreshes
kubectl get pods -A --watch

# In another terminal, create a Deployment:
kubectl create deployment teste --image=nginx:1.27 --replicas=3

# Watch Pods being created in real time in the first terminal!
# Ctrl+C to stop
```

### View cluster events

```bash
# Recent events (sorted by timestamp)
kubectl get events --sort-by='.lastTimestamp' -A

# Events from the last 5 minutes
kubectl get events --field-selector reason=Created -A
```

### Check overall health

```bash
# Everything everywhere
kubectl get all -A

# Node status
kubectl get nodes -o wide

# Cluster components
kubectl get componentstatuses 2>/dev/null || kubectl get --raw='/healthz'
```

### Clean up the test Deployment

```bash
kubectl delete deployment teste
```

---

## 🆚 Tool Comparison

| Feature | kubectl | k9s | Dashboard |
|---|---|---|---|
| **Interface** | Command line | TUI (terminal) | Web (browser) |
| **Learning curve** | Medium | Low | Low |
| **Speed** | Fast | Very fast | Slower |
| **Panoramic view** | Limited | Good | Excellent |
| **Interactivity** | Low | High | High |
| **Reproducible** | ✅ Yes (scripts) | ❌ No | ❌ No |
| **Production** | ✅ Standard | ✅ Popular | ⚠️ Caution (security) |
| **Ideal for** | Automation, CI/CD | Monitoring, debug | Presentations, exploration |

---

## 🧹 Cleanup

```bash
# Stop kubectl proxy (Ctrl+C)

# Remove the Dashboard (if desired)
kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl delete -f labs/lab-05-dashboard-and-monitoring/manifests/dashboard.yaml

# Verify
kubectl get all -n kubernetes-dashboard
# → "No resources found" ✅
```

---

## ✅ What we learned

| Tool | What we did |
|---|---|
| **Kubernetes Dashboard** | Installation, access token, navigating the web interface |
| **k9s** | Interactive terminal interface for Pods, Deployments, logs |
| **kubectl --watch** | Real-time monitoring via command line |
| **Cluster events** | Investigate what is happening in the cluster |
| **Comparison** | kubectl (automation) vs k9s (productivity) vs Dashboard (visual) |

---

**← Back to** [README.md](../../README.md)
