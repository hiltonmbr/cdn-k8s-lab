# 🧪 Lab 05 — Dashboard e Monitoramento Visual

> **Objetivo:** Instalar e explorar ferramentas visuais para monitorar o cluster Kubernetes — o Dashboard web oficial e o k9s (TUI terminal). Visualizar Pods, Deployments, consumo de recursos e eventos do cluster em tempo real.

> **Pré-requisito:** Cluster `k8s-lab` rodando (Lab 01). k9s instalado (opcional, mas recomendado).

> **Tempo estimado:** 25 minutos

---

## 📋 O que você vai praticar

- [x] Instalar o Kubernetes Dashboard oficial
- [x] Criar token de acesso seguro
- [x] Navegar pelo Dashboard no navegador
- [x] Explorar o k9s (interface de terminal interativa)
- [x] Monitorar Pods, Deployments e eventos em tempo real
- [x] Comparar ferramentas de visualização

---

## 🔬 Exercício 1: Kubernetes Dashboard

O **Kubernetes Dashboard** é uma interface web oficial para gerenciar e monitorar o cluster.

### Passo 1 — Instalar o Dashboard

```bash
# Instalar o Dashboard v2 (manifests oficiais)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
```

Saída esperada:
```
namespace/kubernetes-dashboard created
serviceaccount/kubernetes-dashboard created
service/kubernetes-dashboard created
deployment.apps/kubernetes-dashboard created
...
```

### Passo 2 — Verificar a instalação

```bash
# Ver os Pods do Dashboard
kubectl get pods -n kubernetes-dashboard
# → NAME                                         READY   STATUS
# → dashboard-metrics-scraper-xxx                1/1     Running
# → kubernetes-dashboard-xxx                     1/1     Running
```

### Passo 3 — Criar usuário admin para o Dashboard

```bash
kubectl apply -f labs/lab-05-dashboard-e-monitoring/manifests/dashboard.yaml
# → serviceaccount/admin-user created
# → clusterrolebinding.rbac.authorization.k8s.io/admin-user created
```

### Passo 4 — Gerar token de acesso

```bash
# Gerar token temporário (válido por 1 hora)
kubectl -n kubernetes-dashboard create token admin-user
# → eyJhbGciOiJSUzI1NiIs...  ← COPIE este token!
```

> ⚠️ **Copie o token inteiro!** Você vai precisar dele para fazer login no Dashboard.

### Passo 5 — Acessar o Dashboard

```bash
# Criar proxy para acesso local
kubectl proxy
# → Starting to serve on 127.0.0.1:8001
```

Abra no navegador:

**http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/**

1. Selecione **Token**
2. Cole o token gerado no Passo 4
3. Clique **Sign in**

### Passo 6 — Explorar o Dashboard

No Dashboard, explore:

| Seção | O que mostra |
|---|---|
| **Cluster → Nodes** | Nós do cluster (control-plane, workers) |
| **Workloads → Pods** | Todos os Pods em execução |
| **Workloads → Deployments** | Deployments e seus status |
| **Discovery → Services** | Services ativos |
| **Config → ConfigMaps** | ConfigMaps registrados |
| **Config → Secrets** | Secrets (conteúdo protegido) |
| **Cluster → Events** | Eventos recentes do cluster |

#### Exercício guiado no Dashboard:

1. **Trocar namespace:** No topo, selecione "All namespaces" para ver tudo
2. **Criar um Pod:** Clique em "+" → Cole um YAML simples de Pod → Create
3. **Ver logs:** Clique em um Pod → ícone de "Logs" 📄
4. **Ver eventos:** Vá em Cluster → Events para ver a timeline de atividades

> 💡 **Dica:** O Dashboard é ótimo para **visualizar** o cluster, mas prefira `kubectl` e YAMLs para **gerenciar** recursos (mais reproduzível e versionável).

---

## 🔬 Exercício 2: k9s — O Terminal Turbinado

O **k9s** é uma interface de terminal (TUI) que torna a interação com o cluster muito mais produtiva do que `kubectl` puro.

### Passo 1 — Iniciar o k9s

```bash
k9s
```

Você verá uma interface interativa no terminal com todos os Pods listados!

### Passo 2 — Navegar entre recursos

| Comando | O que faz |
|---|---|
| `:pods` + Enter | Ir para a tela de Pods |
| `:deploy` + Enter | Ir para Deployments |
| `:svc` + Enter | Ir para Services |
| `:ns` + Enter | Ir para Namespaces |
| `:nodes` + Enter | Ir para Nodes |
| `:events` + Enter | Ver eventos do cluster |
| `:secrets` + Enter | Ver Secrets |

### Passo 3 — Interagir com recursos

Selecione um recurso com as setas e use:

| Tecla | Ação |
|---|---|
| **Enter** | Entrar/Selecionar |
| **d** | Describe (detalhes completos) |
| **l** | Logs do Pod |
| **s** | Shell (exec -it) no Pod |
| **Ctrl+K** | Deletar recurso selecionado |
| **/** | Buscar/Filtrar |
| **Esc** | Voltar |
| **?** | Ajuda |
| **Ctrl+C** | Sair do k9s |

