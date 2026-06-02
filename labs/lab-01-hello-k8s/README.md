# 🧪 Lab 01 — Hello K8s: Seu Primeiro Cluster

> **Objetivo:** Criar um cluster Kubernetes local com kind, rodar seu primeiro Pod, explorá-lo com kubectl e entender a diferença entre modo imperativo e declarativo.

> **Pré-requisito:** Docker instalado e rodando. Verifique com `docker version`.

> **Tempo estimado:** 30 minutos

---

## 📋 O que você vai praticar

- [x] Instalar kind e kubectl
- [x] Criar e destruir clusters Kubernetes locais
- [x] Rodar Pods de forma imperativa e declarativa
- [x] Usar `kubectl` para inspecionar, logar e acessar Pods
- [x] Entender `port-forward` para acessar serviços no navegador

---

## 🔬 Exercício 1: Instalação das Ferramentas

### Passo 1 — Instalar kind

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

### Passo 2 — Instalar kubectl

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

### Passo 3 — Verificar

```bash
kind version
# → kind v0.25.0 ...

kubectl version --client
# → Client Version: v1.31.x
```

> 💡 Se ambos os comandos retornaram versão, você está pronto!

---

## 🔬 Exercício 2: Seu Primeiro Cluster

### Passo 1 — Criar o cluster

```bash
kind create cluster --name hello-k8s
```

Saída esperada:
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

### Passo 2 — Verificar o cluster

```bash
# Informações do cluster
kubectl cluster-info
# → Kubernetes control plane is running at https://127.0.0.1:xxxxx

# Listar nós
kubectl get nodes
# → NAME                     STATUS   ROLES           AGE   VERSION
# → hello-k8s-control-plane  Ready    control-plane   30s   v1.31.0
```

### Passo 3 — Espiar por baixo dos panos

```bash
# O kind criou um contêiner Docker! Veja:
docker ps --filter "name=hello-k8s"
# → CONTAINER ID   IMAGE                  NAMES
# → abc123def456   kindest/node:v1.31.0   hello-k8s-control-plane
```

> 💡 **Reflexão:** Seu cluster Kubernetes inteiro está rodando dentro de um contêiner Docker. É "Kubernetes dentro do Docker" — simples e leve!

### Passo 4 — Explorar os componentes do cluster

```bash
# Ver todos os Pods do sistema (Control Plane)
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

> 🧠 **Observe:** O API Server, etcd, Scheduler e Controller Manager que aprendemos na documentação estão todos ali, rodando como Pods no namespace `kube-system`!

---

## 🔬 Exercício 3: Primeiro Pod (Modo Imperativo)

### Passo 1 — Criar um Pod Nginx

```bash
kubectl run meu-nginx --image=nginx:1.27 --port=80
# → pod/meu-nginx created
```

### Passo 2 — Verificar

```bash
kubectl get pods
# → NAME        READY   STATUS    RESTARTS   AGE
# → meu-nginx   1/1     Running   0          10s
```

### Passo 3 — Acessar no navegador via port-forward

```bash
# Criar túnel: porta 8080 do seu computador → porta 80 do Pod
kubectl port-forward pod/meu-nginx 8080:80
# → Forwarding from 127.0.0.1:8080 -> 80
```

Abra outro terminal e teste:
```bash
curl http://localhost:8080
# → <!DOCTYPE html>... Welcome to nginx! ...
```

Ou abra no navegador: **http://localhost:8080** — Welcome to nginx! 🎉

Pressione `Ctrl+C` no terminal do port-forward para encerrar.

### Passo 4 — Explorar o Pod

```bash
# Detalhes completos do Pod (eventos, IPs, nó, status)
kubectl describe pod meu-nginx

# Logs do Nginx
kubectl logs meu-nginx

# Entrar no Pod (shell interativo)
kubectl exec -it meu-nginx -- bash

# Dentro do Pod:
hostname
# → meu-nginx

cat /etc/os-release
# → Debian GNU/Linux 12 (bookworm)

curl localhost:80
# → Welcome to nginx!

exit
```

### Passo 5 — Testar o auto-healing (ou falta dele!)

```bash
# Deletar o Pod
kubectl delete pod meu-nginx

# Verificar
kubectl get pods
# → Nenhum Pod! 😱
```

> ⚠️ **Lição:** Pods criados diretamente (`kubectl run`) **não são recriados** quando morrem. Para auto-healing, precisamos de Deployments — tema do Lab 02!

---

## 🔬 Exercício 4: Primeiro Pod (Modo Declarativo — YAML)

Agora vamos criar o mesmo Pod, mas usando um arquivo YAML:

### Passo 1 — Criar o arquivo YAML

Crie o arquivo `pod-nginx.yaml`:

```yaml
# pod-nginx.yaml — Meu primeiro Pod declarativo
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

