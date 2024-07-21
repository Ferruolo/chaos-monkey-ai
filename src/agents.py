import os
from typing import List

import anthropic
import pydantic
from dotenv import load_dotenv

from src.android_controller import AndroidController
from src.behavior_definition import CallCommand
from src.anthropic_interface import AnthropicInterface
load_dotenv()

"""
Goal:
We are going to export most of the control code to the state machine router,
rather than include it in the agent coding. This way we can
keep life simple
"""


class AgentOutput(pydantic.BaseModel):
    success: bool = True
    agent_id: str
    output: str


# This is just a definition to mock up agent behavior and the
# Agent type and should definitely never ever be used for any real functionality
class Agent:
    def __init__(self, agent_id: str, prompt_formatter, call_before_execute: List[CallCommand], pass_success_to: str,
                 pass_failure_to: str) -> None:
        self.agent_id = agent_id
        self.call_before_execute = call_before_execute
        self.prompt_formatter = prompt_formatter
        # self.fetch_commands = fetch_commands
        self.pass_success_to = pass_success_to
        self.pass_failure_to = pass_failure_to

    def run(self, command: str) -> AgentOutput:
        # Creates Infinite Loop, basically just a demo
        # I haven't written a real application in python in months
        return AgentOutput(success=True, agent_id=self.agent_id, output="")

    def format_prompt(self, initial_prompt: str, previous_output: str, fetched_items: List[str]) -> str:
        return self.prompt_formatter(initial_prompt)(previous_output)(fetched_items)

    def fetch_cmd(self, cmd: str) -> str:
        return cmd


# Basic Claude Agent
# TODO: Add history for chain-of-thought prompting
# No longer uses anthropic agent because
class ClaudeAgent(Agent):
    def __init__(self, *args, system_prompt, use_history=False, output_success=lambda x: True,
                 model_name="claude-3-sonnet-20240229"):
        super().__init__(*args)
        self.system_prompt = system_prompt
        self.claude = AnthropicInterface(model_name=model_name)
        self.model_name = model_name
        self.last_command = ""
        self.history = []
        self.use_history = use_history
        self.len_recent_history = 5
        self.output_success = output_success

    def run(self, command: str) -> AgentOutput:
        self.last_command = command

        history = ""

        if len(self.history) > 0:
            recent_history = self.history[-self.len_recent_history:] if len(
                self.history) > self.len_recent_history else self.history
            history = "History:\n" + '\n'.join(recent_history)

        prompt = f"{self.system_prompt}\n{anthropic.HUMAN_PROMPT}\n{command}\n{history}\n{anthropic.AI_PROMPT}"
        print(prompt)

        response = self.claude.call_api(prompt)

        if self.use_history:
            self.history.append(f"```{anthropic.HUMAN_PROMPT} {command} {anthropic.AI_PROMPT} {response.completion}```")

        output_text = response.completion

        return AgentOutput(success=self.output_success(output_text), agent_id=self.agent_id, output=output_text)

    def fetch_cmd(self, cmd: str) -> str:
        if cmd == "get-last-command":
            return self.last_command
        elif cmd == "erase-history":
            self.history = []
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
