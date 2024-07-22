from src.agents import AndroidAgent, ClaudeAgent, AgentOutput
from src.android_controller import AndroidController


class AgentStateMachine:
    def __init__(self, definitions, android: AndroidController) -> None:
        self.agents = {}
        for name, definition in definitions.items():
            # TODO: Simplify in future, DRYY
            if definition['type'] == 'llm-node':
                self.agents[name] = ClaudeAgent(name, definition['prompt-formatter'], definition['call-before-execute'],
                                                definition['pass-success-to'], definition['pass-fail-to'],
                                                system_prompt=definition['system-prompt'],
                                                use_history=definition['use-history'],
                                                output_success=definition['output-success']
                                                )
            elif definition['type'] == 'android-node':
                self.agents[name] = AndroidAgent(name, definition['prompt-formatter'],
                                                 definition['call-before-execute'], definition['pass-success-to'],
                                                 definition['pass-fail-to'], android=android)

    def run_state_machine(self, max_turns: int, start_node: str, task_definition: str):
        current_node = self.agents[start_node]
        previous_output = ""

        for i in range(max_turns):
            fetched_data = [self.agents[cmd.agent_name].fetch_cmd(cmd.agent_command) for cmd in
                            current_node.call_before_execute]

            prompt = current_node.format_prompt(task_definition, previous_output, fetched_data)
            output: AgentOutput = current_node.run(prompt)
            print(f"{current_node.agent_id} -> {output.success}: {output.output}")
            previous_output = output.output
            if output.success:
                current_node = self.agents[current_node.pass_success_to]
            else:
                current_node = self.agents[current_node.pass_failure_to]

            if current_node == "BREAK":
                break
