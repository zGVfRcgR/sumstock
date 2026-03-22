# Devcontainer base image (Ubuntu LTS)
FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-22.04

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000
ENV DEBIAN_FRONTEND=noninteractive

# Install common tools, kubectl, kind, helm, argocd CLI
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates curl git sudo gnupg lsb-release jq conntrack iproute2 iptables \
  && \
  # kubectl (stable)
  KUBECTL_VERSION=$(curl -s https://dl.k8s.io/release/stable.txt) \
  && curl -Lo /tmp/kubectl "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
  && install -o root -g root -m 0755 /tmp/kubectl /usr/local/bin/kubectl \
  && rm -f /tmp/kubectl \
  && \
  # kind
  curl -Lo /usr/local/bin/kind "https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64" \
  && chmod +x /usr/local/bin/kind \
  && \
  # helm
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash \
  && \
  # argocd CLI
  curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64 \
  && chmod +x /usr/local/bin/argocd \
  && \
  # cleanup
  apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy helper script (postStart)
COPY postStart.sh /usr/local/local-poststart/postStart.sh
RUN chmod +x /usr/local/local-poststart/postStart.sh

# Provide workspace dir
RUN mkdir -p /workspace
WORKDIR /workspace

# If using non-root vscode user exists in base image
USER ${USERNAME}
