# k8s manifests

This folder contains Kubernetes manifests for deploying the vulnerable Flask app used in this demo.

How to deploy locally with `kind`:

1. Build the Docker image locally (from repository root):

```powershell
docker build -t security-pipeline-demo-webapp:latest .
```

2. Load the image into the `kind` cluster (replace cluster name if different):

```powershell
C:\Users\mateo\.local\bin\kind.exe load docker-image security-pipeline-demo-webapp:latest --name argocd-demo
```

3. Apply manifests:

```powershell
C:\Users\mateo\.local\bin\kubectl.exe apply -f k8s/deployment.yaml
C:\Users\mateo\.local\bin\kubectl.exe apply -f k8s/service.yaml
```

4. Verify:

```powershell
C:\Users\mateo\.local\bin\kubectl.exe get deployments,svc
```

To view the app locally you can port-forward the service:

```powershell
C:\Users\mateo\.local\bin\kubectl.exe port-forward svc/vulnerable-webapp-svc 5000:5000
# then open http://localhost:5000
```
