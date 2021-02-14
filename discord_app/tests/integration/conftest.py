import docker
import pytest


# @pytest.fixture(scope="session", autouse=True)
# def start_dynamodb_container():
#     docker_client = docker.from_env()
#     dynamodb_container = docker_client.containers.run('amazon/dynamodb-local', ports={8000: 8000}, detach=True,
#                                                       auto_remove=True)
#
#     yield
#
#     dynamodb_container.stop()
