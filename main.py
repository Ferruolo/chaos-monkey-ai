from src.agents import Agent
from src.android_controller import AndroidController

# sys.path.insert(-1,'/home/andrewf/Android/Sdk/platform-tools')
# sys.path.insert(-1,  "/home/andrewf/Android/Sdk/emulator")
#

parsing_agent_role = """AI Parsing Program for Android XML documents. Humans use you to interact with their Androids 
via command line. Given an XML output of the current screen of an android phone, you are tasked with analyzing the 
output and returning a human-readable list of possible actions the human could take with you"""

controller_agent_prompt = """
You are a natural language interface for an Android phone. You are tasked with
taking an XML output of the current screen of an android phone, along with a command,
and return a linux shell command to take that action
"""


controller = AndroidController()

screen = controller.get_screen()

parsing_agent = Agent("Parsing Agent", parsing_agent_role)

print(parsing_agent.act(screen))

# TODO: Controlling Agent`

controller_agent = Agent("Controller Agent", controller_agent_prompt)
print(controller_agent.act(f"Screen: {screen} | Task: Open Chrome from the hotseat"))
# TODO FIX Issue: This selects top left corner of app


