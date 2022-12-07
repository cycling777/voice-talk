import yaml
import os
import aws_cdk as cdk
from constructs import Construct
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep, ManualApprovalStep
from .appication_stage import ApplicationStage

DirName = os.path.dirname(__file__)


class WebsocketPipelineStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get Environment variables for dev stage
        config = self.node.try_get_context("general")

        if config is None:
            raise ValueError(
                f"{self.node.id} - general - {config} is not found in the current context."
            )
        # print("config-type: ", type(config))
        # print("config: ", config)

        # Make pipeline
        pipeline = CodePipeline(
            self, 
            id=f"WebSocketPipeline",
            pipeline_name=f"WebSocketPipeline",
            docker_enabled_for_synth=True,
            synth=ShellStep(
                id="Synth",
                input=CodePipelineSource.connection(
                    repo_string=config["GITHUB_REPOSITORY"],
                    branch=config["GITHUB_BRANCH"],
                    connection_arn=config["CODESTAR_CONNECTION_ARN"]),
                commands=[
                    "npm install -g aws-cdk",
                    'curl -sSL https://install.python-poetry.org | python3 -',
                    'export PATH="/root/.local/bin:${PATH}"',
                    'poetry config virtualenvs.create false',
                    'poetry install',
                    "cdk synth"
                ]
            )
        )

        # Make test stage
        deploy_target = "test"
        dev_stage = pipeline.add_stage(
            ApplicationStage(
                self,
                id=deploy_target,
                deploy_target=deploy_target, 
                env=cdk.Environment(
                    account=config["ACCOUNT"],
                    region=config["REGION"],
                )
            )
        )

        dev_stage.add_post(
            ManualApprovalStep(
                id="TestAsset",
                comment="Test Deploy Stage Worked Correctly",
            )
        )
