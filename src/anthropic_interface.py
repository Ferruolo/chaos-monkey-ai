import os
import requests


class AnthropicInterface:
    def __init__(self, model_name="claude-3-sonnet-20240229", api_key=None):
        if api_key is None:
            api_key = os.environ["CLAUDE_API_KEY"]
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
        self.model = model_name
        self.url = "https://api.anthropic.com/v1/messages"

    def call_api(self, prompt: str):
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(self.url, json=data, headers=self.headers)

        if response.status_code == 200:
            response_data = response.json()
            return response_data['content'][0]['text']
        else:
            raise Exception(f"API call failed with status code {response.status_code}: {response.text}")
