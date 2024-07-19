import os

import anthropic
from dotenv import load_dotenv

from state_machines import Agent, AgentOutput

load_dotenv()

"""
Goal:
We are going to export most of the control code to the state machine router,
rather than include it in the agent coding. This way we can 

"""


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

        response = self.client.completions.create(model="claude-2", prompt=prompt, max_tokens_to_sample=300,
                                                  stop_sequences=[anthropic.HUMAN_PROMPT])

        return AgentOutput(success=True, agent_id=self.agent_id, output=response)


class AndroidAgent(Agent):
    def __init__(self, agent_id, android):
        super().__init__(agent_id)
        self.android = android

    def run(self, command, data):
        if data != "":
            return

        try:
            _, data = self.android.parse(command)
            return AgentOutput(success=True, agent_id=self.agent_id, output=data)
        except Exception as e:
            return AgentOutput(success=False, agent_id=self.agent_id, output=e.__str__())
