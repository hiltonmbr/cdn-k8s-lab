# 📖 04 — Deployments e ReplicaSets

> **Objetivo:** Entender por que nunca criamos Pods "soltos" em produção, e como Deployments gerenciam réplicas, atualizações e rollbacks automaticamente. Ao final, você dominará o recurso mais importante do K8s para aplicações stateless.

---

## 🤔 Por que Não Usar Pods Diretamente?

No módulo anterior, criamos Pods com `kubectl run` e `kubectl apply`. Mas Pods "soltos" têm um problema fatal:

```bash
# Criar um Pod
kubectl run minha-api --image=python:3.12-slim

# Simular uma falha: deletar o Pod
kubectl delete pod minha-api

# Verificar
kubectl get pods
# → Nenhum Pod! 😱 O K8s não recriou automaticamente.
```

**Pods soltos não têm auto-healing!** Quando morrem, morrem para sempre.

> 💡 **Regra de ouro:** Nunca crie Pods diretamente em produção. Use **Deployments** — eles garantem que seus Pods são recriados automaticamente.

---

## 🔄 ReplicaSet: Garantindo N Réplicas

O **ReplicaSet** é o recurso que garante que um número específico de Pods idênticos esteja sempre rodando:

```
┌──────────────────────────────────────────────────┐
│              ReplicaSet (replicas: 3)             │
│                                                  │
│  "Eu garanto que SEMPRE haverá 3 Pods ativos"    │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Pod #1  │  │  Pod #2  │  │  Pod #3  │       │
│  │  nginx   │  │  nginx   │  │  nginx   │       │
│  └──────────┘  └──────────┘  └──────────┘       │
│                                                  │
│  Se Pod #2 morrer → cria Pod #4 automaticamente  │
└──────────────────────────────────────────────────┘
```

Na prática, **você nunca cria ReplicaSets diretamente** — o Deployment faz isso por você. Mas é importante entender que o Deployment gerencia ReplicaSets, que por sua vez gerenciam Pods:

```
Deployment → cria → ReplicaSet → cria → Pod, Pod, Pod
```

---

## 🚀 Deployment: O Recurso Principal

O **Deployment** é o recurso mais usado no Kubernetes. Ele gerencia ReplicaSets e adiciona:
- ✅ Rolling updates (atualizar sem downtime)
- ✅ Rollback (voltar à versão anterior)
- ✅ Scaling (aumentar/diminuir réplicas)
- ✅ Auto-healing (recria Pods que falham)

### Anatomia de um Deployment

```yaml
# deployment-api.yaml
apiVersion: apps/v1           # API do grupo "apps" versão 1
kind: Deployment              # Tipo: Deployment
metadata:
  name: api-vendas            # Nome do Deployment
  labels:
    app: api-vendas
spec:
  replicas: 3                 # Manter 3 Pods sempre ativos

  selector:                   # Como o Deployment encontra seus Pods
    matchLabels:
      app: api-vendas         # "Gerencio todos os Pods com label app=api-vendas"

  template:                   # Template do Pod (como cada Pod será criado)
    metadata:
      labels:
        app: api-vendas       # ⚠️ DEVE coincidir com o selector acima!
    spec:
      containers:
      - name: api
        image: python:3.12-slim
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

### Hierarquia de recursos

```
┌──────────────────────────────────────────────────────────┐
│                    Deployment                             │
│                   (api-vendas)                            │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │               ReplicaSet                           │  │
│  │        (api-vendas-7d8f9b6c5)                     │  │
│  │                                                    │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐     │  │
│  │  │   Pod      │ │   Pod      │ │   Pod      │     │  │
│  │  │ api-vendas │ │ api-vendas │ │ api-vendas │     │  │
│  │  │ -7d8f-abc │ │ -7d8f-def │ │ -7d8f-ghi │     │  │
│  │  └────────────┘ └────────────┘ └────────────┘     │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## ⚙️ Comandos Essenciais para Deployments

```bash
# ── Criar / Atualizar ──
kubectl apply -f deployment-api.yaml            # Criar ou atualizar

# ── Consultar ──
kubectl get deployments                          # Listar Deployments
kubectl get rs                                   # Listar ReplicaSets
kubectl get pods                                 # Listar Pods criados
kubectl describe deployment api-vendas           # Detalhes completos

# ── Escalar ──
kubectl scale deployment api-vendas --replicas=5  # Escalar para 5 réplicas
kubectl scale deployment api-vendas --replicas=1  # Reduzir para 1 réplica

# ── Atualizar imagem ──
kubectl set image deployment/api-vendas \
  api=python:3.13-slim                           # Atualizar versão da imagem

# ── Rollout (status e histórico) ──
kubectl rollout status deployment api-vendas     # Ver progresso da atualização
kubectl rollout history deployment api-vendas    # Ver histórico de versões

# ── Rollback ──
kubectl rollout undo deployment api-vendas       # Voltar à versão anterior
kubectl rollout undo deployment api-vendas \
  --to-revision=2                                # Voltar a uma revisão específica

# ── Deletar ──
kubectl delete deployment api-vendas             # Remove Deployment + RS + Pods
kubectl delete -f deployment-api.yaml            # Remove via arquivo
```

