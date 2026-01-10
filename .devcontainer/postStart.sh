#!/bin/bash
set -euo pipefail

# This script runs inside the devcontainer after the container starts.
# It will:
#  - create a kind cluster named "dev" (if not exists)
#  - install Argo CD into the cluster
#  - print Argo CD initial admin password and instructions to port-forward

KIND_CLUSTER_NAME="dev"
ARGOCD_NAMESPACE="argocd"
KUBECTL="$(command -v kubectl || true)"
KIND="$(command -v kind || true)"
ARGOCD_MANIFEST_URL="https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"

if [ -z "${KIND}" ]; then
  echo "kind not installed in container. Please install kind."
  exit 1
fi

if [ -z "${KUBECTL}" ]; then
  echo "kubectl not installed in container. Please install kubectl."
  exit 1
fi

# Create kind cluster if absent
if ! kind get clusters | grep -q "^${KIND_CLUSTER_NAME}$"; then
  echo "Creating kind cluster '${KIND_CLUSTER_NAME}'..."
  kind create cluster --name "${KIND_CLUSTER_NAME}"
else
  echo "kind cluster '${KIND_CLUSTER_NAME}' already exists."
fi

# Ensure kubectl can see the cluster
echo "KUBECONFIG: $(kubectl config current-context)"

# Install Argo CD
if ! kubectl get ns "${ARGOCD_NAMESPACE}" >/dev/null 2>&1; then
  echo "Installing Argo CD into namespace ${ARGOCD_NAMESPACE}..."
  kubectl create namespace "${ARGOCD_NAMESPACE}"
  kubectl apply -n "${ARGOCD_NAMESPACE}" -f "${ARGOCD_MANIFEST_URL}"
  echo "Argo CD manifests applied. Waiting until argocd-server is ready..."
  kubectl -n "${ARGOCD_NAMESPACE}" wait --for=condition=available deployment/argocd-server --timeout=180s || true
else
  echo "Namespace ${ARGOCD_NAMESPACE} already exists; assuming Argo CD may already be installed."
fi

# Show initial admin password
echo
echo "----- Argo CD initial admin password -----"
kubectl -n "${ARGOCD_NAMESPACE}" get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" 2>/dev/null | base64 --decode || echo "(not found in secret)"
echo
echo "To access Argo CD UI, run:"
echo "  kubectl port-forward svc/argocd-server -n ${ARGOCD_NAMESPACE} 8080:443"
echo "Then open http://localhost:8080 (username: admin, password: above)"
echo
echo "You can also use the argocd CLI to login:"
echo "  argocd login localhost:8080 --insecure --username admin --password <password>"
