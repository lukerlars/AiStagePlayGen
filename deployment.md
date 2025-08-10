
# Notes and stuff


# info for me: 
project id:
pure-display-467912-d3

# Deployment of docker image

### Build the image to amd64 platform (am on m3 mac)
docker build --platform linux/amd64 -t my_app -f Dockerfile .

### Authenticate docker with google cloud
gcloud auth configure-docker europe-north1-docker.pkg.dev

### Tag image
docker tag my_app europe-north1-docker.pkg.dev/pure-display-467912-d3/playwriter-ar-repo/my_app

### Push image
docker push europe-north1-docker.pkg.dev/pure-display-467912-d3/playwriter-ar-repo/my_app

### Deploy 
gcloud run deploy my-app \
  --image europe-north1-docker.pkg.dev/pure-display-467912-d3/playwriter-ar-repo/my_app \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated