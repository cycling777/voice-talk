#!/usr/bin/env python3
import aws_cdk as cdk

from pipeline.pipeline_stack import WebsocketPipelineStack


app = cdk.App()

WebsocketPipelineStack(
    app,
    construct_id="WebSocketPipelineStack",
    env=cdk.Environment(
        account=app.node.try_get_context("general")["ACCOUNT"],
        region=app.node.try_get_context("general")["REGION"],
    )
)

app.synth()
