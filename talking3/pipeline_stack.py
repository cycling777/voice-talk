import aws_cdk as cdk
from constructs import Construct
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from .lambda_stack import LambdaStack


class PipelineStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        pipeline = CodePipeline(
            self, "Pipeline",
            pipeline_name="MyPipeline",
            synth=ShellStep(
                "Synth",
                input=CodePipelineSource.connection(
                    "IPI-k-watanabe/talking3",
                    "main",
                    connection_arn="arn:aws:codestar-connections:us-east-1:958152586967:connection/c5c2b5da-4b6a-4c74-937f-6a73532c0b0a",),
                commands=[
                    "npm install -g aws-cdk",
                    "python -m pip install -r requirements.txt",
                    "cdk synth"]
            )
        )

        pipeline.add_stage(
            LambdaApplicationStage(
                self,
                "Prod",
                env=cdk.Environment(
                    account="958152586967",
                    region="us-east-1",
                )
            )
        )

class LambdaApplicationStage(cdk.Stage):
    def __init__(self, scope, id, *, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)
    
        LambdaStack(self, "TestLambda")
    