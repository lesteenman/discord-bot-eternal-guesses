#!/usr/bin/env python3
import os

from aws_cdk import Environment, App

from infra.infra_stack import InfraStack


environment = Environment(
    account=os.environ.get("AWS_TARGET_ACCOUNT"),
    region=os.environ.get("AWS_REGION"),
)


app = App()
InfraStack(app, "eternal-guesses", env=environment)

app.synth()
