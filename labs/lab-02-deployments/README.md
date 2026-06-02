# 🧪 Lab 02 — Deployments na Prática

> **Objetivo:** Criar Deployments, escalar réplicas, realizar rolling updates e rollbacks. Este lab demonstra por que Deployments são o recurso mais importante do K8s para aplicações stateless.

> **Pré-requisito:** Cluster `k8s-lab` rodando (Lab 01). Docker instalado.

> **Tempo estimado:** 30 minutos

---

## 📋 O que você vai praticar

- [x] Construir uma imagem Docker e carregá-la no cluster kind
- [x] Criar um Deployment com 3 réplicas
- [x] Testar auto-healing (deletar Pods e ver recriação)
- [x] Escalar réplicas manualmente
- [x] Expor o Deployment via Service NodePort
- [x] Realizar rolling update (atualizar versão da API)
- [x] Fazer rollback para versão anterior

---

## 🔬 Exercício 1: Preparação — Build da Imagem

### Passo 1 — Construir a imagem Docker da API

```bash
# A partir da raiz do cdn-k8s-lab
cd labs/lab-02-deployments/app

# Construir a imagem versão 1.0
docker build -t api-vendas:1.0 .
# → Successfully tagged api-vendas:1.0
```

### Passo 2 — Carregar a imagem no cluster kind

O kind usa seu próprio registro de imagens. Precisamos **carregar** a imagem local para dentro do cluster:

```bash
# Carregar imagem para o cluster kind
kind load docker-image api-vendas:1.0 --name k8s-lab
# → Image: "api-vendas:1.0" with ID "sha256:..." loaded
```

> 💡 **Por que isso é necessário?** O cluster kind roda dentro de contêineres Docker. Ele não tem acesso direto às imagens do Docker Engine do seu host. O comando `kind load` copia a imagem para dentro dos nós do cluster.

### Passo 3 — Verificar

```bash
# Voltar para a raiz do lab
cd ../../..
```

---

## 🔬 Exercício 2: Primeiro Deployment

### Passo 1 — Criar o Deployment

```bash
kubectl apply -f labs/lab-02-deployments/manifests/api-deployment.yaml
# → deployment.apps/api-vendas created
```

### Passo 2 — Observar a criação em tempo real

```bash
# Em um terminal separado, observe os Pods sendo criados:
kubectl get pods --watch
# → NAME                         READY   STATUS              RESTARTS   AGE
# → api-vendas-7d8f9b6c5-abc12   0/1     ContainerCreating   0          1s
# → api-vendas-7d8f9b6c5-def34   0/1     ContainerCreating   0          1s
# → api-vendas-7d8f9b6c5-ghi56   0/1     ContainerCreating   0          1s
# → api-vendas-7d8f9b6c5-abc12   1/1     Running             0          3s
# → api-vendas-7d8f9b6c5-def34   1/1     Running             0          4s
# → api-vendas-7d8f9b6c5-ghi56   1/1     Running             0          4s
# Ctrl+C para parar
```

### Passo 3 — Inspecionar a hierarquia

```bash
# Deployment
kubectl get deployments
# → NAME         READY   UP-TO-DATE   AVAILABLE   AGE
# → api-vendas   3/3     3            3           30s

# ReplicaSet (criado automaticamente pelo Deployment)
kubectl get replicasets
# → NAME                    DESIRED   CURRENT   READY   AGE
# → api-vendas-7d8f9b6c5   3         3         3       30s

# Pods (criados automaticamente pelo ReplicaSet)
kubectl get pods -o wide
# → Observe: os Pods estão distribuídos entre os Worker Nodes!
```

> 🧠 **Hierarquia:** Deployment → ReplicaSet → Pods. Você criou apenas o Deployment, e ele criou o resto automaticamente!

---

## 🔬 Exercício 3: Auto-Healing

### Passo 1 — Deletar um Pod e observar

```bash
# Pegar o nome de um dos Pods
POD_NAME=$(kubectl get pods -l app=api-vendas -o jsonpath='{.items[0].metadata.name}')

# Deletar o Pod
kubectl delete pod $POD_NAME
# → pod "api-vendas-7d8f9b6c5-abc12" deleted

# IMEDIATAMENTE verificar:
kubectl get pods
# → Um novo Pod está sendo criado! 🎉
# → api-vendas-7d8f9b6c5-xyz99   0/1   ContainerCreating   0   2s
# → api-vendas-7d8f9b6c5-def34   1/1   Running             0   2m
# → api-vendas-7d8f9b6c5-ghi56   1/1   Running             0   2m
```

> 💡 **Isso é auto-healing!** O ReplicaSet percebeu que havia 2 Pods (desejado: 3) e criou um novo automaticamente. Sem intervenção humana.

### Passo 2 — Testar resiliência extrema

```bash
# Deletar TODOS os Pods de uma vez!
kubectl delete pods -l app=api-vendas

# Verificar imediatamente
kubectl get pods --watch
# → Todos sendo recriados automaticamente! O K8s SEMPRE mantém 3 réplicas.
```

---

## 🔬 Exercício 4: Scaling

### Passo 1 — Escalar para 5 réplicas

```bash
kubectl scale deployment api-vendas --replicas=5

# Verificar
kubectl get pods
# → Agora há 5 Pods!
```

### Passo 2 — Reduzir para 2 réplicas

```bash
kubectl scale deployment api-vendas --replicas=2

# Verificar: Pods excedentes sendo terminados
kubectl get pods --watch
# → 3 Pods em estado "Terminating"
```

### Passo 3 — Voltar para 3 réplicas

```bash
kubectl scale deployment api-vendas --replicas=3
```

---

## 🔬 Exercício 5: Service — Expondo a API

