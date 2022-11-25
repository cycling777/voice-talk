#!/usr/bin/env python3
import os

import aws_cdk as cdk

from talking3.talking3_stack import Talking3Stack
from talking3.pipeline_stack import PipelineStack


app = cdk.App()
PipelineStack(app, "PipelineStack", 
    env=cdk.Environment(account=958152586967, region="us-east-1")
)

app.synth()
