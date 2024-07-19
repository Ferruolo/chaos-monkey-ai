from typing import List

import pydantic

from behavior_definition import CallCommand


class AgentOutput(pydantic.BaseModel):
    success: bool = True
    agent_id: str
    output: str


# This is just a definition to mock up agent behavior and the
# Agent type and should definitely never ever be used for any real functionality
class Agent:
    def __init__(self, agent_id: str, prompt_formatter, fetch_commands: dict, call_before_execute: List[CallCommand],
                 pass_success_to: str, pass_failure_to: str) -> None:
        self.agent_id = agent_id
        self.call_before_execute = call_before_execute
        self.prompt_formatter = prompt_formatter
        self.fetch_commands = fetch_commands
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


class AgentStateMachine:
    def __init__(self, definitions):
        self.agents = {}  # TODO: Implement Me

    def run_state_machine(self, max_turns: int, start_node: str, task_definition: str):
        current_node = self.agents[start_node]
        previous_output = ""

        for i in range(max_turns):
            fetched_data = [self.agents[cmd.agent_name].fetch_cmd(cmd.agent_command) for cmd in
                            current_node.call_before_execute]

            prompt = current_node.format_prompt(fetched_data, previous_output, fetched_data)
            output: AgentOutput = current_node.run(prompt)
            previous_output = output.output
            if output.success:
                current_node = self.agents[current_node.pass_success_to]
            else:
                current_node = self.agents[current_node.pass_failure_to]

            if current_node == "BREAK":
                break
