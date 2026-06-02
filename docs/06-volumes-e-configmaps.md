# 📖 06 — Volumes, ConfigMaps e Secrets

> **Objetivo:** Aprender a persistir dados, externalizar configurações e gerenciar informações sensíveis no Kubernetes. Ao final, você entenderá PVs, PVCs, ConfigMaps e Secrets — os mecanismos que separam dados e configuração do código.

---

## 💾 O Problema: Dados Efêmeros

Assim como no Docker, tudo que é escrito dentro de um contêiner K8s é **efêmero** — quando o Pod morre, os dados morrem juntos:

```bash
# Criar Pod com PostgreSQL
kubectl run pg --image=postgres:16 --env="POSTGRES_PASSWORD=senha"

# Criar dados no banco...

# Deletar o Pod (K8s recria via Deployment)
kubectl delete pod pg

# Novo Pod criado automaticamente — mas sem os dados! 😱
```

Para persistir dados, precisamos de **Volumes**.

---

## 📦 Volumes no Kubernetes vs Docker

| Docker | Kubernetes |
|---|---|
| `docker run -v pgdata:/var/lib/...` | PersistentVolumeClaim (PVC) |
| Volume gerenciado pelo Docker Engine | Volume gerenciado pelo cluster |
| Existe no filesystem do host | Pode ser disco local, NFS, EBS, etc. |
| Simples e direto | Desacoplado: PV → PVC → Pod |

### Arquitetura de Volumes no K8s

```
┌───────────────────────────────────────────────────────────┐
│                                                           │
│  Administrador                    Desenvolvedor           │
│  (provisiona storage)             (solicita storage)      │
│                                                           │
│  ┌──────────────────┐      ┌──────────────────────┐      │
│  │ PersistentVolume │ ◄──► │ PersistentVolumeClaim│      │
│  │      (PV)        │ bind │       (PVC)           │      │
│  │                  │      │                       │      │
│  │ Capacidade: 10Gi │      │ Preciso de: 5Gi      │      │
│  │ Tipo: hostPath   │      │ Acesso: ReadWriteOnce│      │
│  └──────────────────┘      └───────────┬──────────┘      │
│                                         │                 │
│                                    montado em             │
│                                         │                 │
│                                    ┌────▼─────┐          │
│                                    │   Pod    │          │
│                                    │ /data ◄──│── volume │
│                                    └──────────┘          │
└───────────────────────────────────────────────────────────┘
```

---

## 💾 PersistentVolume (PV) e PersistentVolumeClaim (PVC)

### PersistentVolume (PV) — O "disco"

Recurso de armazenamento **provisionado pelo administrador** (ou automaticamente via StorageClass):

```yaml
# pv-local.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-dados
spec:
  capacity:
    storage: 5Gi               # Capacidade total
  accessModes:
    - ReadWriteOnce             # Um Pod pode ler/escrever por vez
  hostPath:
    path: /data/k8s-volumes     # Caminho no nó (apenas para dev/kind)
```

### PersistentVolumeClaim (PVC) — O "pedido"

Solicitação de armazenamento **feita pelo desenvolvedor**:

```yaml
# pvc-dados.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dados-postgres
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi             # "Preciso de pelo menos 2 GiB"
```

### Usando o PVC em um Pod

```yaml
# pod-com-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: postgres
spec:
  containers:
  - name: postgres
    image: postgres:16
    env:
    - name: POSTGRES_PASSWORD
      value: "senha123"
    volumeMounts:
    - name: pg-storage
      mountPath: /var/lib/postgresql/data  # Onde montar o volume
  volumes:
  - name: pg-storage
    persistentVolumeClaim:
      claimName: dados-postgres            # Nome do PVC
```

### Modos de Acesso

| Modo | Abreviação | Descrição |
|---|---|---|
| **ReadWriteOnce** | RWO | Um único nó pode ler/escrever |
| **ReadOnlyMany** | ROX | Múltiplos nós podem ler (somente leitura) |
| **ReadWriteMany** | RWX | Múltiplos nós podem ler/escrever (NFS, Ceph) |

> 💡 **No kind:** Usamos `hostPath` como backend de armazenamento — simples e funcional para aprendizado. Em produção, o backend seria AWS EBS, GCP Persistent Disk ou Ceph.

---

## ⚡ StorageClass: Provisionamento Dinâmico

Em vez de criar PVs manualmente, o **StorageClass** provisiona volumes automaticamente quando um PVC é criado:

```yaml
# O kind já vem com um StorageClass padrão chamado "standard"
# Basta criar o PVC — o PV é criado automaticamente!

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dados-auto
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  # storageClassName: standard   ← Padrão no kind, pode omitir
```

