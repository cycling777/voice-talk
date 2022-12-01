from aws_cdk.aws_lambda import Runtime, Architecture

# CDK Configs
RUNTIMES={
    "python3.6": Runtime.PYTHON_3_6,
    "python3.7": Runtime.PYTHON_3_7,
    "python3.8": Runtime.PYTHON_3_8,
    "python3.9": Runtime.PYTHON_3_9,
}
LAMBDA_ARCHITECTURE={
    "x86": Architecture.X86_64,
    "arm64": Architecture.ARM_64,
}