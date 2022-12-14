import aws_cdk as core
import aws_cdk.assertions as assertions

from fails.talking3_stack import Talking3Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in talking3/talking3_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = Talking3Stack(app, "talking3")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
