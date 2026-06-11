# 📖 07 — kubectl Cheatsheet

> **Quick reference** of all essential `kubectl` commands, organized by category. Keep this page open while working on the Labs!

---

## 🔧 Cluster and Context

```bash
# Cluster info
kubectl cluster-info

# List configured contexts (clusters)
kubectl config get-contexts

# View active context
kubectl config current-context

# Switch context
kubectl config use-context kind-k8s-lab

# View all cluster nodes
kubectl get nodes
kubectl get nodes -o wide          # With IPs and kernel version
```

---

## 🫛 Pods

```bash
# ── List ──
kubectl get pods                            # Current namespace
kubectl get pods -A                         # All namespaces
kubectl get pods -o wide                    # With IPs and nodes
kubectl get pods -l app=nginx               # Filter by label
kubectl get pods --watch                    # Real-time monitoring
kubectl get pods --sort-by='.status.startTime'  # Sort by date

# ── Create (imperative — for quick tests) ──
kubectl run nginx --image=nginx:1.27 --port=80
kubectl run pg --image=postgres:16 --env="POSTGRES_PASSWORD=password"

# ── Details ──
kubectl describe pod <name>                 # Events, status, volumes
kubectl get pod <name> -o yaml              # Full resource YAML

# ── Logs ──
kubectl logs <name>                         # Container logs
kubectl logs <name> -f                      # Follow logs (tail -f)
kubectl logs <name> --previous              # Previous container logs (crash)
kubectl logs <name> -c <container>          # Specific container logs (multi-container)
kubectl logs -l app=nginx --all-containers  # Logs from all Pods with label

# ── Execute commands ──
kubectl exec -it <name> -- bash             # Interactive shell
kubectl exec -it <name> -- sh               # If bash doesn't exist (Alpine)
kubectl exec <name> -- cat /etc/hostname    # Single command

# ── Port-forward ──
kubectl port-forward pod/<name> 8080:80     # Access Pod locally
kubectl port-forward svc/<name> 8080:80     # Access via Service

# ── Delete ──
kubectl delete pod <name>                   # Delete specific Pod
kubectl delete pods --all                   # ⚠️ Delete all Pods in namespace
kubectl delete pod <name> --force --grace-period=0  # Force immediate removal
```

---

## 🚀 Deployments

```bash
# ── Create / Update ──
kubectl apply -f deployment.yaml
kubectl create deployment nginx --image=nginx:1.27 --replicas=3  # Imperative

# ── List ──
kubectl get deployments
kubectl get deploy                          # Shortcut

# ── Scale ──
kubectl scale deployment <name> --replicas=5
kubectl autoscale deployment <name> --min=2 --max=10 --cpu-percent=50

# ── Update image ──
kubectl set image deployment/<name> container=image:new-tag
kubectl rollout restart deployment <name>   # Restart all Pods

# ── Rollout ──
kubectl rollout status deployment <name>    # Update status
kubectl rollout history deployment <name>   # Revision history
kubectl rollout undo deployment <name>      # Rollback (previous version)
kubectl rollout undo deployment <name> --to-revision=2  # Specific rollback

# ── Delete ──
kubectl delete deployment <name>
```

---

## 🌐 Services

```bash
# ── Create ──
kubectl apply -f service.yaml
kubectl expose deployment <name> --port=80 --target-port=8000 --type=NodePort

# ── List ──
kubectl get services
kubectl get svc                             # Shortcut

# ── Details ──
kubectl describe svc <name>

# ── Delete ──
kubectl delete svc <name>
```

---

## 📋 ConfigMaps and Secrets

```bash
# ── ConfigMaps ──
kubectl create configmap <name> --from-literal=KEY=value
kubectl create configmap <name> --from-file=config.yaml
kubectl get configmaps
kubectl describe configmap <name>
kubectl get configmap <name> -o yaml        # View contents

# ── Secrets ──
kubectl create secret generic <name> --from-literal=PASSWORD=senha123
kubectl get secrets
kubectl describe secret <name>
kubectl get secret <name> -o yaml           # View contents (Base64)

# Decode Secret
kubectl get secret <name> -o jsonpath='{.data.PASSWORD}' | base64 -d
```

