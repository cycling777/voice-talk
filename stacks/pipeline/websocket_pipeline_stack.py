import yaml
import os
import aws_cdk as cdk
from constructs import Construct
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep, ManualApprovalStep
from ..structure.ws_application_stack import WebSocketApplicationStack

DirName = os.path.dirname(__file__)


class WebsocketPipelineStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get Environment variables
        deploy_target = self.node.try_get_context("deploy-target")
        config = self.node.try_get_context(deploy_target)

        if config is None:
            raise ValueError(
                f"{self.node.id} - {deploy_target} - {config} is not found in the current context."
            )
        # print("config-type: ", type(config))
        # print("config: ", config)

        # Make pipeline
        pipeline = CodePipeline(
            self, 
            id=f"WebSocketPipeline-{deploy_target}",
            pipeline_name=f"WebSocketPipeline-{deploy_target}",
            synth=ShellStep(
                id="Synth",
                input=CodePipelineSource.connection(
                    repo_string=config["GITHUB_REPOSITORY"],
                    branch=config["GITHUB_BRANCH"],
                    connection_arn=config["CODESTAR_CONNECTION_ARN"]),
                commands=[
                    "npm install -g aws-cdk",
                    "python -m pip install -r requirements.txt",
                    "python -m pip install docker",
                    "systemctl start docker",
                    "cdk synth"]
            )
        )

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
                id="DevAsset",
                comment="Dev Deploy Stage Worked Correctly",
            )
        )

class ApplicationStage(cdk.Stage):
    def __init__(self, scope, id, *, deploy_target: str, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)

        component_dir_name = os.path.join(
            DirName, f"../../config/component/{deploy_target}")

        # call structure stack
        ws_stack = WebSocketApplicationStack(
            self,
            id=f"ws-stack-{deploy_target}",
            deploy_target=deploy_target,
            component_dir_name=component_dir_name,
        )
