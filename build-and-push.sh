docker buildx build \
  --platform=linux/amd64,linux/386,linux/arm64/v8,linux/arm/v7,linux/arm/v5 \
  --pull \
  --push \
  -t rabbitaaron/paperless-smtp:latest .
