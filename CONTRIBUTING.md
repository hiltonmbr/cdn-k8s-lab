# Contributing to K8s Lab

First off, thank you for considering contributing to this educational project! 🎉

## How to Contribute

- 🐛 **Report bugs** — Open an issue describing the problem, steps to reproduce, and expected behavior.
- 💡 **Suggest improvements** — Open an issue with the "enhancement" label.
- 📖 **Fix docs** — Typos, unclear explanations, and missing details are always welcome.
- 🧪 **Improve labs** — Add new exercises, fix broken steps, or enhance existing ones.
- 🔧 **Submit code** — Bug fixes, new features, or refactoring via pull requests.

## Pull Request Process

1. **Fork** the repository and create your branch from `main`.
2. **Run existing labs** to ensure your changes don't break anything.
3. **Update documentation** if your change affects usage or setup.
4. **Keep commits atomic** — one logical change per commit.
5. **Write clear commit messages** following conventional commits style (e.g., `feat: add new lab for ingress`, `fix: correct typo in docs`).
6. **Open a pull request** against the `main` branch with a clear description of what you changed and why.

## Development Setup

```bash
# 1. Clone your fork
git clone https://github.com/YOUR-USERNAME/cdn-k8s-lab.git
cd cdn-k8s-lab

# 2. Install prerequisites
# macOS:
brew install kind kubectl

# Linux:
# kind: https://kind.sigs.k8s.io/docs/user/quick-start/
# kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/

# 3. Create the cluster
kind create cluster --name k8s-lab --config kind-config.yaml

# 4. Verify it works
kubectl get nodes
```

## Code of Conduct

This project follows a **Code of Conduct** that expects all contributors to create a welcoming and inclusive environment. Harassment and disrespectful behavior will not be tolerated.

By participating, you are expected to uphold this code. Please report unacceptable behavior to the repository maintainers.

## Reporting Issues

When reporting issues, please include:

- 📋 **Description** — What happened vs. what you expected.
- 🖥️ **Environment** — OS, Docker version, kind version, kubectl version.
- 📝 **Steps to reproduce** — Minimal, reproducible steps.
- 📎 **Logs** — Relevant terminal output or error messages.

## Style Guide

- **YAML** — Use 2-space indentation, descriptive resource names, and comments where helpful.
- **Python** — Follow PEP 8, use type hints where appropriate, keep functions focused.
- **Markdown** — Use ATX headings, fenced code blocks with language tags, and relative links.

## Questions?

If you have questions, open a discussion or ask in the issues. We're here to help! 🙌
