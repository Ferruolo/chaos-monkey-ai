from src.behavior_definition import agent_definitions, startnode
from src.state_machines import AgentStateMachine
from src.android_controller import AndroidController


prompt = ("Test how gmail behaves when we launch the app on the device without internet connection as well as what "
          "happens when connection is back online.")

app_path = "~/gattaca/sample-app/mysampleapplication/app/build/outputs/apk/release/app-release-unsigned.apk"

if __name__ == "__main__":
    android_controller = AndroidController()

    agent = AgentStateMachine(agent_definitions, android=android_controller)
    try:
        agent.run_state_machine(1000, startnode, prompt)
    except Exception as e:
        print(e)
    android_controller.shutdown()




