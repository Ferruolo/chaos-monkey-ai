import pydantic


class AgentOutput(pydantic.BaseModel):
    success: bool = True
    agent_id: int
    output: str


class Agent:
    def __init__(self, agent_id):
        self.internal_state = ""
        self.agent_id = agent_id

    def run(self, command, data) -> AgentOutput:
        # Creates Infinite Loop, basically just a demo
        # I haven't written a real application in python in months
        return AgentOutput(success=True, agent_id=self.agent_id, output="")


class AgentStateMachine:
    def __init__(self, agents, initial_state: AgentOutput):
        self.agents = agents
        self.initial_state: AgentOutput = initial_state

    def run_state_machine(self, max_turns):

        (agent, command, data) = self.initial_state
        print("Initial State:")
        print(f"Agent {agent} executes command {command}")

        for i in max_turns:
            (agent, command, data) = self.agents[agent].run(command, data)
            print(f"{i}: Agent {agent} executes command {command}")
            if command == "BREAK":
                break
        return True
