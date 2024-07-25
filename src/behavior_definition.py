import pydantic


# TODO: Can we move this whole thing to JSON in the future. I'm gonna be lazy
# TODO: And keep it in python, but this needs to be in JSON

class CallCommand(pydantic.BaseModel):
    agent_name: str
    agent_command: str

# TODO: Fully swipe out of app
# TODO: Write basic report on app


master_node_system_prompt = """
You are an Android Quality Assurance expert tasked with
searching for errors in an app that would be encountered through
normal usage. You will be given a mission, along with the current XML output of
an android screen, and will determine the output using this
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
Return that command, and only that command, with no additional output. You can select a command from
the following list of commands:
tap
swipe
shutdown
enable-wifi
disable-wifi
get-screen
do-nothing
close-app

Remember that each command must contain both the command_name and command_inputs columns, otherwise the output will be 
invalid. For commands that don't need command_inputs, consider just passing [0, 0]
"""


verifier_node_system_prompt = """
You are a natural language verifier for an Android phone command system.
You are tasked with accepting a command and the current screen of an android phone,
and identifying whether or not the requirements of that command have been satisfied.
If you are accidentally passed a list of commands, you will identify a success if some, but not necessarily all
of the requirements have been met
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
        'type': "manual-node",
        'system-prompt': master_node_system_prompt,
        'prompt-formatter': lambda x: lambda y: lambda z: f"{z[0]}",
        'call-before-execute': [
            CallCommand(agent_name="AndroidNode", agent_command="get-screen"),
            CallCommand(agent_name="CommandParser", agent_command="erase-history"),
        ],
        'pass-success-to': 'CommandParser',
        'pass-fail-to': 'BREAK',  # Initiates Break as Failure
        'use-history': True,
        'output-success': lambda x: True,
        'config-filepath': './agent_config.json'
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
        'prompt-formatter': lambda x: lambda y: lambda z: f"Task: {z[1]} |Android Output: {y} |Current Screen: {z[0]} ",
        'call-before-execute': [
            CallCommand(agent_name="AndroidNode", agent_command="get-screen"),
            CallCommand(agent_name="MasterNode", agent_command="get-last-output")
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
    },

}
