import os
import anthropic


class AnthropicInterface:
    def __init__(self, model_name="claude-3-sonnet-20240229", api_key=None):
        if api_key is None:
            api_key = os.environ["CLAUDE_API_KEY"]
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model_name
        self.max_tokens = 1024

    def call_api(self, prompt: str):
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            # tools=[
            #     {
            #         "name": "",
            #         "description": "Get the current weather in a given location",
            #         "input_schema": {
            #             "type": "object",
            #             "properties": {
            #                 "location": {
            #                     "type": "string",
            #                     "description": "The city and state, e.g. San Francisco, CA",
            #                 }
            #             },
            #             "required": ["location"],
            #         },
            #     }
            # ],
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
