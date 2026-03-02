#!/usr/bin/env bash
# setup.sh — Provision the full GCP environment for the Governance Agent
# Usage: bash setup.sh
# Fill in the variables below before running.

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION — edit these before running
# ─────────────────────────────────────────────────────────────────────────────
PROJECT_ID=""                             # GCP project ID
REGION="us-central1"
SERVICE_NAME="governance-agent"
REPO_NAME="governance-agent"             # Artifact Registry repository name
SA_NAME="governance-agent-sa"            # Cloud Run service account name
RULES_BUCKET="governance-rules-${PROJECT_ID}"
GITHUB_PAT=""                            # GitHub Personal Access Token
GITHUB_REPO=""                           # e.g. "org/repo"
BASE_BRANCH="main"
# ─────────────────────────────────────────────────────────────────────────────

# ── Helpers ──────────────────────────────────────────────────────────────────
banner() { echo; echo "══════════════════════════════════════════════════════"; echo "  $*"; echo "══════════════════════════════════════════════════════"; }

# ── 1. Validate inputs ────────────────────────────────────────────────────────
banner "1/10  Validating inputs"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "ERROR: PROJECT_ID is not set. Edit setup.sh and set PROJECT_ID."
  exit 1
fi

if [[ -z "${GITHUB_PAT}" ]]; then
  echo "ERROR: GITHUB_PAT is not set. Edit setup.sh and set GITHUB_PAT."
  exit 1
fi

echo "Project:  ${PROJECT_ID}"
echo "Region:   ${REGION}"
echo "Service:  ${SERVICE_NAME}"
echo "Bucket:   ${RULES_BUCKET}"

# Resolve project number (needed for Cloud Build SA)
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:latest"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Project number: ${PROJECT_NUMBER}"
echo "Cloud Build SA: ${CLOUDBUILD_SA}"

# ── 2. Enable GCP APIs ────────────────────────────────────────────────────────
banner "2/10  Enabling GCP APIs"

gcloud services enable \
  cloudrun.googleapis.com \
  cloudbuild.googleapis.com \
  storage.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  aiplatform.googleapis.com \
  iam.googleapis.com \
  --project="${PROJECT_ID}"

echo "APIs enabled."

# ── 3. Create Artifact Registry repository ────────────────────────────────────
banner "3/10  Creating Artifact Registry repository"

if gcloud artifacts repositories describe "${REPO_NAME}" \
    --location="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
  echo "Repository '${REPO_NAME}' already exists — skipping."
else
  gcloud artifacts repositories create "${REPO_NAME}" \
    --repository-format=docker \
    --location="${REGION}" \
    --project="${PROJECT_ID}" \
    --description="Docker images for ${SERVICE_NAME}"
  echo "Repository '${REPO_NAME}' created."
fi

# ── 4. Create service account for Cloud Run ───────────────────────────────────
banner "4/10  Creating Cloud Run service account"

if gcloud iam service-accounts describe "${SA_EMAIL}" \
    --project="${PROJECT_ID}" &>/dev/null; then
  echo "Service account '${SA_EMAIL}' already exists — skipping creation."
else
  gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="Governance Agent — Cloud Run SA" \
    --project="${PROJECT_ID}"
  echo "Service account created."
fi

# Grant Vertex AI / Gemini access
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/aiplatform.user" \
  --condition=None

# Fallback role for Gemini API
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/ml.developer" \
  --condition=None

echo "IAM roles granted to service account."

# ── 5. Create GCS bucket and upload rules ─────────────────────────────────────
banner "5/10  Creating GCS bucket and uploading rules"

if gcloud storage buckets describe "gs://${RULES_BUCKET}" \
    --project="${PROJECT_ID}" &>/dev/null; then
  echo "Bucket 'gs://${RULES_BUCKET}' already exists — skipping creation."
else
  gcloud storage buckets create "gs://${RULES_BUCKET}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}"
  echo "Bucket created."
fi

