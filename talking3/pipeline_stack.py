import aws_cdk as cdk
from constructs import Construct
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from .lambda_stack import LambdaStack


class PipelineStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get Environment variables
        deploy_target="dev" #default deploy target
        try:
            deploy_target=self.node.try_get_context("deploy-target")
        except AttributeError:
            deploy_target="dev"

        account=self.node.try_get_context(deploy_target)["ACCOUNT"]
        region=self.node.try_get_context(deploy_target)["REGION"]
        repo_string = self.node.try_get_context(deploy_target)["GITHUB_REPOSITORY"]
        branch = self.node.try_get_context(deploy_target)["GITHUB_BRANCH"]
        connection_arn = self.node.try_get_context(deploy_target)["CODESTAR_CONNECTION_ARN"]

        # Make pipeline
        pipeline = CodePipeline(
            self, "Pipeline",
            pipeline_name="MyPipeline",
            synth=ShellStep(
                "Synth",
                input=CodePipelineSource.connection(
                    repo_string=repo_string,
                    branch=branch,
                    connection_arn=connection_arn),
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
                    account=account,
                    region=region,
                )
            )
        )

class LambdaApplicationStage(cdk.Stage):
    def __init__(self, scope, id, *, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)
    
        LambdaStack(self, "TestLambda")
    