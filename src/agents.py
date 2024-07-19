from state_machines import Agent
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()


# Basic Claude Agent
class ClaudeAgent(Agent):
    def __init__(self, agent_id, system_prompt):
        super().__init__(agent_id)
        self.prompt_input = None
        self.system_prompt = system_prompt
        self.client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])
        self.prompt_formatter = lambda x: lambda y: f"COMMAND: {x} \n\n DATA: {y}"

    def run(self, command, data):
        self.prompt_input = self.prompt_formatter(command)(data)
        prompt = f"{self.system_prompt} {anthropic.HUMAN_PROMPT}  {anthropic.AI_PROMPT}"

        response = self.client.completions.create(
            model="claude-2",
            prompt=prompt,
            max_tokens_to_sample=300,
            stop_sequences=[anthropic.HUMAN_PROMPT]
        )

        return response


class AndroidAgent(Agent):
    def __init__(self, agent_id, android):
        super().__init__(agent_id)
        self.android = android


    def run(self, command, data):
        if data != "":
            return

        try:
            _, data = self.android.parse(command)
        except Exception as e:
            return e.__str__()