### Passo 4 — Exercício prático no k9s

1. Digite `:deploy` → Veja os Deployments
2. Selecione um Deployment → Pressione **Enter** → Veja os Pods
3. Selecione um Pod → Pressione **l** → Veja os logs em tempo real
4. Pressione **Esc** → Volte
5. Selecione um Pod → Pressione **d** → Veja o describe completo
6. Pressione **Esc** → Volte
7. Selecione um Pod → Pressione **s** → Abra um shell no Pod
8. Digite `exit` para sair do shell

### Passo 5 — Filtrar por namespace

```
# Dentro do k9s, pressione ":" e digite:
:pods all       # Ver Pods de todos os namespaces
:pods spark     # Ver Pods apenas do namespace spark
```

> 💡 **k9s vs Dashboard:** O k9s é mais rápido para interações frequentes (logs, shell, delete). O Dashboard é melhor para ter uma visão panorâmica do cluster. Use ambos!

---

## 🔬 Exercício 3: Monitoramento com kubectl

Mesmo sem ferramentas visuais, o kubectl oferece excelentes capacidades de monitoramento:

### Monitorar Pods em tempo real

```bash
# Watch mode: atualiza automaticamente
kubectl get pods -A --watch

# Em outro terminal, crie um Deployment:
kubectl create deployment teste --image=nginx:1.27 --replicas=3

# Observe os Pods sendo criados em tempo real no primeiro terminal!
# Ctrl+C para parar
```

### Ver eventos do cluster

```bash
# Eventos recentes (ordenados por timestamp)
kubectl get events --sort-by='.lastTimestamp' -A

# Eventos dos últimos 5 minutos
kubectl get events --field-selector reason=Created -A
```

### Verificar saúde geral

```bash
# Tudo de tudo
kubectl get all -A

# Status dos nós
kubectl get nodes -o wide

# Componentes do cluster
kubectl get componentstatuses 2>/dev/null || kubectl get --raw='/healthz'
```

### Limpar o Deployment de teste

```bash
kubectl delete deployment teste
```

---

## 🆚 Comparação de Ferramentas

| Característica | kubectl | k9s | Dashboard |
|---|---|---|---|
| **Interface** | Linha de comando | TUI (terminal) | Web (navegador) |
| **Curva de aprendizado** | Média | Baixa | Baixa |
| **Velocidade** | Rápido | Muito rápido | Mais lento |
| **Visão panorâmica** | Limitada | Boa | Excelente |
| **Interatividade** | Baixa | Alta | Alta |
| **Reproduzível** | ✅ Sim (scripts) | ❌ Não | ❌ Não |
| **Produção** | ✅ Padrão | ✅ Popular | ⚠️ Cuidado (segurança) |
| **Ideal para** | Automação, CI/CD | Monitoramento, debug | Apresentações, exploração |

---

## 🧹 Limpeza

```bash
# Parar o kubectl proxy (Ctrl+C)

# Remover o Dashboard (se quiser)
kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl delete -f labs/lab-05-dashboard-e-monitoring/manifests/dashboard.yaml

# Verificar
kubectl get all -n kubernetes-dashboard
# → "No resources found" ✅
```

---

## ✅ O que aprendemos

| Ferramenta | O que fizemos |
|---|---|
| **Kubernetes Dashboard** | Instalação, token de acesso, navegação pela interface web |
| **k9s** | Interface de terminal interativa para Pods, Deployments, logs |
| **kubectl --watch** | Monitoramento em tempo real via linha de comando |
| **Eventos do cluster** | Investigar o que está acontecendo no cluster |
| **Comparação** | kubectl (automação) vs k9s (produtividade) vs Dashboard (visual) |

---

**← Voltar ao** [README.md](../../README.md)
