import yaml
import os
import aws_cdk as cdk
from constructs import Construct
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep, ManualApprovalStep
from .structures.ws_application_stack import WebSocketApplicationStack

DirName = os.path.dirname(__file__)


class WebsocketPipelineStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get Environment variables for dev stage
        config = self.node.try_get_context("general")
        dev_config = self.node.try_get_context("dev")
        prod_config = self.node.try_get_context("prod")

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
                    "python -m pip install -r requirements.txt",
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

class ApplicationStage(cdk.Stage):
    def __init__(self, scope, id, *, deploy_target: str, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)

        # component_dir_name = os.path.join(
        #     DirName, f"../../config/{deploy_target}/components")
        component_dir_name = f"config/{deploy_target}/components"

        # call structure stack
        ws_stack = WebSocketApplicationStack(
            self,
            id=f"ws-stack-{deploy_target}",
            deploy_target=deploy_target,
            components_dir_name=component_dir_name,
        )
