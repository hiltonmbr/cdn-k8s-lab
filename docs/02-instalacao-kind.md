# 📖 02 — Instalação: kind, kubectl e Ferramentas

> **Objetivo:** Instalar e configurar todas as ferramentas necessárias para rodar um cluster Kubernetes local no seu computador. Ao final, você terá um cluster K8s funcional com 3 nós.

---

## 🧰 O que vamos instalar

| Ferramenta | O que é | Por que precisamos |
|---|---|---|
| **[kind](https://kind.sigs.k8s.io/)** | Kubernetes IN Docker — cria clusters K8s usando contêineres Docker como nós | É a forma mais leve de rodar K8s localmente. Sem VMs! |
| **[kubectl](https://kubernetes.io/docs/tasks/tools/)** | CLI oficial do Kubernetes | Para interagir com o cluster (criar, listar, deletar recursos) |
| **[k9s](https://k9scli.io/)** | Interface TUI (Terminal User Interface) para K8s | Visualizar e gerenciar o cluster de forma interativa no terminal |

### Por que kind?

Existem várias formas de rodar K8s localmente. Escolhemos o kind por ser a mais adequada para aprendizado:

| Ferramenta | Prós | Contras |
|---|---|---|
| **kind** ✅ | Leve, rápido, usa Docker que você já tem, multi-node fácil | Sem dashboard nativo |
| minikube | Muitas features, addons prontos | Pesado, usa VM por padrão |
| Docker Desktop K8s | Um clique para ativar | Single-node, limitado |
| k3d | Leve, usa k3s | Menos documentação |

> 💡 **kind usa Docker por baixo!** Cada nó do cluster K8s é um contêiner Docker. Você pode ver os nós com `docker ps`. Isso significa que **o único pré-requisito é ter Docker instalado** — que você já tem do Docker Lab.

---

## 🍎 Instalação no macOS

### 1. kind

```bash
# Via Homebrew (recomendado)
brew install kind

# Verificar
kind version
# → kind v0.25.0 go1.23.x
```

### 2. kubectl

```bash
# Via Homebrew
brew install kubectl

# Verificar
kubectl version --client
# → Client Version: v1.31.x
```

### 3. k9s (opcional, mas muito recomendado)

```bash
# Via Homebrew
brew install k9s

# Verificar
k9s version
```

---

## 🐧 Instalação no Linux

### 1. kind

```bash
# Download do binário
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Verificar
kind version
```

### 2. kubectl

```bash
# Download do binário
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/kubectl

# Verificar
kubectl version --client
```

### 3. k9s

```bash
# Via script de instalação
curl -sS https://webi.sh/k9s | sh

# Ou download manual: https://github.com/derailed/k9s/releases
```

---

## 🪟 Instalação no Windows

### 1. kind

```powershell
# Via Chocolatey
choco install kind

# Ou via Scoop
scoop install kind

# Verificar
kind version
```

### 2. kubectl

```powershell
# Via Chocolatey
choco install kubernetes-cli

# Verificar
kubectl version --client
```

### 3. k9s

```powershell
# Via Chocolatey
choco install k9s

# Via Scoop
scoop install k9s
```

> ⚠️ **Windows:** Certifique-se de que o Docker Desktop está rodando com **WSL 2** habilitado. O kind depende do Docker Engine funcionando.

---

## 🎯 Criando Seu Primeiro Cluster

### Cluster simples (single-node)

O cluster mais simples tem apenas um nó que faz tudo (Control Plane + Worker):

```bash
# Criar cluster com nome padrão "kind"
kind create cluster

# Verificar que o cluster foi criado
kubectl cluster-info
# → Kubernetes control plane is running at https://127.0.0.1:xxxxx

# Listar nós
kubectl get nodes
# → NAME                 STATUS   ROLES           AGE   VERSION
# → kind-control-plane   Ready    control-plane   30s   v1.31.0
```

Pronto! Você tem um cluster Kubernetes funcional. 🎉

```bash
# Deletar quando terminar
kind delete cluster
```

### Cluster multi-node (recomendado para os Labs)

Para simular um ambiente mais realista, usamos a configuração `kind-config.yaml` deste repositório:

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
# Criar cluster multi-node
kind create cluster --name k8s-lab --config kind-config.yaml

# Verificar: agora há 3 nós!
kubectl get nodes
# → NAME                    STATUS   ROLES           AGE   VERSION
# → k8s-lab-control-plane   Ready    control-plane   45s   v1.31.0
# → k8s-lab-worker          Ready    <none>          30s   v1.31.0
# → k8s-lab-worker2         Ready    <none>          30s   v1.31.0
```

### O que aconteceu por baixo?

O kind criou **3 contêineres Docker** — cada um simulando um nó do cluster:

```bash
# Veja os contêineres do kind
docker ps
# → CONTAINER ID   IMAGE                  NAMES
# → abc123         kindest/node:v1.31.0   k8s-lab-control-plane
# → def456         kindest/node:v1.31.0   k8s-lab-worker
# → ghi789         kindest/node:v1.31.0   k8s-lab-worker2
```

```
┌───────────────────────────────────────────────────────┐
│                   Seu Computador                       │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │              Docker Engine                       │  │
│  │                                                  │  │
│  │  ┌──────────────┐ ┌────────────┐ ┌────────────┐ │  │
│  │  │  Contêiner   │ │ Contêiner  │ │ Contêiner  │ │  │
│  │  │  Docker #1   │ │ Docker #2  │ │ Docker #3  │ │  │
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

> 💡 **Elegância do kind:** Contêineres Docker simulando nós K8s que por sua vez executam contêineres de aplicação. É "contêiner dentro de contêiner" — mas funciona perfeitamente para aprendizado!

---

## 🔧 Gerenciando Clusters kind

```bash
# Listar clusters existentes
kind get clusters
# → k8s-lab

# Ver informações do cluster ativo
kubectl cluster-info

# Ver todos os nós com detalhes
kubectl get nodes -o wide

# Trocar entre clusters (se tiver mais de um)
kubectl config get-contexts
kubectl config use-context kind-k8s-lab

# Deletar um cluster
kind delete cluster --name k8s-lab

# Deletar TODOS os clusters
kind delete clusters --all
```

---

## 🔧 Configurando kubectl: Contextos

O kubectl pode gerenciar múltiplos clusters. Cada cluster é um **contexto**:

```bash
# Ver o contexto atual (cluster ativo)
kubectl config current-context
# → kind-k8s-lab

# Listar todos os contextos
kubectl config get-contexts
# → CURRENT   NAME           CLUSTER        AUTHINFO
# → *         kind-k8s-lab   kind-k8s-lab   kind-k8s-lab

# Trocar de contexto
kubectl config use-context kind-k8s-lab
```

> ⚠️ **Cuidado em produção:** Sempre verifique o contexto antes de executar comandos! Rodar `kubectl delete` no cluster errado pode ser catastrófico. O comando `kubectl config current-context` é seu melhor amigo.

---

## 🖥️ k9s: O Terminal Turbinado para K8s

O **k9s** é uma interface de terminal interativa que torna a visualização e gerenciamento do cluster muito mais produtivo:

```bash
# Iniciar o k9s (conecta ao cluster ativo)
k9s
```

### Comandos principais do k9s

| Tecla | Ação |
|---|---|
| `:pods` | Ir para a tela de Pods |
| `:deploy` | Ir para Deployments |
| `:svc` | Ir para Services |
| `:nodes` | Ir para Nodes |
| `:ns` | Ir para Namespaces |
| `d` | Describe (detalhes do recurso selecionado) |
| `l` | Logs do Pod selecionado |
| `s` | Shell (exec -it) no Pod |
| `Ctrl+D` | Deletar recurso selecionado |
| `?` | Ajuda |
| `Ctrl+C` | Sair |

> 💡 **Dica:** O k9s é como um "htop para Kubernetes". Muito útil para monitorar Pods em tempo real durante os Labs.

---

## ✅ Checklist de Verificação

Execute estes comandos para confirmar que tudo está instalado corretamente:

```bash
# 1. Docker está rodando
docker version
# ✅ Deve mostrar Client e Server

# 2. kind está instalado
kind version
# ✅ Deve mostrar versão (ex: v0.25.0)

# 3. kubectl está instalado
kubectl version --client
# ✅ Deve mostrar versão do cliente

# 4. Criar cluster de teste
kind create cluster --name teste
# ✅ Deve criar sem erros

# 5. kubectl se conecta ao cluster
kubectl get nodes
# ✅ Deve listar o nó "teste-control-plane"

# 6. (Opcional) k9s funciona
k9s
# ✅ Deve abrir a interface (Ctrl+C para sair)

# 7. Limpar
kind delete cluster --name teste
```

Se todos os passos passaram, seu ambiente está pronto! 🎉

---

## 📝 Resumo

| Ferramenta | Comando de instalação (macOS) | Verificação |
|---|---|---|
| **kind** | `brew install kind` | `kind version` |
| **kubectl** | `brew install kubectl` | `kubectl version --client` |
| **k9s** | `brew install k9s` | `k9s version` |

| Ação | Comando |
|---|---|
| Criar cluster simples | `kind create cluster` |
| Criar cluster multi-node | `kind create cluster --name lab --config kind-config.yaml` |
| Listar clusters | `kind get clusters` |
| Ver nós | `kubectl get nodes` |
| Deletar cluster | `kind delete cluster --name lab` |

---

**Próximo:** [03 — Pods e Containers](03-pods-e-containers.md) →
