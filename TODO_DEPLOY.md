# Google Cloud Deployment Guide

This guide walks through deploying AiStagePlayGen to Google Cloud Run.

## Prerequisites

- [ ] Google Cloud account with billing enabled
- [ ] `gcloud` CLI installed and authenticated
- [ ] Docker installed (for local testing)

## Step 1: Setup Google Cloud Project

```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
    run.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com
```

## Step 2: Store OpenAI API Key in Secret Manager

```bash
# Create the secret (you'll be prompted to enter the key)
echo -n "YOUR_OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-

# Or from your .env file
grep OPENAI_API_KEY .env | cut -d'=' -f2 | gcloud secrets create openai-api-key --data-file=-
```

## Step 3: Build and Push Docker Image

**Option A: Using Cloud Build (recommended)**
```bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/aistageplaygen
```

**Option B: Build locally and push**
```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Build
docker build -t gcr.io/$PROJECT_ID/aistageplaygen .

# Push
docker push gcr.io/$PROJECT_ID/aistageplaygen
```

## Step 4: Deploy to Cloud Run

```bash
gcloud run deploy aistageplaygen \
    --image gcr.io/$PROJECT_ID/aistageplaygen \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-secrets=OPENAI_API_KEY=openai-api-key:latest \
    --memory 1Gi \
    --timeout 300
```

After deployment, you'll receive a URL like:
`https://aistageplaygen-xxxxx-uc.a.run.app`

## Step 5: Verify Deployment

```bash
# Get the service URL
gcloud run services describe aistageplaygen --region us-central1 --format='value(status.url)'

# Test it's responding
curl -I $(gcloud run services describe aistageplaygen --region us-central1 --format='value(status.url)')
```

---

## Deployment Checklist

- [ ] Google Cloud project created
- [ ] Required APIs enabled
- [ ] OpenAI API key stored in Secret Manager
- [ ] Docker image built and pushed
- [ ] Cloud Run service deployed
- [ ] Service URL accessible

---

## Updating the Deployment

To deploy updates:

```bash
# Rebuild and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/aistageplaygen

# Redeploy (Cloud Run will use the new image)
gcloud run deploy aistageplaygen \
    --image gcr.io/$PROJECT_ID/aistageplaygen \
    --region us-central1
```

---

## Troubleshooting

### View logs
```bash
gcloud run services logs read aistageplaygen --region us-central1
```

### Check service status
```bash
gcloud run services describe aistageplaygen --region us-central1
```

### Test Secret Manager access
```bash
gcloud secrets versions access latest --secret=openai-api-key
```

---

## Cost Optimization

Cloud Run charges per request and compute time. To minimize costs:

- Set `--min-instances=0` to scale to zero when idle (default)
- Set `--max-instances=1` to limit concurrent instances
- Use `--cpu-throttling` to reduce costs during idle periods

```bash
gcloud run deploy aistageplaygen \
    --image gcr.io/$PROJECT_ID/aistageplaygen \
    --region us-central1 \
    --min-instances=0 \
    --max-instances=3 \
    --set-secrets=OPENAI_API_KEY=openai-api-key:latest
```

---

## Future Improvements

- [ ] Add Cloud SQL for persistent database storage
- [ ] Configure custom domain
- [ ] Set up CI/CD with Cloud Build triggers
- [ ] Add authentication (Cloud IAP or Firebase Auth)
- [ ] Configure monitoring and alerting