---

## 🔄 Rolling Update: Atualização Sem Downtime

Quando você atualiza a imagem de um Deployment, o K8s faz uma **atualização gradual** (rolling update):

```
Estado inicial: 3 Pods com imagem v1
                                                    
Passo 1: Cria 1 Pod v2, mantém 3 v1         (4 Pods total)
Passo 2: Pod v2 está Ready → Remove 1 v1    (3 Pods total)
Passo 3: Cria outro Pod v2, mantém 2 v1     (4 Pods total)
Passo 4: Pod v2 está Ready → Remove 1 v1    (3 Pods total)
Passo 5: Cria último Pod v2, mantém 1 v1    (4 Pods total)
Passo 6: Pod v2 está Ready → Remove último v1 (3 Pods total)

Estado final: 3 Pods com imagem v2 ✅
```

```
v1 ████████████████████░░░░░░░░░░ → morrendo gradualmente
v2 ░░░░░░░░░░████████████████████ → nascendo gradualmente

Usuários NUNCA ficam sem serviço! Sempre há Pods respondendo.
```

### Configurando a estratégia

```yaml
spec:
  strategy:
    type: RollingUpdate       # Padrão — atualiza gradualmente
    rollingUpdate:
      maxSurge: 1             # Máximo de Pods extras durante a atualização
      maxUnavailable: 0       # Nenhum Pod pode ficar indisponível
```

| Estratégia | Comportamento | Quando usar |
|---|---|---|
| **RollingUpdate** (padrão) | Atualiza gradualmente, sem downtime | Maioria dos casos |
| **Recreate** | Mata todos os Pods v1, depois cria todos v2 | Quando v1 e v2 não podem coexistir |

---

## ↩️ Rollback: Voltando Atrás

Fez um deploy de uma versão com bug? Rollback em segundos:

```bash
# Ver histórico de revisões
kubectl rollout history deployment api-vendas
# → REVISION  CHANGE-CAUSE
# → 1         <none>
# → 2         <none>
# → 3         <none>

# Voltar à revisão anterior (2 → 1 passo atrás)
kubectl rollout undo deployment api-vendas

# Voltar a uma revisão específica
kubectl rollout undo deployment api-vendas --to-revision=1

# Verificar que o rollback foi aplicado
kubectl rollout status deployment api-vendas
```

> 💡 **Como funciona:** O K8s mantém os ReplicaSets antigos (com réplicas=0). No rollback, ele simplesmente escala o ReplicaSet antigo de volta e escala o novo para zero. Rápido e seguro.

---

## 📈 Horizontal Pod Autoscaler (HPA)

O HPA escala o número de réplicas **automaticamente** com base em métricas:

```bash
# Escalar automaticamente entre 2 e 10 réplicas,
# mantendo o uso médio de CPU em 50%
kubectl autoscale deployment api-vendas \
  --min=2 \
  --max=10 \
  --cpu-percent=50
```

```
                    Uso de CPU
                        │
     Alta demanda ──►   │  ████████ 80%  → HPA: escalar para 8 réplicas
                        │  ████████
     Demanda normal ──► │  ████     50%  → HPA: manter 5 réplicas
                        │  ████
     Baixa demanda ──►  │  ██       20%  → HPA: reduzir para 2 réplicas
                        │  ██
                        └──────────────
                          Réplicas
```

> ⚠️ **Pré-requisito:** O HPA precisa do **Metrics Server** instalado no cluster para ler métricas de CPU e memória dos Pods.

---

## 📝 Resumo

| Conceito | Definição |
|---|---|
| **Deployment** | Gerencia ReplicaSets e Pods. Recurso principal para aplicações stateless |
| **ReplicaSet** | Garante N réplicas de um Pod sempre ativas. Criado automaticamente pelo Deployment |
| **Rolling Update** | Atualização gradual da imagem, sem downtime |
| **Rollback** | Reverter para uma versão anterior do Deployment |
| **Scaling** | Aumentar/diminuir réplicas manualmente ou via HPA |
| **HPA** | Horizontal Pod Autoscaler — escala réplicas com base em métricas (CPU, memória) |
| **Strategy** | RollingUpdate (gradual, sem downtime) ou Recreate (mata tudo, recria tudo) |

---

**Próximo:** [05 — Services e Networking](05-services-e-networking.md) →
