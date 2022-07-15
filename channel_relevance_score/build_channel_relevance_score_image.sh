#docker image name
IMAGE_REPO_NAME=channel_relevance_score
IMAGE_TAG=1.0.0
IMAGE_URI=footprintsforretailapp.azurecr.io/$IMAGE_REPO_NAME:$IMAGE_TAG

#Build Image
echo "Building image: "$IMAGE_URI
docker build -f ./crs_serving/Dockerfile -t $IMAGE_URI ./
echo "Finished building image: "$IMAGE_URI

echo "Pushing image: "$IMAGE_URI
docker push "$IMAGE_URI"
echo "Finished pushing image: "$IMAGE_URI