### Passo 1 — Criar o Service

```bash
kubectl apply -f labs/lab-02-deployments/manifests/api-service.yaml
# → service/api-vendas created
```

### Passo 2 — Verificar

```bash
kubectl get services
# → NAME         TYPE       CLUSTER-IP     PORT(S)        AGE
# → api-vendas   NodePort   10.96.xx.xx    80:30001/TCP   5s
```

### Passo 3 — Acessar a API

```bash
# Acessar via NodePort
curl http://localhost:30001
# → {"app":"API de Vendas","hostname":"api-vendas-7d8f9b6c5-abc12","version":"1.0",...}

# Chamar várias vezes — observe o hostname mudando!
for i in {1..6}; do curl -s http://localhost:30001 | python3 -m json.tool | grep hostname; done
# → "hostname": "api-vendas-7d8f9b6c5-abc12"
# → "hostname": "api-vendas-7d8f9b6c5-def34"  ← Pod diferente!
# → "hostname": "api-vendas-7d8f9b6c5-ghi56"  ← Outro Pod!
# → "hostname": "api-vendas-7d8f9b6c5-abc12"
# → ...
```

> 🧠 **Load Balancing!** O Service distribui as requisições entre os 3 Pods automaticamente (round-robin). Cada resposta vem de um Pod diferente!

### Passo 4 — Ver dados de vendas

```bash
curl http://localhost:30001/vendas | python3 -m json.tool
# → { "vendas": [...], "total": 6650.0 }

curl http://localhost:30001/health | python3 -m json.tool
# → { "status": "healthy", "version": "1.0" }
```

---

## 🔬 Exercício 6: Rolling Update

Vamos atualizar a API da versão 1.0 para 2.0 **sem downtime**!

### Passo 1 — Construir versão 2.0

Edite o arquivo `labs/lab-02-deployments/app/app.py` e altere a variável `VERSION`:

```python
VERSION = os.environ.get("APP_VERSION", "2.0")  # ← Mudar de 1.0 para 2.0
```

E adicione um novo endpoint:

```python
@app.route("/v2/info")
def info_v2():
    return jsonify({"message": "Endpoint novo da v2!", "pod": socket.gethostname()})
```

```bash
# Reconstruir com nova tag
cd labs/lab-02-deployments/app
docker build -t api-vendas:2.0 .

# Carregar no cluster
kind load docker-image api-vendas:2.0 --name k8s-lab

cd ../../..
```

### Passo 2 — Disparar rolling update

```bash
# Em um terminal, observe os Pods:
kubectl get pods --watch

# Em outro terminal, atualize a imagem:
kubectl set image deployment/api-vendas api=api-vendas:2.0
```

### Passo 3 — Observar o rolling update

```bash
# Status da atualização
kubectl rollout status deployment api-vendas
# → Waiting for rollout to finish: 1 out of 3 new replicas have been updated...
# → Waiting for rollout to finish: 2 out of 3 new replicas have been updated...
# → deployment "api-vendas" successfully rolled out ✅

# Verificar a versão
curl http://localhost:30001 | python3 -m json.tool
# → "version": "2.0" ← Atualizado!
```

### Passo 4 — Ver o histórico

```bash
kubectl rollout history deployment api-vendas
# → REVISION  CHANGE-CAUSE
# → 1         <none>
# → 2         <none>
```

---

## 🔬 Exercício 7: Rollback

Ops! A versão 2.0 tem um bug. Vamos reverter para 1.0:

### Passo 1 — Executar rollback

```bash
kubectl rollout undo deployment api-vendas
# → deployment.apps/api-vendas rolled back
```

### Passo 2 — Verificar

```bash
# Aguardar rollback completar
kubectl rollout status deployment api-vendas

# Testar
curl http://localhost:30001 | python3 -m json.tool
# → "version": "1.0" ← De volta à versão 1.0! 🎉
```

> 💡 **Como funciona:** O K8s mantém os ReplicaSets antigos (com 0 réplicas). No rollback, ele escala o ReplicaSet antigo de volta. Os Pods da versão 2.0 são terminados e os da 1.0 são recriados. Tudo automático!

```bash
# Verificar: dois ReplicaSets existem
kubectl get replicasets
# → NAME                    DESIRED   CURRENT   READY
# → api-vendas-7d8f9b6c5   3         3         3     ← v1.0 (ativo)
# → api-vendas-a1b2c3d4e   0         0         0     ← v2.0 (inativo)
```

---

## 🧹 Limpeza

```bash
# Remover Deployment e Service
kubectl delete -f labs/lab-02-deployments/manifests/

# Verificar
kubectl get all
# → Apenas os serviços de sistema

# (Opcional) Remover imagens
docker rmi api-vendas:1.0 api-vendas:2.0
```

---

## ✅ O que aprendemos

| Conceito | Comando |
|---|---|
| Build + load para kind | `docker build -t img:tag .` + `kind load docker-image img:tag` |
| Criar Deployment | `kubectl apply -f deployment.yaml` |
| Ver hierarquia | `kubectl get deploy,rs,pods` |
| Auto-healing | Deletar Pod → K8s recria automaticamente |
| Escalar | `kubectl scale deployment app --replicas=N` |
| Expor via Service | `kubectl apply -f service.yaml` (NodePort) |
| Load balancing | Service distribui tráfego entre Pods |
| Rolling update | `kubectl set image deployment/app container=img:nova-tag` |
| Ver rollout | `kubectl rollout status deployment app` |
| Rollback | `kubectl rollout undo deployment app` |
| Histórico | `kubectl rollout history deployment app` |

---

**Próximo:** [Lab 03 — App Fullstack (K8s + Banco Externo)](../lab-03-app-fullstack/README.md) →
