# 📖 07 — kubectl Cheatsheet

> **Referência rápida** de todos os comandos essenciais do `kubectl`, organizados por categoria. Mantenha esta página aberta enquanto trabalha nos Labs!

---

## 🔧 Cluster e Contexto

```bash
# Informações do cluster
kubectl cluster-info

# Listar contextos (clusters) configurados
kubectl config get-contexts

# Ver contexto ativo
kubectl config current-context

# Trocar de contexto
kubectl config use-context kind-k8s-lab

# Ver todos os nós do cluster
kubectl get nodes
kubectl get nodes -o wide          # Com IPs e versão do kernel
```

---

## 🫛 Pods

```bash
# ── Listar ──
kubectl get pods                            # Namespace atual
kubectl get pods -A                         # Todos os namespaces
kubectl get pods -o wide                    # Com IPs e nós
kubectl get pods -l app=nginx               # Filtrar por label
kubectl get pods --watch                    # Monitorar em tempo real
kubectl get pods --sort-by='.status.startTime'  # Ordenar por data

# ── Criar (imperativo — para testes rápidos) ──
kubectl run nginx --image=nginx:1.27 --port=80
kubectl run pg --image=postgres:16 --env="POSTGRES_PASSWORD=senha"

# ── Detalhes ──
kubectl describe pod <nome>                 # Eventos, status, volumes
kubectl get pod <nome> -o yaml              # YAML completo do recurso

# ── Logs ──
kubectl logs <nome>                         # Logs do contêiner
kubectl logs <nome> -f                      # Seguir logs (tail -f)
kubectl logs <nome> --previous              # Logs do contêiner anterior (crash)
kubectl logs <nome> -c <container>          # Logs de contêiner específico (multi-container)
kubectl logs -l app=nginx --all-containers  # Logs de todos os Pods com label

# ── Executar comandos ──
kubectl exec -it <nome> -- bash             # Shell interativo
kubectl exec -it <nome> -- sh               # Se bash não existe (Alpine)
kubectl exec <nome> -- cat /etc/hostname    # Comando único

# ── Port-forward ──
kubectl port-forward pod/<nome> 8080:80     # Acessar Pod localmente
kubectl port-forward svc/<nome> 8080:80     # Acessar via Service

# ── Deletar ──
kubectl delete pod <nome>                   # Deletar Pod específico
kubectl delete pods --all                   # ⚠️ Deletar todos os Pods do namespace
kubectl delete pod <nome> --force --grace-period=0  # Forçar remoção imediata
```

---

## 🚀 Deployments

```bash
# ── Criar / Atualizar ──
kubectl apply -f deployment.yaml
kubectl create deployment nginx --image=nginx:1.27 --replicas=3  # Imperativo

# ── Listar ──
kubectl get deployments
kubectl get deploy                          # Atalho

# ── Escalar ──
kubectl scale deployment <nome> --replicas=5
kubectl autoscale deployment <nome> --min=2 --max=10 --cpu-percent=50

# ── Atualizar imagem ──
kubectl set image deployment/<nome> container=imagem:nova-tag
kubectl rollout restart deployment <nome>   # Reiniciar todos os Pods

# ── Rollout ──
kubectl rollout status deployment <nome>    # Status da atualização
kubectl rollout history deployment <nome>   # Histórico de revisões
kubectl rollout undo deployment <nome>      # Rollback (versão anterior)
kubectl rollout undo deployment <nome> --to-revision=2  # Rollback específico

# ── Deletar ──
kubectl delete deployment <nome>
```

---

## 🌐 Services

```bash
# ── Criar ──
kubectl apply -f service.yaml
kubectl expose deployment <nome> --port=80 --target-port=8000 --type=NodePort

# ── Listar ──
kubectl get services
kubectl get svc                             # Atalho

# ── Detalhes ──
kubectl describe svc <nome>

# ── Deletar ──
kubectl delete svc <nome>
```

---

## 📋 ConfigMaps e Secrets

```bash
# ── ConfigMaps ──
kubectl create configmap <nome> --from-literal=KEY=value
kubectl create configmap <nome> --from-file=config.yaml
kubectl get configmaps
kubectl describe configmap <nome>
kubectl get configmap <nome> -o yaml        # Ver conteúdo

# ── Secrets ──
kubectl create secret generic <nome> --from-literal=PASSWORD=senha123
kubectl get secrets
kubectl describe secret <nome>
kubectl get secret <nome> -o yaml           # Ver conteúdo (Base64)

# Decodificar Secret
kubectl get secret <nome> -o jsonpath='{.data.PASSWORD}' | base64 -d
```

