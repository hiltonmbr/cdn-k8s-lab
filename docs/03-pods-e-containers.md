# 📖 03 — Pods e Containers

> **Objetivo:** Entender o Pod — a unidade atômica do Kubernetes. Aprender a anatomia de um YAML, ciclo de vida, Labels, Selectors e limites de recursos. Ao final, você saberá criar, inspecionar e gerenciar Pods com confiança.

---

## 🫛 O que é um Pod?

No Docker, a unidade básica é o **contêiner**. No Kubernetes, a unidade básica é o **Pod**.

> **Pod** = invólucro que encapsula um ou mais contêineres que compartilham a mesma rede (IP) e armazenamento (volumes).

### Analogia

Pense em um Pod como um **apartamento**:
- O **apartamento** (Pod) tem um endereço IP único
- Os **moradores** (contêineres) compartilham o mesmo endereço, a mesma cozinha (volumes) e o mesmo WiFi (rede local)
- Se o apartamento é demolido (Pod deletado), os moradores vão juntos
- O condomínio (cluster K8s) constrói um novo apartamento automaticamente

### Pod vs Contêiner

| Aspecto | Contêiner Docker | Pod Kubernetes |
|---|---|---|
| **O que é** | Processo isolado | Grupo de 1+ contêineres |
| **Rede** | IP próprio por contêiner | IP compartilhado no Pod |
| **Comunicação interna** | Via rede Docker | Via `localhost` (mesmo Pod) |
| **Quem gerencia** | Docker Engine | kubelet (agente do K8s) |
| **Efêmero?** | Sim, mas sem auto-healing | Sim, com auto-healing via Deployment |

> 💡 **Na prática:** 90% dos Pods contêm apenas **um contêiner**. Multi-container Pods existem para padrões avançados como sidecar (logging, proxy).

---

## 📝 Anatomia de um Pod YAML

Todo recurso no Kubernetes é definido por um arquivo YAML com 4 seções obrigatórias:

```yaml
# pod-nginx.yaml
apiVersion: v1                # 1. Versão da API do K8s para este recurso
kind: Pod                     # 2. Tipo do recurso (Pod, Deployment, Service...)
metadata:                     # 3. Metadados (nome, labels, namespace)
  name: meu-nginx             #    Nome único do Pod dentro do namespace
  labels:                     #    Labels: pares chave-valor para organização
    app: nginx
    env: lab
spec:                         # 4. Especificação (o que o Pod deve conter)
  containers:                 #    Lista de contêineres dentro do Pod
  - name: nginx               #    Nome do contêiner
    image: nginx:1.27         #    Imagem Docker a ser usada
    ports:
    - containerPort: 80       #    Porta que o contêiner expõe
```

### As 4 seções fundamentais

```
┌─────────────────────────────────────────────────────┐
│                   Pod YAML                           │
│                                                     │
│  ┌─────────────┐                                    │
│  │ apiVersion  │  "Qual API usar?" → v1, apps/v1    │
│  └─────────────┘                                    │
│  ┌─────────────┐                                    │
│  │    kind     │  "Que tipo de recurso?" → Pod      │
│  └─────────────┘                                    │
│  ┌─────────────┐                                    │
│  │  metadata   │  "Quem é você?" → nome, labels     │
│  └─────────────┘                                    │
│  ┌─────────────┐                                    │
│  │    spec     │  "O que você contém?" → containers  │
│  └─────────────┘                                    │
└─────────────────────────────────────────────────────┘
```

### Criar e aplicar

```bash
# Criar o Pod a partir do YAML
kubectl apply -f pod-nginx.yaml

# Verificar
kubectl get pods
# → NAME        READY   STATUS    RESTARTS   AGE
# → meu-nginx   1/1     Running   0          10s

# Detalhes completos
kubectl describe pod meu-nginx

# Logs
kubectl logs meu-nginx

# Entrar no Pod
kubectl exec -it meu-nginx -- bash

# Deletar
kubectl delete pod meu-nginx
# ou
kubectl delete -f pod-nginx.yaml
```

---

## 🔄 Ciclo de Vida de um Pod

Um Pod passa por estados definidos durante sua existência:

