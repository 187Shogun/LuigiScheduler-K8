## Luigi Scheduler Deployment for K8
This project builds a docker image with luigi installed plus
some additional configuration files to avoid repetition. The
K8 deployment file deploys the scheduler and exposes the luigi
dashboard in a K8 service. 
The K8 pod running the scheduler runs on a Docker image with GCP
components as base and it is configured to earn the rights of a 
given service account if you bind the K8 and IAM service accounts.

### Instructions: 

1. Run `gcloud init` and authenticate into a GCP cloud account.
2. Create a service account and a K8 cluster in GCP. 
3. Run `run-deployment.ps1` to authenticate into the K8 server, bind a service account and deploy assets. 