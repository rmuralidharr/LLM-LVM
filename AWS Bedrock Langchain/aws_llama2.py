import boto3
import json
##llama2 model meta from aws

prompt_data="""
Act as Shakespeare and write a poem on machine learning
"""
bedrock=boto3.client(service_name="Bedrock-runtime")

payload={
    "prompt":"[INST]"+prompt_data+"[/INST]",
    "max_gen_len":512,
    "temperature":0.5,
    "top_p":0.9

}
body=json.dumps(payload)
model_id="meta.llama2-70b-chat-v1"
response=bedrock.invoke_model(
    body=body,
    modelId=model_id,
    accept="application/json",
    contentType= "application/json",

)
response_body=json.load(response.get('body').read())
response_text=response_body['generation']
print(response_text)