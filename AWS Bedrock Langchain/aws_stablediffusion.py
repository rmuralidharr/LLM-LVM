import boto3
import json,base64,os

prompt_data="""
provide me an 4k hd mage of a bench, aslo use a blue sky rainy season adn cimenatic display
"""

prompt_template=[{"text":prompt_data,"weight":1}]
bedrock=boto3.clinet(service_name="bedrock-runtime")
payload={
    "text_prompts":prompt_template,
    "cfg_scale":10,
    "seed":0,
    "steps":50,
    "width":512,
    "height":512

}

body=json.dumps(payload)

model_id="stability.stable-diffusion-xl-v0"
response=bedrock.invoke_model(
    boby=body,
    modelId=model_id,
    contentType= "application/json",
    accept= "application/json"

)

response_body=json.loads(response.get("body").read())
print(response_body)
artifiact=response_body.get("artifacts")[0]
image_encoded=artifiact.get("base64").encode("utf-8")
image_bytes=base64.b64decode(image_encoded)

#save image to a file in output directory
output_dirt="output"
os.makedirs(output_dirt,exist_ok=True)
file_name=f"{output_dirt}/generated-img.png"
with open(file_name,"wb") as f:
    f.write(image_bytes)