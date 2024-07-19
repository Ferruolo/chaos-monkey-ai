from src.behavior_definition import agent_definitions, startnode
from src.state_machines import AgentStateMachine
from src.android_controller import AndroidController


prompt = "Simply find a way to break GMAIL using WIFI"



if __name__ == "__main__":
    android_controller = AndroidController()
    agent = AgentStateMachine(agent_definitions, android=android_controller)
    agent.run_state_machine(1000, startnode, prompt)
    android_controller.shutdown()




