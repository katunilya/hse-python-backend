

compose_run:
    docker compose up -d

docker_stop:
    docker stop $(docker ps -q)
    docker rm -f $(docker ps -aq)
    docker logs
    docker rmi $(docker images -q)
