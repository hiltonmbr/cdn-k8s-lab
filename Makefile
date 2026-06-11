# ☸️ K8s Lab Makefile
# Targets for managing the Kubernetes lab environment

.PHONY: help setup cluster-create cluster-delete cluster-info \
        lab-01 lab-02 lab-03 lab-04 lab-05 \
        clean docker-build docker-load lint all

CLUSTER_NAME ?= k8s-lab
KIND_CONFIG ?= kind-config.yaml
NAMESPACE_LAB02 ?= default
NAMESPACE_LAB03 ?= fullstack
NAMESPACE_LAB04 ?= spark

help:
	@echo "🌟 Welcome to the K8s Lab Makefile!"
	@echo ""
	@echo "Available targets:"
	@echo "  help            📖 Show this help message"
	@echo "  setup           🔧 Install dependencies and create cluster"
	@echo "  cluster-create  🏗️  Create kind cluster"
	@echo "  cluster-delete  🗑️  Delete kind cluster"
	@echo "  cluster-info    ℹ️  Show cluster info"
	@echo "  lab-01          🧪 Run Lab 01 — Hello K8s"
	@echo "  lab-02          🧪 Run Lab 02 — Deployments"
	@echo "  lab-03          🧪 Run Lab 03 — Fullstack App"
	@echo "  lab-04          🧪 Run Lab 04 — Spark on K8s"
	@echo "  lab-05          🧪 Run Lab 05 — Dashboard & Monitoring"
	@echo "  clean           🧹 Clean all lab resources"
	@echo "  docker-build    🐳 Build all Docker images"
	@echo "  docker-load     📦 Load Docker images into kind"
	@echo "  lint            ✅ Check YAML syntax"
	@echo "  all             🚀 Setup + build + load + cluster"
	@echo ""
	@echo "Variables:"
	@echo "  CLUSTER_NAME=$${CLUSTER_NAME}  (default: k8s-lab)"

setup: cluster-create
	@echo "✅ Setup complete! Cluster '$(CLUSTER_NAME)' is ready."

cluster-create:
	@echo "🏗️  Creating kind cluster '$(CLUSTER_NAME)'..."
	@if kind get clusters | grep -q "^$(CLUSTER_NAME)$$"; then \
		echo "✅ Cluster '$(CLUSTER_NAME)' already exists."; \
	else \
		kind create cluster --name $(CLUSTER_NAME) --config $(KIND_CONFIG); \
	fi

cluster-delete:
	@echo "🗑️  Deleting kind cluster '$(CLUSTER_NAME)'..."
	@kind delete cluster --name $(CLUSTER_NAME) 2>/dev/null || echo "Cluster '$(CLUSTER_NAME)' not found."
	@echo "✨ Cluster deleted."

cluster-info:
	@echo "ℹ️  Cluster info for '$(CLUSTER_NAME)':"
	@kubectl cluster-info 2>/dev/null || echo "Cluster not running."
	@echo ""
	@echo "📋 Nodes:"
	@kubectl get nodes 2>/dev/null || true

lab-01:
	@echo "🧪 Running Lab 01 — Hello K8s"
	@echo "📖 Follow the guide: labs/lab-01-hello-k8s/README.md"
	@echo ""
	@echo "Quick commands:"
	@echo "  kubectl run nginx --image=nginx:latest --port=80"
	@echo "  kubectl port-forward pod/nginx 8080:80"

lab-02:
	@echo "🧪 Running Lab 02 — Deployments"
	@echo "⏳ Applying manifests..."
	@if ! kind get clusters | grep -q "^$(CLUSTER_NAME)$$"; then \
		echo "❌ Cluster '$(CLUSTER_NAME)' not running. Run 'make cluster-create' first."; \
		exit 1; \
	fi
	kubectl apply -f labs/lab-02-deployments/manifests/
	@echo "✅ Lab 02 applied! Access API at http://localhost:30001"

