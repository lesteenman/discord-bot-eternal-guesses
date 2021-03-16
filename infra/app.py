#!/usr/bin/env python3
import os

from aws_cdk import core

from infra.infra_stack import InfraStack


environment = core.Environment(
    account=os.environ.get("AWS_TARGET_ACCOUNT"),
    region=os.environ.get("AWS_REGION"),
)


app = core.App()
InfraStack(app, "eternal-guesses", env=environment)

app.synth()
