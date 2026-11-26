kind create cluster --name platform-lab
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add argo https://argoproj.github.io/argo-helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx --namespace ingress-nginx --create-namespace --wait
helm upgrade --install argocd argo/argo-cd --namespace argocd --create-namespace --wait
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace --set grafana.adminPassword=admin --wait
kubectl apply -f argocd/project.yaml
kubectl apply -f argocd/root-app.yaml
