# 🧪 Lab 04 — Spark on K8s: Big Data no Cluster

> **Objetivo:** Executar Apache Spark dentro do cluster Kubernetes — deploy de Spark Master + Workers, submeter jobs de processamento e observar a escalabilidade. Este é o link direto entre K8s e o mundo de Big Data.

> **Pré-requisito:** Cluster `k8s-lab` rodando (Lab 01). Recomendado 8 GB de RAM livre.

> **Tempo estimado:** 35 minutos

---

## 📋 O que você vai praticar

- [x] Criar namespace isolado para o Spark
- [x] Configurar RBAC (permissões) para o Spark
- [x] Fazer deploy do Spark Master e Workers no K8s
- [x] Acessar o Web UI do Spark Master
- [x] Submeter um job PySpark (WordCount)
- [x] Escalar Workers e observar o impacto
- [x] Monitorar Pods com kubectl

---

## 🏗️ Arquitetura do Lab

```
┌──────────────────────────────────────────────────────────────┐
│  Cluster K8s (kind) — Namespace: spark                       │
│                                                              │
│  ┌────────────────────┐                                      │
│  │   Spark Master     │  ← Coordena jobs e Workers           │
│  │   (Pod)            │                                      │
│  │   Porta: 7077      │  ← Comunicação com Workers           │
│  │   Web UI: 8080     │  ← Dashboard do Spark                │
│  └────────┬───────────┘                                      │
│           │                                                  │
│     ┌─────┴──────┐                                           │
│     │            │                                           │
│  ┌──▼──────┐  ┌──▼──────┐                                   │
│  │ Worker  │  │ Worker  │  ← Executam as tarefas dos jobs    │
│  │  #1     │  │  #2     │                                    │
│  │ 512m    │  │ 512m    │  ← Memória alocada                 │
│  │ 1 core  │  │ 1 core  │  ← CPU alocada                    │
│  └─────────┘  └─────────┘                                    │
│                                                              │
│  Escalável: kubectl scale deployment spark-worker --replicas=4│
└──────────────────────────────────────────────────────────────┘
```

---

## 🔬 Exercício 1: Preparar o Ambiente

### Passo 1 — Criar o Namespace

```bash
kubectl apply -f labs/lab-04-spark-on-k8s/manifests/spark-namespace.yaml
# → namespace/spark created
```

### Passo 2 — Configurar RBAC

```bash
kubectl apply -f labs/lab-04-spark-on-k8s/manifests/spark-rbac.yaml
# → serviceaccount/spark created
# → role.rbac.authorization.k8s.io/spark-role created
# → rolebinding.rbac.authorization.k8s.io/spark-role-binding created
```

> 💡 **RBAC (Role-Based Access Control)** define quem pode fazer o quê no cluster. O Spark precisa de permissão para criar e gerenciar Pods de Executor dinamicamente.

---

## 🔬 Exercício 2: Deploy do Spark Master

### Passo 1 — Criar o Master

```bash
kubectl apply -f labs/lab-04-spark-on-k8s/manifests/spark-master.yaml
# → deployment.apps/spark-master created
# → service/spark-master created
```

### Passo 2 — Verificar

```bash
kubectl get pods -n spark
# → NAME                            READY   STATUS    RESTARTS   AGE
# → spark-master-xxx-abc12          1/1     Running   0          20s
```

### Passo 3 — Acessar o Web UI do Spark

```bash
kubectl port-forward svc/spark-master -n spark 4040:8080
# → Forwarding from 127.0.0.1:4040 -> 8080
```

Abra: **http://localhost:4040** — Spark Master UI! 🎉

Você verá:
- **Workers:** 0 (nenhum ainda)
- **Applications:** Nenhuma em execução
- **Status:** ALIVE

> Mantenha este port-forward rodando em um terminal separado.

---

## 🔬 Exercício 3: Deploy dos Workers

### Passo 1 — Criar os Workers

```bash
kubectl apply -f labs/lab-04-spark-on-k8s/manifests/spark-worker.yaml
# → deployment.apps/spark-worker created
```

### Passo 2 — Verificar

```bash
kubectl get pods -n spark
# → NAME                            READY   STATUS    RESTARTS   AGE
# → spark-master-xxx-abc12          1/1     Running   0          1m
# → spark-worker-xxx-def34          1/1     Running   0          10s
# → spark-worker-xxx-ghi56          1/1     Running   0          10s
```

### Passo 3 — Verificar no Web UI

Recarregue **http://localhost:4040**:
- **Workers:** 2 ← Os Workers se registraram no Master!
- **Cores in use:** 2
- **Memory in use:** 1.0 GiB

### Passo 4 — Ver a distribuição nos nós

```bash
kubectl get pods -n spark -o wide
# → NAME              NODE
# → spark-master-...  k8s-lab-worker
# → spark-worker-...  k8s-lab-worker2  ← Distribuídos pelo Scheduler!
# → spark-worker-...  k8s-lab-worker
```

