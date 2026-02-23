# Instructions

## Build and Publish the Image
- Use the `image_build` directory for your Docker build context.
- Create a CI/CD pipeline (GitHub Actions, GitLab CI, etc.) that builds the Docker image and pushes it to AWS ECR.
- Tag the image appropriately (e.g., `submission`, `v1.0.0`).

## Deploy to Kubernetes
- Use the Helm chart in the `deploy/` directory to deploy the application.
- Deploy with a GitOps tool like ArgoCD, referencing the provided values file.
- This setup assumes a single environment for demo purposes; overlays for prod/non-prod are not included.

## What’s Deployed
- **Helm chart** with:
  - Horizontal Pod Autoscaler (HPA)
  - ExternalSecret (for API key, assumes External Secrets Operator is running)
  - Deployment (with autoscaling, runs container from ECR)
  - Service (type: LoadBalancer)
  - ServiceAccount (with IRSA annotation)

## Notes
- I didn’t have time to add cert-manager, AWS Load Balancer Controller, or external-dns.
- The service type is set to LoadBalancer for simplicity.
- ExternalSecret template is included, assuming the operator is running and secret store exists and is functioning properly.

---

If you have questions or want to see overlays for multiple environments, let me know!