```
                    ┌──────────┐
    kubectl apply → │ Pending  │ ← Scheduler procurando nó
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ Running  │ ← Contêineres em execução
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              │                     │
         ┌────▼─────┐         ┌────▼─────┐
         │Succeeded │         │  Failed  │
         │(Completed)│        │ (Error)  │
         └──────────┘         └──────────┘
```

| Estado | Significado |
|---|---|
| **Pending** | Pod aceito pelo cluster, mas ainda não está rodando (baixando imagem, aguardando recursos) |
| **Running** | Pod está executando em um nó. Pelo menos um contêiner está ativo |
| **Succeeded** | Todos os contêineres terminaram com sucesso (exit code 0) |
| **Failed** | Pelo menos um contêiner terminou com erro (exit code ≠ 0) |
| **CrashLoopBackOff** | Contêiner está reiniciando repetidamente após falhas consecutivas |

### Investigando problemas

```bash
# Status geral
kubectl get pods

# Se o Pod está em Pending ou CrashLoopBackOff, investigar:
kubectl describe pod <nome-do-pod>
# → A seção "Events" mostra exatamente o que aconteceu

# Se o Pod está em Error, ver os logs:
kubectl logs <nome-do-pod>

# Logs do contêiner que crashou (anterior):
kubectl logs <nome-do-pod> --previous
```

---

## 🏷️ Labels e Selectors

Labels são **pares chave-valor** anexados a recursos. São o principal mecanismo de organização do Kubernetes.

### Por que Labels importam?

Imagine um cluster com 200 Pods. Como o K8s sabe quais Pods pertencem a qual aplicação? **Labels!**

```yaml
metadata:
  name: api-vendas-abc123
  labels:
    app: api-vendas        # ← Qual aplicação
    env: producao          # ← Qual ambiente
    team: dados            # ← Qual equipe
    version: "2.1"         # ← Qual versão
```

### Selectors — Filtrando por Labels

Os Selectors permitem **selecionar** recursos por suas Labels:

```bash
# Listar todos os Pods da aplicação "api-vendas"
kubectl get pods -l app=api-vendas

# Listar Pods de produção
kubectl get pods -l env=producao

# Listar Pods da equipe de dados em produção
kubectl get pods -l team=dados,env=producao

# Deletar todos os Pods de testes
kubectl delete pods -l env=teste
```

### Labels no K8s — O Grande Quadro

```
                    Service
                 (app=api-vendas)
                       │
          Seleciona via Label ──► "app=api-vendas"
                       │
           ┌───────────┼───────────┐
           │           │           │
    ┌──────▼──┐  ┌─────▼───┐  ┌───▼───────┐
    │ Pod #1  │  │ Pod #2  │  │  Pod #3   │
    │app=     │  │app=     │  │app=       │
    │api-vendas  │api-vendas  │api-vendas │
    │env=prod │  │env=prod │  │env=prod   │
    └─────────┘  └─────────┘  └───────────┘
```

> 💡 **Conceito fundamental:** Labels + Selectors são como o K8s "gruda" recursos uns aos outros. Um Service encontra seus Pods por Labels. Um Deployment gerencia seus Pods por Labels. Entenda isso e você entende metade do K8s.

---

## 📊 Resource Requests e Limits

No Docker, um contêiner pode usar toda a CPU e memória do host. No K8s, você **declara** quanto cada Pod precisa:

```yaml
spec:
  containers:
  - name: api
    image: python:3.12-slim
    resources:
      requests:          # Mínimo garantido
        memory: "256Mi"  # 256 MiB de RAM reservados
        cpu: "250m"      # 0.25 CPU (250 milicores)
      limits:            # Máximo permitido
        memory: "512Mi"  # Até 512 MiB (acima disso → OOMKilled)
        cpu: "500m"      # Até 0.5 CPU (acima disso → throttling)
```

### Requests vs Limits

| | Request | Limit |
|---|---|---|
| **O que é** | Reserva mínima garantida | Teto máximo permitido |
| **Para que serve** | Scheduler usa para decidir onde colocar o Pod | Impede que um Pod consuma recursos demais |
| **Se exceder** | N/A (já é o mínimo) | CPU: throttling / Memória: OOMKilled (Pod morto) |