---

## 🔬 Exercício 4: Submeter um Job PySpark

### Passo 1 — Copiar o job para dentro do Master

```bash
# Pegar o nome do Pod do Master
MASTER_POD=$(kubectl get pods -n spark -l app=spark-master -o jsonpath='{.items[0].metadata.name}')

# Copiar o script wordcount.py para dentro do Pod
kubectl cp labs/lab-04-spark-on-k8s/jobs/wordcount.py spark/$MASTER_POD:/tmp/wordcount.py
```

### Passo 2 — Submeter o job via spark-submit

```bash
kubectl exec -it $MASTER_POD -n spark -- \
  spark-submit \
    --master spark://spark-master:7077 \
    /tmp/wordcount.py
```

### Passo 3 — Observar a execução

A saída mostrará o processamento do WordCount:

```
============================================================
🚀 WordCount — Spark on Kubernetes
============================================================

📊 Top 15 palavras mais frequentes:
----------------------------------------
+-------------+-----+
|palavra      |count|
+-------------+-----+
|kubernetes   |6    |
|de           |6    |
|spark        |5    |
|dados        |5    |
|contêineres  |3    |
|docker       |3    |
|em           |3    |
|...          |...  |
+-------------+-----+

📈 Total de palavras: 73
📈 Palavras únicas: 38
============================================================
```

> 🧠 **O que aconteceu?** O Spark Driver rodou dentro do Pod do Master, distribuiu tarefas para os 2 Workers, processou os dados em paralelo e agregou os resultados. Tudo dentro do Kubernetes!

---

## 🔬 Exercício 5: Escalar Workers

### Passo 1 — Escalar para 4 Workers

```bash
kubectl scale deployment spark-worker --replicas=4 -n spark

# Verificar
kubectl get pods -n spark
# → 4 Workers rodando!
```

### Passo 2 — Verificar no Web UI

Recarregue http://localhost:4040:
- **Workers:** 4 ← Escalou!
- **Cores:** 4
- **Memory:** 2.0 GiB

### Passo 3 — Submeter o job novamente e comparar

```bash
kubectl exec -it $MASTER_POD -n spark -- \
  spark-submit \
    --master spark://spark-master:7077 \
    /tmp/wordcount.py
```

### Passo 4 — Reduzir Workers

```bash
kubectl scale deployment spark-worker --replicas=1 -n spark

# Verificar: Pods excedentes terminando
kubectl get pods -n spark --watch
```

> 💡 **Este é o poder do Spark on K8s!** Em ambientes reais, o Horizontal Pod Autoscaler (HPA) escalaria automaticamente os Workers com base na carga de trabalho. Sem provisionamento manual.

---

## 🔬 Exercício 6: Monitorar com kubectl

### Ver logs em tempo real

```bash
# Logs do Master
kubectl logs -f $(kubectl get pods -n spark -l app=spark-master -o jsonpath='{.items[0].metadata.name}') -n spark

# Logs de um Worker
kubectl logs -f $(kubectl get pods -n spark -l app=spark-worker -o jsonpath='{.items[0].metadata.name}') -n spark
```

### Ver uso de recursos

```bash
# Detalhes de um Pod (eventos, recursos)
kubectl describe pod $MASTER_POD -n spark

# Ver todos os recursos do namespace spark
kubectl get all -n spark
```

---

## 🧹 Limpeza

```bash
# Parar o port-forward (Ctrl+C)

# Remover tudo do namespace spark
kubectl delete namespace spark

# Verificar
kubectl get all -n spark
# → "No resources found" ✅
```

---

## ✅ O que aprendemos

| Conceito | O que fizemos |
|---|---|
| **Namespace** | Isolamento do ambiente Spark (`spark`) |
| **RBAC** | Permissões para o Spark criar Pods de Executor |
| **Spark Master** | Coordenador do cluster Spark, rodando como Pod |
| **Spark Workers** | Executores das tarefas, gerenciados como Deployment |
| **spark-submit** | Submissão de jobs PySpark dentro do cluster K8s |
| **Scaling** | Escalar Workers de 2 para 4 e voltar com um comando |
| **Web UI** | Dashboard do Spark acessível via port-forward |
| **kubectl cp** | Copiar arquivos para dentro de Pods |

### 🔗 Relação com Big Data

| Antes (YARN/Hadoop) | Agora (Spark on K8s) |
|---|---|
| Cluster fixo e pré-alocado | Pods criados sob demanda |
| Capacidade ociosa em períodos sem jobs | Recursos liberados quando o job termina |
| Difícil de escalar (adicionar máquinas) | `kubectl scale` ou HPA automático |
| Infraestrutura separada para cada ferramenta | Spark, Kafka, Airflow no mesmo cluster K8s |

---

**Próximo:** [Lab 05 — Dashboard e Monitoramento](../lab-05-dashboard-e-monitoring/README.md) →