### Passo 2 — Aplicar o YAML

```bash
kubectl apply -f pod-nginx.yaml
# → pod/nginx-declarativo created
```

### Passo 3 — Verificar

```bash
kubectl get pods
# → NAME                READY   STATUS    RESTARTS   AGE
# → nginx-declarativo   1/1     Running   0          5s

# Ver com labels
kubectl get pods --show-labels
# → NAME                LABELS
# → nginx-declarativo   app=nginx,lab=01
```

### Passo 4 — Filtrar por labels

```bash
# Listar Pods com label app=nginx
kubectl get pods -l app=nginx
# → nginx-declarativo

# Listar Pods do Lab 01
kubectl get pods -l lab=01
# → nginx-declarativo
```

### Passo 5 — Acessar

```bash
kubectl port-forward pod/nginx-declarativo 8080:80
# Abra: http://localhost:8080
# Ctrl+C para parar
```

### Passo 6 — Deletar via YAML

```bash
kubectl delete -f pod-nginx.yaml
# → pod "nginx-declarativo" deleted
```

> 💡 **Vantagem do declarativo:** O YAML pode ir para o Git, ser versionado, revisado por colegas e aplicado em qualquer cluster. É reproduzível!

---

## 🔬 Exercício 5: Cluster Multi-Node

Vamos criar um cluster com 3 nós para simular um ambiente mais realista:

### Passo 1 — Deletar o cluster anterior

```bash
kind delete cluster --name hello-k8s
```

### Passo 2 — Criar cluster multi-node

Use o arquivo `kind-config.yaml` da raiz deste repositório:

```bash
# A partir da raiz do cdn-k8s-lab
kind create cluster --name k8s-lab --config kind-config.yaml
```

### Passo 3 — Verificar os 3 nós

```bash
kubectl get nodes
# → NAME                    STATUS   ROLES           AGE   VERSION
# → k8s-lab-control-plane   Ready    control-plane   30s   v1.31.0
# → k8s-lab-worker          Ready    <none>          20s   v1.31.0
# → k8s-lab-worker2         Ready    <none>          20s   v1.31.0
```

### Passo 4 — Ver os contêineres Docker

```bash
docker ps --filter "name=k8s-lab"
# → 3 contêineres! Um para cada nó do cluster.
```

### Passo 5 — Criar Pods e ver distribuição

```bash
# Criar 3 Pods
kubectl run pod-1 --image=nginx:1.27
kubectl run pod-2 --image=nginx:1.27
kubectl run pod-3 --image=nginx:1.27

# Ver em qual nó cada Pod foi alocado
kubectl get pods -o wide
# → NAME    READY   STATUS    IP           NODE
# → pod-1   1/1     Running   10.244.1.2   k8s-lab-worker
# → pod-2   1/1     Running   10.244.2.3   k8s-lab-worker2
# → pod-3   1/1     Running   10.244.1.4   k8s-lab-worker
```

> 🧠 **Observe:** O Scheduler do K8s distribuiu os Pods entre os Workers automaticamente! Ele tenta balancear a carga entre os nós.

---

## 🧹 Limpeza Final

```bash
# Deletar os Pods de teste
kubectl delete pod pod-1 pod-2 pod-3

# Manter o cluster k8s-lab para os próximos Labs!
# Ou, se quiser deletar tudo:
# kind delete cluster --name k8s-lab
```

> 💡 **Dica:** Mantenha o cluster `k8s-lab` rodando — você vai usá-lo nos próximos Labs. Se precisar recriar, basta rodar `kind create cluster --name k8s-lab --config kind-config.yaml` novamente.

---

## ✅ O que aprendemos

| Conceito | Comando |
|---|---|
| Criar cluster kind | `kind create cluster --name lab` |
| Criar cluster multi-node | `kind create cluster --config kind-config.yaml` |
| Ver nós do cluster | `kubectl get nodes` |
| Criar Pod (imperativo) | `kubectl run nginx --image=nginx:1.27` |
| Criar Pod (declarativo) | `kubectl apply -f pod.yaml` |
| Acessar Pod no navegador | `kubectl port-forward pod/nome 8080:80` |
| Ver logs | `kubectl logs nome` |
| Entrar no Pod | `kubectl exec -it nome -- bash` |
| Detalhes do Pod | `kubectl describe pod nome` |
| Filtrar por labels | `kubectl get pods -l app=nginx` |
| Deletar Pod | `kubectl delete pod nome` |
| Deletar via YAML | `kubectl delete -f pod.yaml` |
| Deletar cluster | `kind delete cluster --name lab` |

---

**Próximo:** [Lab 02 — Deployments na Prática](../lab-02-deployments/README.md) →
