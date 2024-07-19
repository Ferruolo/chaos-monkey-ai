import os
from android_controller import AndroidController
import anthropic
from dotenv import load_dotenv

from state_machines import Agent, AgentOutput

load_dotenv()

"""
Goal:
We are going to export most of the control code to the state machine router,
rather than include it in the agent coding. This way we can minimize the amount of
code written
"""


# Basic Claude Agent
# TODO: Add history for chain-of-thought prompting
class ClaudeAgent(Agent):
    def __init__(self, *args, system_prompt, model="claude-2"):
        super().__init__(*args)
        self.system_prompt = system_prompt
        self.client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])
        self.model = model
        self.last_command = ""

    def run(self, command: str) -> AgentOutput:
        self.last_command = command
        prompt = f"{self.system_prompt} {anthropic.HUMAN_PROMPT} {command}  {anthropic.AI_PROMPT}"

        response = self.client.completions.create(model=self.model, prompt=prompt, max_tokens_to_sample=300,
                                                  stop_sequences=[anthropic.HUMAN_PROMPT])

        return AgentOutput(success=True, agent_id=self.agent_id, output=response)

    def fetch_cmd(self, cmd: str) -> str:
        if cmd == "get-last-command":
            return self.last_command
        else:
            return ""


class AndroidAgent(Agent):
    def __init__(self, *args, android: AndroidController):
        super().__init__(*args)
        self.android: AndroidController = android

    def run(self, command):
        try:
            _, data = self.android.parse(command)
            return AgentOutput(success=True, agent_id=self.agent_id, output=data)
        except Exception as e:
            return AgentOutput(success=False, agent_id=self.agent_id, output=e.__str__())

    def fetch_cmd(self, cmd: str) -> str:
        if cmd == "get-screen":
            return self.android.get_screen()