---

## 💾 Volumes (PV / PVC)

```bash
kubectl get pv                              # PersistentVolumes
kubectl get pvc                             # PersistentVolumeClaims
kubectl describe pvc <name>                 # Details and binding status
kubectl get storageclass                    # Available StorageClasses
```

---

## 📁 Namespaces

```bash
# ── List ──
kubectl get namespaces
kubectl get ns                              # Shortcut

# ── Create ──
kubectl create namespace my-ns

# ── Use ──
kubectl get pods -n my-ns                   # List Pods in a namespace
kubectl apply -f file.yaml -n my-ns         # Apply in specific namespace

# ── Change default namespace ──
kubectl config set-context --current --namespace=my-ns
```

---

## 📄 Apply and Delete Resources

```bash
# ── Apply YAML ──
kubectl apply -f file.yaml               # Create or update
kubectl apply -f manifests/              # Apply all YAMLs from a directory
kubectl apply -f https://url/resource.yaml   # Apply from a URL

# ── Delete ──
kubectl delete -f file.yaml              # Delete resource defined in YAML
kubectl delete -f manifests/             # Delete everything from directory
kubectl delete all --all -n <namespace>  # ⚠️ Delete EVERYTHING in a namespace

# ── Dry-run (test without applying) ──
kubectl apply -f file.yaml --dry-run=client   # Validate locally
kubectl apply -f file.yaml --dry-run=server   # Validate on server
```

---

## 🔍 Debug and Troubleshooting

```bash
# ── Cluster events ──
kubectl get events --sort-by='.lastTimestamp'
kubectl get events -A                       # All namespaces

# ── Investigate problematic Pod ──
kubectl describe pod <name>                 # "Events" section is key
kubectl logs <name>                         # View stdout/stderr
kubectl logs <name> --previous              # Previous crash logs

# ── Quick status ──
kubectl get all                             # Everything in current namespace
kubectl get all -A                          # Everything in all namespaces

# ── Node resources ──
kubectl top nodes                           # Node CPU and memory
kubectl top pods                            # Pod CPU and memory
# (requires Metrics Server installed)

# ── Test connectivity from inside the cluster ──
kubectl run debug --image=busybox -it --rm -- wget -qO- http://api-vendas:80
kubectl run debug --image=busybox -it --rm -- nslookup api-vendas
```

---

## ⌨️ Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc` for productivity:

```bash
# kubectl shortcuts
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployments'
alias kga='kubectl get all'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias kdp='kubectl describe pod'
alias kl='kubectl logs'
alias klf='kubectl logs -f'
alias kei='kubectl exec -it'
alias kns='kubectl config set-context --current --namespace'

# Usage example:
# kgp           → kubectl get pods
# kaf app.yaml  → kubectl apply -f app.yaml
# klf my-pod    → kubectl logs -f my-pod
# kns prod      → switch to namespace "prod"
```

---

## 📝 Generate YAMLs Automatically

```bash
# Generate Pod YAML without creating
kubectl run nginx --image=nginx:1.27 --port=80 \
  --dry-run=client -o yaml > pod.yaml

# Generate Deployment YAML without creating
kubectl create deployment nginx --image=nginx:1.27 --replicas=3 \
  --dry-run=client -o yaml > deployment.yaml

# Generate Service YAML without creating
kubectl expose deployment nginx --port=80 --type=NodePort \
  --dry-run=client -o yaml > service.yaml
```

> 💡 **Tip:** `--dry-run=client -o yaml` is your best friend for quickly creating YAML templates without memorizing the full structure.

---

**← Back to** [README.md](../README.md)
