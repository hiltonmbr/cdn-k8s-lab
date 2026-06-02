# 🧪 Lab 03 — App Fullstack: K8s + Banco Externo

> **Objetivo:** Criar uma aplicação completa com API Python rodando no cluster K8s e PostgreSQL rodando **fora** do cluster como contêiner Docker — simulando o cenário real de banco de dados gerenciado (AWS RDS, Google Cloud SQL, servidor dedicado).

> **Pré-requisito:** Cluster `k8s-lab` rodando (Lab 01). Docker instalado.

> **Tempo estimado:** 40 minutos

---

## 📋 O que você vai praticar

- [x] Subir PostgreSQL como contêiner Docker externo (fora do K8s)
- [x] Criar Namespace para isolar o projeto
- [x] Usar Secrets para armazenar credenciais do banco
- [x] Criar Service ExternalName para acessar serviço externo
- [x] Deploy da API Flask com conexão ao banco externo
- [x] Deploy do pgAdmin para gerenciar o banco visualmente
- [x] Testar resiliência: deletar Pods sem perder dados

---

## 🏗️ Arquitetura do Lab

```
┌─────────────────────────────────────────────────────────────┐
│                    Seu Computador (Host)                     │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cluster K8s (kind)                                   │  │
│  │  Namespace: fullstack                                 │  │
│  │                                                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐  │  │
│  │  │ Pod: API   │  │ Pod: API   │  │ Pod: pgAdmin   │  │  │
│  │  │ Flask #1   │  │ Flask #2   │  │                │  │  │
│  │  └─────┬──────┘  └─────┬──────┘  └───────┬────────┘  │  │
│  │        │               │                  │           │  │
│  │  ┌─────▼───────────────▼──────────────────▼────────┐  │  │
│  │  │     Service: postgres (ExternalName)             │  │  │
│  │  │     → resolve para host.docker.internal          │  │  │
│  │  └─────────────────────┬───────────────────────────┘  │  │
│  └────────────────────────│──────────────────────────────┘  │
│                           │                                  │
│                    ┌──────▼───────┐                          │
│                    │ PostgreSQL   │  ← Contêiner Docker      │
│                    │ (externo)    │     FORA do cluster       │
│                    │ porta: 5432  │                           │
│                    └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

> 💡 **Por que este padrão?** Em produção, bancos de dados quase **nunca** rodam dentro do cluster K8s. Eles ficam em serviços gerenciados (AWS RDS, Cloud SQL) ou servidores dedicados. Isso separa o **stateless** (API, que escala facilmente) do **stateful** (banco, que precisa de cuidados especiais com dados).

---

## 🔬 Exercício 1: Subir o PostgreSQL Externo

### Passo 1 — Iniciar o PostgreSQL via Docker (fora do cluster)

```bash
docker run -d \
  --name postgres-externo \
  -e POSTGRES_PASSWORD=senha123 \
  -e POSTGRES_DB=escola \
  -p 5432:5432 \
  postgres:16
```

### Passo 2 — Verificar que está rodando

```bash
docker ps --filter "name=postgres-externo"
# → STATUS: Up X seconds

# Testar conexão diretamente
docker exec -it postgres-externo psql -U postgres -d escola -c "SELECT 1"
# → 1
```

> 🧠 **Observe:** O PostgreSQL está rodando como um contêiner Docker **comum**, fora do cluster K8s. Ele não sabe que o K8s existe. É um servidor de banco de dados independente.

---

## 🔬 Exercício 2: Preparar os Recursos K8s

### Passo 1 — Construir a imagem da API

```bash
cd labs/lab-03-app-fullstack/app

docker build -t api-escola:1.0 .
kind load docker-image api-escola:1.0 --name k8s-lab

cd ../../..
```

### Passo 2 — Criar o Namespace

```bash
kubectl apply -f labs/lab-03-app-fullstack/manifests/namespace.yaml
# → namespace/fullstack created

# Verificar
kubectl get namespaces
# → NAME          STATUS   AGE
# → default       Active   ...
# → fullstack     Active   5s  ← Nosso namespace!
# → kube-system   Active   ...
```

### Passo 3 — Criar o Secret com credenciais

```bash
kubectl apply -f labs/lab-03-app-fullstack/manifests/postgres-secret.yaml
# → secret/postgres-secret created

# Verificar (o conteúdo é Base64, não texto puro)
kubectl get secret postgres-secret -n fullstack -o yaml
```

### Passo 4 — Criar o Service ExternalName

```bash
kubectl apply -f labs/lab-03-app-fullstack/manifests/postgres-external-service.yaml
# → service/postgres created

# Verificar
kubectl get svc -n fullstack
# → NAME       TYPE           CLUSTER-IP   EXTERNAL-IP              PORT(S)   AGE
# → postgres   ExternalName   <none>       host.docker.internal     <none>    5s
```

> 💡 **O que aconteceu?** Criamos um "alias DNS" dentro do cluster. Quando qualquer Pod no namespace `fullstack` acessar o hostname `postgres`, o DNS do K8s resolve para `host.docker.internal`, que é o IP do seu computador — onde o PostgreSQL está rodando!

---

## 🔬 Exercício 3: Deploy da API

### Passo 1 — Aplicar o Deployment e o Service da API

```bash
kubectl apply -f labs/lab-03-app-fullstack/manifests/api-deployment.yaml
kubectl apply -f labs/lab-03-app-fullstack/manifests/api-service.yaml
```

### Passo 2 — Verificar os Pods

```bash
kubectl get pods -n fullstack
# → NAME                         READY   STATUS    RESTARTS   AGE
# → api-escola-xxx-abc12         1/1     Running   0          10s
# → api-escola-xxx-def34         1/1     Running   0          10s
```

### Passo 3 — Testar a API

```bash
# Acessar via NodePort
curl http://localhost:30002 | python3 -m json.tool
# → {
# →   "app": "API Escola — K8s Lab",
# →   "database": "host.docker.internal:5432/escola",
# →   "endpoints": ["/alunos", "/alunos/<id>", "/health"],
# →   ...
# → }

