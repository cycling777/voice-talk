import yaml
import os

DirName = os.path.join(os.path.dirname(__file__))
deploy_target="dev"
component_path = os.path.join(DirName, f"../../config/component/{deploy_target}")

# yaml_path = os.path.join(DirName, "../../config/component/dev/ws_connection_table.yml")
yaml_path = os.path.join(component_path, "ws_lambda.yml")
with open(yaml_path) as file:
    config = yaml.safe_load(file)
    print(component_path)
    print(yaml_path)
    print(config)