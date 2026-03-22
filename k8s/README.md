# k8s manifests for sumstock

このディレクトリにはサンプルの Kubernetes マニフェストが含まれています。
Argo CD によりこのディレクトリを監視すると、自動でデプロイされます。

構成:
- k8s/app/* : サンプルアプリ（Deployment + Service）
- k8s/argocd/application.yaml : Argo CD の Application マニフェスト（Argo CD 自体がインストール済みであることが前提）

使い方（概要）:
1. devcontainer を開く (VS Code: "Remote-Containers: Reopen in Container")
2. postStart スクリプトで kind クラスターと Argo CD をセットアップ（自動で実行されます）
3. Argo CD UI をポートフォワード:
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   そして http://localhost:8080 にアクセス
4. Argo CD の Application で `https://github.com/zGVfRcgR/sumstock.git` の `k8s/argocd/application.yaml` を使うか、
   kubectl apply -f k8s/argocd/application.yaml を実行して Argo CD に登録
