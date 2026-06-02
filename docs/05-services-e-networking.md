# 📖 05 — Services e Networking

> **Objetivo:** Entender como Pods se comunicam entre si e com o mundo externo. Aprender os tipos de Service, DNS interno e Ingress. Ao final, você saberá expor aplicações de forma segura e estável.

---

## 🤔 O Problema: Pods São Efêmeros

Você aprendeu que Pods podem ser destruídos e recriados a qualquer momento. Quando isso acontece, eles recebem **novos IPs**:

```bash
# Criar Deployment com 3 réplicas
kubectl apply -f deployment-api.yaml

# Ver IPs dos Pods
kubectl get pods -o wide
# → NAME                     IP            NODE
# → api-abc123   10.244.1.5   worker-1
# → api-def456   10.244.2.3   worker-2
# → api-ghi789   10.244.1.7   worker-1

# Deletar um Pod (K8s recria automaticamente)
kubectl delete pod api-abc123

# Ver IPs novamente
kubectl get pods -o wide
# → api-xyz999   10.244.2.8   worker-2  ← NOVO IP!
# → api-def456   10.244.2.3   worker-2
# → api-ghi789   10.244.1.7   worker-1
```

**Problema:** Se outro serviço precisa acessar essa API, para qual IP ele aponta? O IP muda a cada recriação!

> 💡 **Analogia:** Imagine que o número de telefone dos seus colegas mudasse toda vez que eles trocassem de aparelho. Seria impossível ligar para alguém. O **Service** é como uma "lista telefônica" com um número fixo que nunca muda.

---

## 🌐 Service: Endereço Virtual Estável

Um **Service** cria um endereço virtual fixo (**Cluster IP**) que roteia tráfego para os Pods corretos, independente de quantos existam ou quais IPs tenham:

```yaml
# service-api.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-vendas           # Nome do Service (e entrada DNS!)
spec:
  selector:
    app: api-vendas           # "Roteie tráfego para Pods com esta label"
  ports:
  - port: 80                  # Porta do Service
    targetPort: 8000           # Porta do contêiner nos Pods
  type: ClusterIP              # Tipo (padrão): acessível apenas dentro do cluster
```

```
              ┌──────────────────────────────────────────┐
              │         Service: api-vendas               │
              │      ClusterIP: 10.96.45.123              │
              │      DNS: api-vendas.default.svc           │
              │                                           │
              │      selector: app=api-vendas              │
              └──────────┬───────────┬───────────┬────────┘
                         │           │           │
                   Balanceamento de carga (round-robin)
                         │           │           │
                  ┌──────▼──┐  ┌─────▼───┐  ┌───▼───────┐
                  │ Pod #1  │  │ Pod #2  │  │  Pod #3   │
                  │10.244.  │  │10.244.  │  │10.244.    │
                  │ 1.5     │  │ 2.3     │  │ 1.7       │
                  └─────────┘  └─────────┘  └───────────┘
```

---

## 🏷️ Tipos de Service

### 1. ClusterIP (padrão) — Acesso interno

Cria um IP virtual acessível **apenas dentro do cluster**. Ideal para comunicação entre serviços:

```yaml
spec:
  type: ClusterIP    # Padrão — pode omitir
  ports:
  - port: 80
    targetPort: 8000
```

```
┌─────────────────────────────────────────────────┐
│                   Cluster K8s                    │
│                                                  │
│  Pod A ──► api-vendas:80 ──► Pod B (api-vendas) │
│                                                  │
│  ✅ Funciona dentro do cluster                    │
│  ❌ NÃO acessível do seu navegador               │
└─────────────────────────────────────────────────┘
```

### 2. NodePort — Acesso via porta do nó

Expõe o Service em uma porta fixa (30000-32767) em **todos os nós** do cluster:

```yaml
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 8000
    nodePort: 30001    # Porta no nó (30000-32767)
```

