# import requests

# def query(payload, model_id, api_token):
#     headers = {"Authorization": f"Bearer {api_token}"}
#     API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
#     response = requests.post(API_URL, headers=headers, json=payload)
#     return response.json()

# model_id = "distilbert-base-uncased"
# api_token = "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" # get yours at hf.co/settings/tokens
# data = query("The goal of life is [MASK].", model_id, api_token)

# print(data[0]['sequence'])

import openai
openai.api_key = "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"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "user", "content": "who is the world's fastest athlete"},
            {"role": "user", "content": "what's the sentiment of this review: the food was not good but the ambience and service was good."},
        ]
)

result = ''
for choice in response.choices:
    result += choice.message.content

print(result)
print(response.choices)