### Unidades

| Recurso | Formato | Exemplos |
|---|---|---|
| **CPU** | milicores (m) | `100m` = 0.1 CPU, `1000m` = 1 CPU, `"2"` = 2 CPUs |
| **Memória** | Mi (Mebibytes), Gi (Gibibytes) | `256Mi`, `1Gi`, `2Gi` |

> ⚠️ **Boa prática:** Sempre defina requests e limits! Sem eles, um único Pod pode consumir toda a memória do nó e derrubar outros Pods.

---

## 📦 Pods Multi-Container (Sidecar Pattern)

Embora a maioria dos Pods tenha um único contêiner, existem casos legítimos para múltiplos contêineres no mesmo Pod:

```yaml
# pod-com-sidecar.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-com-logger
spec:
  containers:
  # Contêiner principal — a aplicação
  - name: app
    image: python:3.12-slim
    command: ["python", "-c", "import time; [print(f'Log {i}', flush=True) or time.sleep(2) for i in range(1000)]"]
    volumeMounts:
    - name: logs
      mountPath: /var/log/app

  # Sidecar — coleta e processa logs
  - name: log-collector
    image: busybox:latest
    command: ["sh", "-c", "tail -f /var/log/app/*.log 2>/dev/null || sleep infinity"]
    volumeMounts:
    - name: logs
      mountPath: /var/log/app

  volumes:
  - name: logs
    emptyDir: {}    # Volume compartilhado entre os contêineres
```

### Padrões Multi-Container

| Padrão | Descrição | Exemplo |
|---|---|---|
| **Sidecar** | Complementa o contêiner principal com funcionalidade auxiliar | Logger, proxy, sincronizador de dados |
| **Ambassador** | Proxy que simplifica comunicação com serviços externos | Proxy para banco de dados multi-região |
| **Adapter** | Adapta a saída do contêiner principal para um formato padrão | Converter métricas para formato Prometheus |

---

## 🆚 Criando Pods: Imperativo vs Declarativo

Existem duas formas de criar Pods:

### Imperativo (rápido, para testes)

```bash
# Criar Pod direto no terminal
kubectl run meu-nginx --image=nginx:1.27 --port=80

# Criar e expor numa única linha
kubectl run meu-nginx --image=nginx:1.27 --port=80 --expose
```

### Declarativo (recomendado, para tudo que importa)

```bash
# Criar arquivo YAML
cat <<EOF > pod-nginx.yaml
apiVersion: v1
kind: Pod
metadata:
  name: meu-nginx
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.27
    ports:
    - containerPort: 80
EOF

# Aplicar
kubectl apply -f pod-nginx.yaml
```

> 💡 **Regra de ouro:** Use imperativo para testes rápidos. Use declarativo para **tudo o mais**. YAMLs vão para o Git, são versionados, revisados e reproduzíveis.

### Dica — Gerar YAML a partir de comando imperativo

```bash
# Gerar YAML sem criar o Pod (--dry-run + -o yaml)
kubectl run meu-nginx --image=nginx:1.27 --port=80 \
  --dry-run=client -o yaml > pod-nginx.yaml

# Agora edite o YAML gerado conforme necessário
```

---

## 📝 Resumo

| Conceito | Definição |
|---|---|
| **Pod** | Menor unidade executável do K8s. Encapsula 1+ contêineres com rede e volumes compartilhados |
| **YAML** | Formato declarativo para definir recursos. 4 seções: apiVersion, kind, metadata, spec |
| **Labels** | Pares chave-valor para organizar e selecionar recursos |
| **Selectors** | Filtros que selecionam recursos por Labels (`-l app=nginx`) |
| **Requests** | Reserva mínima de recursos garantida ao Pod |
| **Limits** | Teto máximo de recursos que o Pod pode consumir |
| **Sidecar** | Contêiner auxiliar no mesmo Pod que complementa o principal |
| **`kubectl apply -f`** | Forma declarativa (recomendada) de criar recursos |
| **`kubectl run`** | Forma imperativa (rápida) de criar Pods |

---

**Próximo:** [04 — Deployments e ReplicaSets](04-deployments-e-replicasets.md) →
