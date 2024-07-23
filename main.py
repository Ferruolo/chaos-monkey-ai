from src.behavior_definition import agent_definitions, startnode
from src.state_machines import AgentStateMachine
from src.android_controller import AndroidController

output_path = "summary.txt"

prompt = "Open an app called 'my sample application', and test how it works with and without wifi"

app_path = ("/Users/andrewferruolo/chaos-monkey-ai/sample-app/mysampleapplication/app/build/outputs/apk/release/app"
            "-release-unsigned.apk")

if __name__ == "__main__":
    android_controller = AndroidController(device_name='Pixel_8_API_35')

    agent = AgentStateMachine(agent_definitions, android=android_controller)
    # android_controller.push_app(app_path, "my-sample-application.apk")
    output = None
    try:
        output = agent.run_state_machine(1000, startnode, prompt)
    except Exception as e:
        print(e)
    if output is not None:
        print("Writing Summary!")
        with open(output_path, 'w') as f:
            f.write(output)
    android_controller.shutdown()