```bash
# Verificar StorageClasses disponíveis
kubectl get storageclass
# → NAME                 PROVISIONER             AGE
# → standard (default)   rancher.io/local-path   1h
```

---

## 📋 ConfigMaps: Configurações Externalizadas

**ConfigMaps** armazenam configurações não-sensíveis fora dos contêineres. Vantagem: altere a configuração **sem reconstruir a imagem Docker**.

### Criando um ConfigMap

```yaml
# configmap-app.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: config-api
data:
  # Pares chave-valor simples
  DATABASE_HOST: "postgres"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "vendas"
  LOG_LEVEL: "INFO"

  # Arquivo de configuração completo
  app.conf: |
    [server]
    host = 0.0.0.0
    port = 8000
    workers = 4
```

### Usando ConfigMap como variáveis de ambiente

```yaml
spec:
  containers:
  - name: api
    image: minha-api:1.0
    envFrom:
    - configMapRef:
        name: config-api        # Todas as chaves viram variáveis de ambiente
```

### Usando ConfigMap como arquivo montado

```yaml
spec:
  containers:
  - name: api
    image: minha-api:1.0
    volumeMounts:
    - name: config-volume
      mountPath: /app/config      # Monta o ConfigMap como diretório
  volumes:
  - name: config-volume
    configMap:
      name: config-api
```

```bash
# Criar ConfigMap via terminal
kubectl create configmap config-api \
  --from-literal=DATABASE_HOST=postgres \
  --from-literal=LOG_LEVEL=INFO

# Criar ConfigMap a partir de um arquivo
kubectl create configmap config-app --from-file=app.conf
```

---

## 🗝️ Secrets: Dados Sensíveis

**Secrets** armazenam dados sensíveis (senhas, tokens, certificados) codificados em Base64:

### Criando um Secret

```yaml
# secret-db.yaml
apiVersion: v1
kind: Secret
metadata:
  name: secret-postgres
type: Opaque
data:
  # Valores codificados em Base64
  # echo -n "senha123" | base64  →  c2VuaGExMjM=
  POSTGRES_PASSWORD: c2VuaGExMjM=
  POSTGRES_USER: cG9zdGdyZXM=
```

### Criando Secret via terminal (mais prático)

```bash
# O kubectl codifica em Base64 automaticamente
kubectl create secret generic secret-postgres \
  --from-literal=POSTGRES_PASSWORD=senha123 \
  --from-literal=POSTGRES_USER=postgres
```

### Usando Secret como variáveis de ambiente

```yaml
spec:
  containers:
  - name: api
    image: minha-api:1.0
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: secret-postgres
          key: POSTGRES_PASSWORD
```

### Usando Secret como volume montado

```yaml
spec:
  containers:
  - name: api
    volumeMounts:
    - name: secret-volume
      mountPath: /app/secrets
      readOnly: true              # Boa prática: somente leitura
  volumes:
  - name: secret-volume
    secret:
      secretName: secret-postgres
```

> ⚠️ **Base64 NÃO é criptografia!** Secrets são codificados em Base64 por padrão, o que é reversível. Em produção, use soluções como **Sealed Secrets**, **Vault** ou **SOPS** para criptografia real. E **nunca versione Secrets no Git!**

---

## 🆚 ConfigMap vs Secret

| Aspecto | ConfigMap | Secret |
|---|---|---|
| **Para que** | Configurações não-sensíveis | Dados sensíveis |
| **Codificação** | Texto puro | Base64 |
| **Exemplos** | URLs, flags, arquivos .conf | Senhas, tokens, chaves SSH |
| **Tamanho máximo** | 1 MiB | 1 MiB |
| **Git** | ✅ Pode versionar | ❌ Nunca versionar |
| **Uso em Pods** | envFrom, volumeMount | env.valueFrom, volumeMount |

---

## 📝 Resumo

| Conceito | Definição |
|---|---|
| **PersistentVolume (PV)** | Recurso de armazenamento provisionado no cluster |
| **PersistentVolumeClaim (PVC)** | Solicitação de armazenamento feita por um Pod |
| **StorageClass** | Provisiona PVs automaticamente quando PVCs são criados |
| **ConfigMap** | Armazena configurações não-sensíveis externalizadas |
| **Secret** | Armazena dados sensíveis codificados em Base64 |
| **hostPath** | Backend de volume usando diretório do nó (apenas dev) |
| **envFrom** | Injeta ConfigMap/Secret como variáveis de ambiente |
| **volumeMount** | Monta ConfigMap/Secret como arquivo no sistema de arquivos |

---

**Próximo:** [07 — kubectl Cheatsheet](07-kubectl-cheatsheet.md) →
