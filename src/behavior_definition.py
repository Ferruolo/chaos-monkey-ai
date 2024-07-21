import pydantic


# TODO: Can we move this whole thing to JSON in the future. I'm gonna be lazy
# TODO: And keep it in python, but this needs to be in JSON

class CallCommand(pydantic.BaseModel):
    agent_name: str
    agent_command: str


master_node_system_prompt = """
You are an Android Quality Assurance expert tasked with
searching for errors in an app that would be encountered through
normal usage. When given an xml output of the current app screen, along with a list 
of your previous movements and their outcome, you will provide the next, and only the next command
"""

command_node_system_prompt = """
You are a natural language interface for an Android phone. You are tasked with
taking an XML output of the current screen of an android phone, along with a command,
and returning a command in the following JSON Format:
{
    command_name: A string containing the commands tap or swipe
    command_inputs: [int] A list of integer coordinates for the respective command. If tap command, pass [x, y], else for swipe pass 
        [x-start y-start x-end y-end duration]
}
Return that command, and only that command, with no additional output.


Here are some tips for completing tasks:
 
Open an App: To Open an app, swipe down
from middle of the screen to 3/4 of the way down the screen to open the applications 
area, then click on the application

Turn off/on wifi: Swipe down on the top of the screen to enter settings area, then click on wifi
button to toggle wifi availability.

Close App: Swipe up from very bottom of the screen
"""

verifier_node_system_prompt = """
You are a natural language verifier for an Android phone command system. 
You are tasked with taking a command, and the current screen of an android phone,
and identifying whether or not the requirements of that command have been satisfied.
You will provide your output as follows:
if Success, return 
    <SUCCESS>
otherwise return
    <FAILURE>
Do not return any other text, explanation or otherwise
"""


def check_output(x: str) -> bool:
    if type(x) != str:
        return False
    else:
        return "<SUCCESS>" in x


startnode = "MasterNode"

# TODO: Fix prompt-formatters
#Todo: maybe make this whole thing pydantic?
agent_definitions = {
    # The master node basically determines the next step
    # for the program given the assignment and the current state
    # and determines the task upon which the other nodes
    # will complete
    'MasterNode': {
        'type': "llm-node",
        'system-prompt': master_node_system_prompt,
        'prompt-formatter': lambda x: lambda y: lambda z: f"Task: {x} | Current Screen: {z[0]}",
        'call-before-execute': [
            CallCommand(agent_name="AndroidNode", agent_command="get-screen"),
            CallCommand(agent_name="CommandParser", agent_command="erase-history"),
        ],
        'pass-success-to': 'CommandParser',
        'pass-fail-to': 'BREAK',  # Initiates Break as Failure
        'use-history': True,
        'output-success': lambda x: True,
    },
    ## This Module takes in a task from the master node and
    # the current state and determines the next
    # command given the task from the master node
    'CommandParser': {
        'type': "llm-node",
        'system-prompt': command_node_system_prompt,
        'prompt-formatter': lambda x: lambda y: lambda z: f"Task: {y} | Current Screen: {z[0]}",
        'call-before-execute': [
            CallCommand(agent_name="AndroidNode", agent_command="get-screen")
        ],
        'pass-success-to': 'AndroidNode',
        'pass-fail-to': 'BREAK',  # Should Never Fail
        'use-history': True,
        'output-success': lambda x: True,
    },
    ##
    # This Module determines whether the current task has been achieved given
    # the current screen output and the initial task from the master node
    # If success, routes to the master node, else routes to the command parser
    'VerifierNode': {
        'type': "llm-node",
        'system-prompt': verifier_node_system_prompt,
        'prompt-formatter': lambda x: lambda y: lambda z: f"Task: {z[1]} | Current Screen: {z[0]} ",
        'call-before-execute': [
            CallCommand(agent_name="AndroidNode", agent_command="get-screen"),
            CallCommand(agent_name="CommandParser", agent_command="get-last-command")
        ],
        'pass-success-to': 'MasterNode',
        'pass-fail-to': 'CommandParser',  # If we haven't reached
        'use-history': False,
        'output-success': check_output,
    },
    # Android Controller, self-explanatory:
    'AndroidNode': {
        'type': "android-node",
        'prompt-formatter': lambda x: lambda y: lambda z: f"{y}",
        'call-before-execute': [],
        'pass-success-to': 'VerifierNode',
        'pass-fail-to': 'CommandParser'  # If we haven't reached
                        ''
    }
}
