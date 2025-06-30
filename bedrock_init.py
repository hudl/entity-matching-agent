"""
Lists the available Amazon Bedrock models.
"""

import logging
import json
import boto3


from botocore.exceptions import ClientError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_foundation_models(bedrock_client):
    """
    Gets a list of available Amazon Bedrock foundation models.

    :return: The list of available bedrock foundation models.
    """

    try:
        response = bedrock_client.list_foundation_models()
        models = response["modelSummaries"]
        logger.info("Got %s foundation models.", len(models))
        return models

    except ClientError:
        logger.error("Couldn't list foundation models.")
        raise


def main():
    """Entry point for the example. Uses the AWS SDK for Python (Boto3)
    to create an Amazon Bedrock client. Then lists the available Bedrock models
    in the region set in the callers profile and credentials.
    """
    session = boto3.Session(profile_name="Engineer_Main_0493")
    bedrock_client = session.client(service_name="bedrock")

    fm_models = list_foundation_models(bedrock_client)
    for model in fm_models:
        print(f"Model: {model['modelName']}")
        print(json.dumps(model, indent=2))
        print("---------------------------\n")

    logger.info("Done.")


#######################################################################################

import boto3
import json

from botocore.exceptions import ClientError

# Create an Amazon Bedrock Runtime client.
session = boto3.Session(profile_name="Engineer_Main_0493")
brt = session.client("bedrock-runtime")

# Set the model ID, e.g., Amazon Titan Text G1 - Express.
model_id = "amazon.titan-text-express-v1"

# Define the prompt for the model.
prompt = "Describe the purpose of a 'hello world' program in one line."

# Format the request payload using the model's native structure.
native_request = {
    "inputText": prompt,
    "textGenerationConfig": {"maxTokenCount": 512, "temperature": 0.5, "topP": 0.9},
}

# Convert the native request to JSON.
request = json.dumps(native_request)

try:
    # Invoke the model with the request.
    response = brt.invoke_model(modelId=model_id, body=request)

except (ClientError, Exception) as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)

# Decode the response body.
model_response = json.loads(response["body"].read())

# Extract and print the response text.
response_text = model_response["results"][0]["outputText"]
print(response_text)

#####################################################################

import boto3
from botocore.exceptions import ClientError

# Create an Amazon Bedrock Runtime client.
session = boto3.Session(profile_name="Engineer_Main_0493")
brt = session.client("bedrock-runtime")

# Set the model ID, e.g., Amazon Titan Text G1 - Express.
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Start a conversation with the user message.
user_message = "Describe the purpose of a 'hello world' program in one line."
conversation = [
    {
        "role": "user",
        "content": [{"text": user_message}],
    }
]

try:
    # Send the message to the model, using a basic inference configuration.
    response = brt.converse(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
    )

    # Extract and print the response text.
    response_text = response["output"]["message"]["content"][0]["text"]
    print(response_text)

except (ClientError, Exception) as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)

##################################################################

from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage

# 1. Instantiate the ChatBedrock class
# By default, it uses the credentials and region from your environment.
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs={"temperature": 0.7},
)

# 2. Prepare your message
# LangChain uses a standardized message format.
messages = [
    HumanMessage(
        content="Hello! Can you explain what a Large Language Model is in one sentence?"
    )
]

# 3. Invoke the model
response = llm.invoke(messages)

# 4. Print the response content
print(response.content)

if __name__ == "__main__":
    main()