echo "Uploading rules..."
gcloud storage cp rules/governance/*  "gs://${RULES_BUCKET}/governance/"
gcloud storage cp rules/security/*    "gs://${RULES_BUCKET}/security/"
gcloud storage cp rules/code-quality/* "gs://${RULES_BUCKET}/code-quality/"
echo "Rules uploaded."

# Grant the Cloud Run SA read access to the bucket
gcloud storage buckets add-iam-policy-binding "gs://${RULES_BUCKET}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.objectViewer"
echo "objectViewer granted on bucket."

# ── 6. Store GitHub PAT in Secret Manager ────────────────────────────────────
banner "6/10  Storing GitHub PAT in Secret Manager"

if gcloud secrets describe github-pat --project="${PROJECT_ID}" &>/dev/null; then
  echo "Secret 'github-pat' already exists — adding a new version."
  echo -n "${GITHUB_PAT}" | gcloud secrets versions add github-pat \
    --data-file=- \
    --project="${PROJECT_ID}"
else
  echo -n "${GITHUB_PAT}" | gcloud secrets create github-pat \
    --data-file=- \
    --project="${PROJECT_ID}"
  echo "Secret 'github-pat' created."
fi

# Grant Cloud Build SA access to the secret
gcloud secrets add-iam-policy-binding github-pat \
  --project="${PROJECT_ID}" \
  --member="serviceAccount:${CLOUDBUILD_SA}" \
  --role="roles/secretmanager.secretAccessor"
echo "secretAccessor granted to Cloud Build SA."

# ── 7. Build and push Docker image ────────────────────────────────────────────
banner "7/10  Building and pushing Docker image"

gcloud builds submit . \
  --tag="${IMAGE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}"

echo "Image pushed: ${IMAGE}"

# ── 8. Deploy to Cloud Run ────────────────────────────────────────────────────
banner "8/10  Deploying to Cloud Run"

gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE}" \
  --platform=managed \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --service-account="${SA_EMAIL}" \
  --set-env-vars="RULES_BUCKET=${RULES_BUCKET},GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION}" \
  --allow-unauthenticated \
  --memory=1Gi \
  --timeout=120 \
  --min-instances=0

CLOUD_RUN_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --format="value(status.url)")

echo "Cloud Run URL: ${CLOUD_RUN_URL}"

# ── 9. Grant Cloud Build SA permission to invoke Cloud Run ────────────────────
banner "9/10  Granting Cloud Build SA run.invoker on Cloud Run"

gcloud run services add-iam-policy-binding "${SERVICE_NAME}" \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --member="serviceAccount:${CLOUDBUILD_SA}" \
  --role="roles/run.invoker"

echo "run.invoker granted to Cloud Build SA."

# ── 10. Summary ───────────────────────────────────────────────────────────────
banner "10/10  Done!"

echo
echo "Cloud Run URL : ${CLOUD_RUN_URL}"
echo "Rules bucket  : gs://${RULES_BUCKET}"
echo "Docker image  : ${IMAGE}"
echo "Service account: ${SA_EMAIL}"
echo
echo "─────────────────────────────────────────────────────────────────────────"
echo "  NEXT STEP: Create the Cloud Build trigger manually"
echo "─────────────────────────────────────────────────────────────────────────"
echo
echo "  1. Open the Cloud Build Triggers console:"
echo "     https://console.cloud.google.com/cloud-build/triggers?project=${PROJECT_ID}"
echo
echo "  2. Click 'Connect Repository', select GitHub, and authorize GCP."
echo "     Select your repository: ${GITHUB_REPO}"
echo
echo "  3. Click 'Create Trigger' and fill in:"
echo "     - Event:         Pull Request"
echo "     - Source:        ${GITHUB_REPO}, branch ^${BASE_BRANCH}\$"
echo "     - Configuration: Cloud Build configuration file → cloudbuild.yaml"
echo "     - Substitutions:"
echo "         _AGENT_URL   = ${CLOUD_RUN_URL}"
echo "         _GITHUB_REPO = ${GITHUB_REPO}"
echo "         _BASE_BRANCH = ${BASE_BRANCH}"
echo
echo "  4. Save the trigger. Every new PR will trigger a governance review."
echo
echo "  For more information:"
echo "  https://cloud.google.com/build/docs/automating-builds/github/connect-repo-github"
echo
