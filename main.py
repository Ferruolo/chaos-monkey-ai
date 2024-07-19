from src.behavior_definition import agent_definitions, startnode
from src.state_machines import AgentStateMachine
from src.android_controller import AndroidController


prompt = ("Open an app called 'my sample application', and test how it works with and without wifi")

app_path = "~/gattaca/sample-app/mysampleapplication/app/build/outputs/apk/release/app-release-unsigned.apk"

if __name__ == "__main__":
    android_controller = AndroidController()

    agent = AgentStateMachine(agent_definitions, android=android_controller)
    try:
        agent.run_state_machine(1000, startnode, prompt)
    except Exception as e:
        print(e)
    android_controller.shutdown()