# Health check (verifica conexão com banco)
curl http://localhost:30002/health | python3 -m json.tool
# → {"database": "connected", "status": "healthy"}

# Listar alunos (dados pré-inseridos)
curl http://localhost:30002/alunos | python3 -m json.tool
# → {"alunos": [...], "total": 5}
```

### Passo 4 — Inserir um novo aluno via API

```bash
curl -X POST http://localhost:30002/alunos \
  -H "Content-Type: application/json" \
  -d '{"nome": "Kubernetes Aluno", "email": "k8s@lab.com", "nota": 9.9}'
# → {"id": 6, "nome": "Kubernetes Aluno", "email": "k8s@lab.com", "nota": "9.90"}

# Verificar que foi inserido
curl http://localhost:30002/alunos | python3 -m json.tool
# → total: 6 ← Novo aluno aparece!
```

---

## 🔬 Exercício 4: Deploy do pgAdmin

### Passo 1 — Aplicar o Deployment do pgAdmin

```bash
kubectl apply -f labs/lab-03-app-fullstack/manifests/pgadmin-deployment.yaml
```

### Passo 2 — Aguardar (pgAdmin é pesado, pode demorar)

```bash
kubectl get pods -n fullstack --watch
# Espere até que o Pod do pgAdmin esteja "Running"
```

### Passo 3 — Acessar o pgAdmin

```bash
# Port-forward para acessar no navegador
kubectl port-forward svc/pgadmin -n fullstack 5050:80
# → Forwarding from 127.0.0.1:5050 -> 80
```

Abra: **http://localhost:5050**

- **Email:** admin@lab.com
- **Senha:** admin123

### Passo 4 — Conectar ao PostgreSQL no pgAdmin

1. Clique em **"Add New Server"**
2. Na aba **General**: Nome = `PostgreSQL Externo`
3. Na aba **Connection**:
   - **Host:** `host.docker.internal`
   - **Port:** `5432`
   - **Database:** `escola`
   - **Username:** `postgres`
   - **Password:** `senha123`
4. Clique **Save**

Agora você pode navegar pelas tabelas, ver os dados dos alunos e executar queries SQL diretamente!

---

## 🔬 Exercício 5: Testando Resiliência

### Teste 1 — Deletar Pods da API (dados persistem!)

```bash
# Deletar TODOS os Pods da API
kubectl delete pods -l app=api-escola -n fullstack

# Verificar: K8s recria automaticamente
kubectl get pods -n fullstack --watch

# Testar: os dados do banco estão intactos!
curl http://localhost:30002/alunos | python3 -m json.tool
# → O aluno "Kubernetes Aluno" ainda está lá! 🎉
```

> 🧠 **Por quê?** O banco de dados está **fora** do cluster. Deletar Pods da API não afeta o banco. Os novos Pods reconectam automaticamente.

### Teste 2 — Escalar a API

```bash
# Escalar para 5 réplicas
kubectl scale deployment api-escola --replicas=5 -n fullstack

# Verificar
kubectl get pods -n fullstack -l app=api-escola
# → 5 Pods rodando!

# Testar load balancing
for i in {1..5}; do curl -s http://localhost:30002 | python3 -m json.tool | grep pod; done
# → Hostnames diferentes a cada requisição (balanceamento)

# Voltar para 2 réplicas
kubectl scale deployment api-escola --replicas=2 -n fullstack
```

### Teste 3 — Parar e reiniciar o PostgreSQL

```bash
# Parar o banco externo
docker stop postgres-externo

# Testar a API
curl http://localhost:30002/health
# → {"status": "unhealthy", "error": "..."} ← API detecta a falha!

# Reiniciar o banco
docker start postgres-externo

# Testar novamente
curl http://localhost:30002/health
# → {"status": "healthy", "database": "connected"} ← Reconexão automática!

# Os dados persistiram?
curl http://localhost:30002/alunos | python3 -m json.tool
# → Todos os alunos ainda estão lá (incluindo "Kubernetes Aluno") ✅
```

---

## 🧹 Limpeza

```bash
# Remover TODOS os recursos do namespace fullstack
kubectl delete namespace fullstack
# → Isso remove: Deployment, Service, Secret, Pods — tudo!

# Remover o PostgreSQL externo
docker rm -f postgres-externo

# Verificar
kubectl get all -n fullstack
# → "No resources found" ✅
```

---

## ✅ O que aprendemos

| Conceito | O que fizemos |
|---|---|
| **PostgreSQL externo** | Banco rodando fora do cluster (padrão de produção) |
| **Namespace** | Isolamento lógico de recursos (`fullstack`) |
| **Secret** | Credenciais do banco armazenadas de forma segura |
| **ExternalName Service** | DNS alias dentro do K8s para serviço externo |
| **Separação stateless/stateful** | API escala no K8s, banco fica protegido fora |
| **Resiliência** | Pods morrem e recriam sem perder dados do banco |
| **pgAdmin** | Interface visual para gerenciar o banco de dentro do cluster |

---

**Próximo:** [Lab 04 — Spark on K8s](../lab-04-spark-on-k8s/README.md) →