```
┌──────────────────────────────────────────────────────────┐
│  Seu Navegador                                           │
│     │                                                    │
│     │ http://localhost:30001                              │
│     ▼                                                    │
│  ┌─────────────────────────────────────────────────┐     │
│  │  Nó do Cluster (porta 30001)                    │     │
│  │     │                                            │     │
│  │     ▼                                            │     │
│  │  Service (ClusterIP:80)                          │     │
│  │     │                                            │     │
│  │     ├──► Pod #1                                  │     │
│  │     ├──► Pod #2                                  │     │
│  │     └──► Pod #3                                  │     │
│  └─────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

### 3. LoadBalancer — Balanceador na nuvem

Em provedores cloud (AWS, GCP, Azure), cria automaticamente um balanceador de carga externo com IP público:

```yaml
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
```

> ⚠️ **No kind:** O tipo LoadBalancer não provisiona um IP externo real (não há cloud provider). Use **NodePort** ou **port-forward** para acessar serviços localmente.

### Resumo dos tipos

| Tipo | Acesso | Uso típico | Funciona no kind? |
|---|---|---|---|
| **ClusterIP** | Apenas dentro do cluster | Comunicação entre serviços | ✅ Sim |
| **NodePort** | IP do nó + porta (30000-32767) | Desenvolvimento, testes | ✅ Sim |
| **LoadBalancer** | IP público (cloud) | Produção na nuvem | ⚠️ Parcial |
| **ExternalName** | DNS externo (CNAME) | Apontar para serviços externos | ✅ Sim |

---

## 🌍 DNS Interno do Kubernetes

O K8s possui um servidor DNS interno que resolve **nomes de Services** para seus ClusterIPs. Formato:

```
<nome-do-service>.<namespace>.svc.cluster.local
```

Na prática, dentro do **mesmo namespace**, você pode usar apenas o nome:

```python
# Python — conectar à API de vendas (mesmo namespace)
import requests
response = requests.get("http://api-vendas:80/health")

# Python — conectar ao banco no namespace "database"
import psycopg2
conn = psycopg2.connect(host="postgres.database.svc.cluster.local", ...)
```

```
┌────────────────────────────────────────────────────────┐
│                    DNS Interno K8s                       │
│                                                         │
│  Nome curto (mesmo namespace):                          │
│    api-vendas  →  10.96.45.123                          │
│                                                         │
│  Nome completo (outro namespace):                       │
│    api-vendas.default.svc.cluster.local → 10.96.45.123 │
│                                                         │
│  Nome completo (namespace database):                    │
│    postgres.database.svc.cluster.local → 10.96.12.50   │
└────────────────────────────────────────────────────────┘
```

> 💡 **Comparação com Docker:** No Docker Compose, contêineres na mesma rede se encontram pelo nome do serviço (`postgres`, `redis`). No K8s é igual — mas via **Service**, não via nome do Pod.

---

## 🔀 ExternalName: Apontando para Fora do Cluster

O Service do tipo **ExternalName** não roteia para Pods — ele funciona como um **alias DNS** para um serviço externo:

```yaml
# postgres-external-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: fullstack
spec:
  type: ExternalName
  externalName: host.docker.internal   # Aponta para o host (onde roda o Docker/PostgreSQL)
```

```
┌────────────────────────────────────────────────────────┐
│  Cluster K8s                                           │
│                                                        │
│  Pod (API) ──► "postgres" ──► DNS resolve para         │
│                                host.docker.internal    │
│                                    │                   │
└────────────────────────────────────│───────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────┐
│  Host (seu computador)                                 │
│                                                        │
│  PostgreSQL rodando via Docker (fora do cluster)       │
│  Porta: 5432                                           │
└────────────────────────────────────────────────────────┘
```

> 💡 **Caso de uso real:** Sua empresa tem um banco de dados gerenciado na AWS RDS. A API roda no K8s. Use ExternalName para que a API acesse o banco pelo nome `postgres` dentro do cluster — se um dia migrar o banco para dentro do K8s, basta trocar o tipo do Service. O código da API **não muda**.

---

## 🔌 Port-Forward: Acesso Rápido para Debug

O `kubectl port-forward` cria um túnel temporário do seu computador para um Pod ou Service:

```bash
# Encaminhar porta do Pod
kubectl port-forward pod/api-vendas-abc123 8080:8000
# → http://localhost:8080 acessa o Pod diretamente

# Encaminhar porta do Service (balanceia entre Pods)
kubectl port-forward svc/api-vendas 8080:80
# → http://localhost:8080 acessa via Service

# Encaminhar para um Deployment
kubectl port-forward deployment/api-vendas 8080:8000
```

> ⚠️ **port-forward é para desenvolvimento/debug.** Não use em produção — o túnel fecha quando você interrompe o comando (Ctrl+C). Para acesso permanente, use NodePort ou Ingress.

---

## 📝 Resumo

| Conceito | Definição |
|---|---|
| **Service** | Endereço virtual estável que roteia tráfego para Pods via Labels |
| **ClusterIP** | Tipo padrão — acessível apenas dentro do cluster |
| **NodePort** | Expõe na porta do nó (30000-32767) — acesso externo |
| **LoadBalancer** | Cria balanceador na nuvem com IP público |
| **ExternalName** | Alias DNS para serviços fora do cluster |
| **DNS interno** | `<service>.<namespace>.svc.cluster.local` |
| **port-forward** | Túnel temporário para debug local |

---

**Próximo:** [06 — Volumes e ConfigMaps](06-volumes-e-configmaps.md) →
