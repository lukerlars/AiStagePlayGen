"""A Google Cloud Python Pulumi program for StagePlayGen Streamlit App"""

import pulumi
import pulumi_docker as docker
from pulumi_gcp import storage, artifactregistry, cloudrunv2, secretmanager, serviceaccount

config = pulumi.Config()
gcp_config = pulumi.Config("gcp")
project = gcp_config.require("project")
region = config.get("region") or "europe-north1"
app_name = "stageplaygen"

# -----------------------------------------------------------------------------
# Artifact Registry - Container image storage
# -----------------------------------------------------------------------------
registry = artifactregistry.Repository(
    f"{app_name}-registry",
    repository_id=f"{app_name}-repo",
    location=region,
    format="DOCKER",
    description="Container registry for StagePlayGen Streamlit app",
)

# Build the registry URL
registry_url = pulumi.Output.concat(
    region, "-docker.pkg.dev/", project, "/", registry.repository_id
)

# -----------------------------------------------------------------------------
# Docker Image - Build and push to Artifact Registry
# -----------------------------------------------------------------------------
image = docker.Image(
    f"{app_name}-image",
    image_name=pulumi.Output.concat(registry_url, "/", app_name, ":latest"),
    build=docker.DockerBuildArgs(
        context="..",  # Parent directory where Dockerfile is located
        dockerfile="../Dockerfile",
        platform="linux/amd64",  # Cloud Run requires linux/amd64
    ),
    registry=docker.RegistryArgs(
        server=pulumi.Output.concat(region, "-docker.pkg.dev"),
    ),
    opts=pulumi.ResourceOptions(depends_on=[registry]),
)

# -----------------------------------------------------------------------------
# Secret Manager - Store OpenAI API key
# -----------------------------------------------------------------------------
openai_secret = secretmanager.Secret(
    "openai-api-key",
    secret_id="openai-api-key",
    replication=secretmanager.SecretReplicationArgs(
        auto=secretmanager.SecretReplicationAutoArgs(),
    ),
)

# Note: You'll need to add a secret version manually or via CLI:
# gcloud secrets versions add openai-api-key --data-file=- <<< "your-api-key"

# -----------------------------------------------------------------------------
# Cloud Run Service Account
# -----------------------------------------------------------------------------
# Create a dedicated service account for Cloud Run
cloudrun_sa = serviceaccount.Account(
    f"{app_name}-sa",
    account_id=f"{app_name}-runner",
    display_name="StagePlayGen Cloud Run Service Account",
)

# Grant the service account access to Secret Manager
secret_accessor = secretmanager.SecretIamMember(
    "cloudrun-secret-accessor",
    secret_id=openai_secret.secret_id,
    role="roles/secretmanager.secretAccessor",
    member=pulumi.Output.concat("serviceAccount:", cloudrun_sa.email),
)

# -----------------------------------------------------------------------------
# Cloud Run Service
# -----------------------------------------------------------------------------
cloud_run_service = cloudrunv2.Service(
    f"{app_name}-service",
    name=app_name,
    location=region,
    template=cloudrunv2.ServiceTemplateArgs(
        containers=[
            cloudrunv2.ServiceTemplateContainerArgs(
                # Use the image built and pushed by the Docker provider
                image=image.repo_digest,
                ports=cloudrunv2.ServiceTemplateContainerPortsArgs(container_port=8080),
                resources=cloudrunv2.ServiceTemplateContainerResourcesArgs(
                    limits={"memory": "512Mi", "cpu": "1"},
                ),
                envs=[
                    cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="GOOGLE_CLOUD_PROJECT",
                        value=project,
                    ),
                ],
            )
        ],
        scaling=cloudrunv2.ServiceTemplateScalingArgs(
            min_instance_count=0,
            max_instance_count=2,
        ),
        service_account=cloudrun_sa.email,
    ),
    opts=pulumi.ResourceOptions(depends_on=[image, secret_accessor]),
)

# -----------------------------------------------------------------------------
# IAM - Allow unauthenticated access (public web app)
# -----------------------------------------------------------------------------
public_access = cloudrunv2.ServiceIamMember(
    f"{app_name}-public-access",
    name=cloud_run_service.name,
    location=region,
    role="roles/run.invoker",
    member="allUsers",
)

# -----------------------------------------------------------------------------
# Storage Bucket - For any persistent storage needs
# -----------------------------------------------------------------------------
bucket = storage.Bucket(
    f"{app_name}-bucket",
    name=pulumi.Output.concat(project, "-", app_name, "-storage"),
    location="EU",
    uniform_bucket_level_access=True,
)

# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------
pulumi.export("registry_url", registry_url)
pulumi.export("image_name", image.repo_digest)
pulumi.export("service_url", cloud_run_service.uri)
pulumi.export("bucket_name", bucket.url)
