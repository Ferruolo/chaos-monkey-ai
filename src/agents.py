import anthropic
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


class Agent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])
        self.conversation_history: List[Dict[str, str]] = []

    def think(self, task: str) -> str:
        system_prompt = f"You are {self.name}, a {self.role}."

        human_prompt = f"Your task is: {task}\n\n"
        human_prompt += "Previous conversation:\n"
        for message in self.conversation_history[-5:]:  # Include last 5 messages for context
            human_prompt += f"{message['role']}: {message['content']}\n"

        prompt = f"{anthropic.HUMAN_PROMPT} {system_prompt}\n\n{human_prompt}{anthropic.AI_PROMPT}"

        response = self.client.completions.create(
            model="claude-2",
            prompt=prompt,
            max_tokens_to_sample=300,
            stop_sequences=[anthropic.HUMAN_PROMPT]
        )

        thought = response.completion.strip()
        self.conversation_history.append({"role": self.name, "content": thought})
        return thought

    def act(self, task: str) -> str:
        return self.think(task)


class Planner(Agent):
    def __init__(self):
        super().__init__("Planner", "strategic thinker and task decomposer")

    def create_plan(self, main_task: str) -> List[str]:
        plan_prompt = f"Create a step-by-step plan to accomplish the following task: {main_task}"
        plan_thought = self.think(plan_prompt)
        return [step.strip() for step in plan_thought.split('\n') if step.strip()]


class Executor(Agent):
    def __init__(self):
        super().__init__("Executor", "task implementer and problem solver")


class Critic(Agent):
    def __init__(self):
        super().__init__("Critic", "result evaluator and improvement suggester")

    def evaluate(self, task: str, result: str) -> str:
        eval_prompt = f"Evaluate the following result for the task '{task}': {result}"
        return self.think(eval_prompt)


class AgentSystem:
    def __init__(self):
        self.planner = Planner()
        self.executor = Executor()
        self.critic = Critic()

    def run(self, main_task: str) -> List[Dict[str, Any]]:
        results = []

        # Planning phase
        plan = self.planner.create_plan(main_task)
        print("Plan")
        print(plan)
        results.append({"phase": "planning", "output": plan})

        # Execution and evaluation phase
        for step in plan:
            execution_result = self.executor.act(step)
            results.append({"phase": "execution", "task": step, "output": execution_result})

            evaluation = self.critic.evaluate(step, execution_result)
            results.append({"phase": "evaluation", "task": step, "output": evaluation})

        return results


# Example usage
if __name__ == "__main__":
    system = AgentSystem()
    main_task = "Organize a virtual team-building event for a remote company with 5 employees"
    results = system.run(main_task)

    for result in results:
        print(f"Phase: {result['phase']}")
        if 'task' in result:
            print(f"Task: {result['task']}")
        print(f"Output: {result['output']}")
        print("---")
