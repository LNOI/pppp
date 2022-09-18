# chmod +x ./run.sh

EXPOSE_PORT=6310 \
    CONTAINER_IMAGE=ai-psp \
    BUILD_IMAGE_TAG=latest \
    IMAGE_NAME=sss_ai_psp \
    CONTAINER_NAME=sss_ai_psp-$EXPOSE_PORT \
    docker-compose down --remove-orphans

EXPOSE_PORT=6310 \
    CONTAINER_IMAGE=ai-psp \
    BUILD_IMAGE_TAG=latest \
    IMAGE_NAME=sss_ai_psp \
    CONTAINER_NAME=sss_ai_psp-$EXPOSE_PORT \
    docker-compose build --force-rm

EXPOSE_PORT=6310 \
    CONTAINER_IMAGE=ai-psp \
    BUILD_IMAGE_TAG=latest \
    IMAGE_NAME=sss_ai_psp \
    CONTAINER_NAME=sss_ai_psp-$EXPOSE_PORT \
    docker-compose up -d #--remove-orphans ai-psp:latest
