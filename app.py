#!/usr/bin/env python3
import os

import aws_cdk as cdk

from talking3.talking3_stack import Talking3Stack
from talking3.pipeline_stack import PipelineStack


app = cdk.App()
deploy_target="dev" #default deploy target
try:
    deploy_target=app.node.try_get_context("deploy-target")
except AttributeError:
    deploy_target="dev"

PipelineStack(
    app, 
    "PipelineStack", 
    env=cdk.Environment(
        account=app.node.try_get_context(deploy_target)["ACCOUNT"],
        region=app.node.try_get_context(deploy_target)["REGION"],
    )
)

app.synth()
