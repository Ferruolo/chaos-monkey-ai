# Agentic Testing Module

## How to Use (Theoretically)
1. Download Android Studio/SDK, install all requirements
2. Install python/all requirements
3. get anthropic API key/set all requirements
4. Set Claude API Key and Android SDK path in .env file
5. Make your android app, install on phone using Android Studio (should be named com.example-my-sample-application)
6. Make sure your android app is in the hot seat!
7. Adjust prompts as you see fit
8. Edit necessary items in main.py
9. Run it and enjoy your summary



## Basic Explanation
This repository uses agentic AI to move through an 
application, identifying the issues. It defines two 
actual AI agents, which are the Command Parser 
(which translates from natural language to machine language)
and the verifier node (which ensures that the task that was 
supposed to get completed gets completed). There are also the
two manual nodes, the Android Node (which houses the android controller),
and the master node (which tells everything what to do).
You can see the way that these nodes interact within 
src/behavior_definition.py.

## Next steps:
1. I want to move away from the manual node, but don't know how to prompt
well enough to. Eventually, this node should do Depth First Search

2. We need to add more commands so that the model has the total capability of a human CLI tester

# Please reach out to andrew.ferruolo@gmail.com with any questions