---

## 💾 Volumes (PV / PVC)

```bash
kubectl get pv                              # PersistentVolumes
kubectl get pvc                             # PersistentVolumeClaims
kubectl describe pvc <nome>                 # Detalhes e status de binding
kubectl get storageclass                    # StorageClasses disponíveis
```

---

## 📁 Namespaces

```bash
# ── Listar ──
kubectl get namespaces
kubectl get ns                              # Atalho

# ── Criar ──
kubectl create namespace meu-ns

# ── Usar ──
kubectl get pods -n meu-ns                  # Listar Pods de um namespace
kubectl apply -f arquivo.yaml -n meu-ns     # Aplicar em namespace específico

# ── Mudar namespace padrão ──
kubectl config set-context --current --namespace=meu-ns
```

---

## 📄 Aplicar e Deletar Recursos

```bash
# ── Aplicar YAML ──
kubectl apply -f arquivo.yaml               # Criar ou atualizar
kubectl apply -f manifests/                 # Aplicar todos os YAMLs de um diretório
kubectl apply -f https://url/recurso.yaml   # Aplicar de uma URL

# ── Deletar ──
kubectl delete -f arquivo.yaml              # Deletar recurso definido no YAML
kubectl delete -f manifests/                # Deletar tudo do diretório
kubectl delete all --all -n <namespace>     # ⚠️ Deletar TUDO em um namespace

# ── Dry-run (testar sem aplicar) ──
kubectl apply -f arquivo.yaml --dry-run=client   # Validar localmente
kubectl apply -f arquivo.yaml --dry-run=server   # Validar no servidor
```

---

## 🔍 Debug e Troubleshooting

```bash
# ── Eventos do cluster ──
kubectl get events --sort-by='.lastTimestamp'
kubectl get events -A                       # Todos os namespaces

# ── Investigar Pod com problema ──
kubectl describe pod <nome>                 # Seção "Events" é a chave
kubectl logs <nome>                         # Ver stdout/stderr
kubectl logs <nome> --previous              # Logs do crash anterior

# ── Status rápido ──
kubectl get all                             # Tudo no namespace atual
kubectl get all -A                          # Tudo em todos os namespaces

# ── Recursos do nó ──
kubectl top nodes                           # CPU e memória dos nós
kubectl top pods                            # CPU e memória dos Pods
# (requer Metrics Server instalado)

# ── Testar conectividade de dentro do cluster ──
kubectl run debug --image=busybox -it --rm -- wget -qO- http://api-vendas:80
kubectl run debug --image=busybox -it --rm -- nslookup api-vendas
```

---

## ⌨️ Aliases Úteis

Adicione ao seu `~/.bashrc` ou `~/.zshrc` para produtividade:

```bash
# Atalhos para kubectl
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployments'
alias kga='kubectl get all'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias kdp='kubectl describe pod'
alias kl='kubectl logs'
alias klf='kubectl logs -f'
alias kei='kubectl exec -it'
alias kns='kubectl config set-context --current --namespace'

# Exemplo de uso:
# kgp           → kubectl get pods
# kaf app.yaml  → kubectl apply -f app.yaml
# klf meu-pod   → kubectl logs -f meu-pod
# kns prod      → trocar para namespace "prod"
```

---

## 📝 Gerar YAMLs Automaticamente

```bash
# Gerar YAML de Pod sem criar
kubectl run nginx --image=nginx:1.27 --port=80 \
  --dry-run=client -o yaml > pod.yaml

# Gerar YAML de Deployment sem criar
kubectl create deployment nginx --image=nginx:1.27 --replicas=3 \
  --dry-run=client -o yaml > deployment.yaml

# Gerar YAML de Service sem criar
kubectl expose deployment nginx --port=80 --type=NodePort \
  --dry-run=client -o yaml > service.yaml
```

> 💡 **Dica:** `--dry-run=client -o yaml` é o seu melhor amigo para criar templates YAML rapidamente sem decorar a estrutura completa.

---

**← Voltar ao** [README.md](../README.md)
