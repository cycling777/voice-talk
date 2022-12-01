#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.pipeline.test_pipeline_stack import TestPipelineStack
from stacks.pipeline.websocket_pipeline_stack import WebsocketPipelineStack


app = cdk.App()

try:
    deploy_target=app.node.try_get_context("deploy-target")
except AttributeError:
    deploy_target="dev"

TestPipelineStack(
    app, 
    construct_id="PipelineStack", 
    env=cdk.Environment(
        account=app.node.try_get_context(deploy_target)["ACCOUNT"],
        region=app.node.try_get_context(deploy_target)["REGION"],
    )
)

# WebsocketPipelineStack(
#     app, 
#     construct_id="WebSocketPipelineStack", 
#     env=cdk.Environment(
#         account=app.node.try_get_context(deploy_target)["ACCOUNT"],
#         region=app.node.try_get_context(deploy_target)["REGION"],
#     )
# )


app.synth()
