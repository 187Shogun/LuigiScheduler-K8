#Define parameters:
$PROJECT_ID="alchemialabs-dev-001"
$K8_SA="gke-worker-sa"
$IAM_SA="aldah-worker-dev"
$CLUSTER_NAME="autopilot-cluster-1"
$NAMESPACE="default"
$REGION="us-central1"

# Authenticate into the K8 cluster:
echo "Authenticating into K8 cluster..."
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION --project $PROJECT_ID

# Create a K8 service account and bind it to a GCPservice account:
echo "Binding service accounts..."
kubectl create serviceaccount $K8_SA --namespace $NAMESPACE
gcloud iam service-accounts add-iam-policy-binding $IAM_SA@$PROJECT_ID.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:$PROJECT_ID.svc.id.goog[default/$K8_SA]"
kubectl annotate serviceaccount $K8_SA --namespace $NAMESPACE iam.gke.io/gcp-service-account=$IAM_SA@$PROJECT_ID.iam.gserviceaccount.com

# Deploy assets to K8 cluster:
echo "Deploying assets..."
kubectl apply -f pvc.yaml
kubectl apply -f deployment.yaml
echo "Deployment successful!"