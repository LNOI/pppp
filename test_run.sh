#!/bin/sh
CI_BUILD_TOKEN=JxCSfsv3GF6demxzgTAq
CI_REGISTRY=registry.gitlab.com
CONTAINER_IMAGE=fashion
TEST_EXPOSE_PORT=8681
TEST_CONTAINER_NAME=sss_server-$TEST_EXPOSE_PORT
EXPOSE_PORT=8680
CONTAINER_NAME=sss_server-$EXPOSE_PORT
BUILD_IMAGE_TAG=late-build
SLEEP_WHEN_START_CONTAINER=10
LOG_FOLDER=/home/thinh/central_log/test_sss

docker login -u gitlab-ci-token -p $CI_BUILD_TOKEN $CI_REGISTRY

docker pull redis:6.0.8
docker build -t $CONTAINER_IMAGE:$BUILD_IMAGE_TAG .

docker stop $TEST_CONTAINER_NAME || true
docker rm $TEST_CONTAINER_NAME || true
docker run -t -d -p $TEST_EXPOSE_PORT:8680/tcp -v $LOG_FOLDER:/ai_server/log --name $TEST_CONTAINER_NAME $CONTAINER_IMAGE:$BUILD_IMAGE_TAG app.py test
sleep $SLEEP_WHEN_START_CONTAINER
docker logs $TEST_CONTAINER_NAME

docker stop test_redis_cache || true
docker rm test_redis_cache || true
docker run -t -d -p 6379:6379/tcp --name test_redis_cache redis:6.0.8
docker network create test-net || true
docker network connect test-net test_redis_cache
docker network connect test-net $TEST_CONTAINER_NAME

docker exec $TEST_CONTAINER_NAME python3 test/integration_test.py