lab-03:
	@echo "🧪 Running Lab 03 — Fullstack App"
	@if ! kind get clusters | grep -q "^$(CLUSTER_NAME)$$"; then \
		echo "❌ Cluster '$(CLUSTER_NAME)' not running. Run 'make cluster-create' first."; \
		exit 1; \
	fi
	@echo "⏳ Creating namespace and applying manifests..."
	kubectl apply -f labs/lab-03-fullstack-app/manifests/
	@echo "✅ Lab 03 applied! Access API at http://localhost:30002"

lab-04:
	@echo "🧪 Running Lab 04 — Spark on K8s"
	@if ! kind get clusters | grep -q "^$(CLUSTER_NAME)$$"; then \
		echo "❌ Cluster '$(CLUSTER_NAME)' not running. Run 'make cluster-create' first."; \
		exit 1; \
	fi
	@echo "⏳ Applying Spark manifests..."
	kubectl apply -f labs/lab-04-spark-on-k8s/manifests/
	@echo "✅ Lab 04 applied! Access Spark UI at http://localhost:4040"

lab-05:
	@echo "🧪 Running Lab 05 — Dashboard & Monitoring"
	@if ! kind get clusters | grep -q "^$(CLUSTER_NAME)$$"; then \
		echo "❌ Cluster '$(CLUSTER_NAME)' not running. Run 'make cluster-create' first."; \
		exit 1; \
	fi
	@echo "⏳ Applying Dashboard manifests..."
	kubectl apply -f labs/lab-05-dashboard-and-monitoring/manifests/
	@echo "✅ Lab 05 applied! Run 'kubectl proxy' to access the dashboard."

clean:
	@echo "🧹 Cleaning up lab resources..."
	@for ns in $(NAMESPACE_LAB03) $(NAMESPACE_LAB04); do \
		if kubectl get namespace $$ns >/dev/null 2>&1; then \
			echo "  Deleting namespace: $$ns"; \
			kubectl delete namespace $$ns --ignore-not-found >/dev/null 2>&1; \
		fi; \
	done
	@echo "  Deleting lab-02 resources..."
	@kubectl delete -f labs/lab-02-deployments/manifests/ --ignore-not-found >/dev/null 2>&1 || true
	@echo "🧹 Clean complete!"

docker-build:
	@echo "🐳 Building Docker images..."
	@echo "  Building api-sales:1.0..."
	@docker build -t api-sales:1.0 labs/lab-02-deployments/app/ > /dev/null && echo "    ✅ api-sales:1.0 built"
	@echo "  Building api-school:1.0..."
	@docker build -t api-school:1.0 labs/lab-03-fullstack-app/app/ > /dev/null && echo "    ✅ api-school:1.0 built"
	@echo "🐳 All images built!"

docker-load:
	@echo "📦 Loading Docker images into kind cluster '$(CLUSTER_NAME)'..."
	@if ! kind get clusters | grep -q "^$(CLUSTER_NAME)$$"; then \
		echo "❌ Cluster '$(CLUSTER_NAME)' not running. Run 'make cluster-create' first."; \
		exit 1; \
	fi
	@echo "  Loading api-sales:1.0..."
	@kind load docker-image api-sales:1.0 --name $(CLUSTER_NAME) > /dev/null && echo "    ✅ Loaded api-sales:1.0"
	@echo "  Loading api-school:1.0..."
	@kind load docker-image api-school:1.0 --name $(CLUSTER_NAME) > /dev/null && echo "    ✅ Loaded api-school:1.0"
	@echo "📦 All images loaded!"

lint:
	@echo "✅ Checking YAML syntax..."
	@find labs -name "*.yaml" -exec sh -c 'echo "  Checking: $$1"; python3 -c "import yaml; yaml.safe_load(open(\"$$1\"))" && echo "    ✅ Valid" || echo "    ❌ Invalid"' _ {} \;
	@echo "✅ Lint complete!"

all: setup docker-build docker-load
	@echo "🚀 All done! Cluster is running with images loaded."
