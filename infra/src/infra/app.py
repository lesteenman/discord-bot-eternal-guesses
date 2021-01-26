#!/usr/bin/env python3

from aws_cdk import core

from infra_stack import InfraStack


app = core.App()
InfraStack(app, "eternal-guesses")

app.synth()
