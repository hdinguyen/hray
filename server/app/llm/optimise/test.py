import dspy
from datasets import load_dataset
from llm.models import llm

dspy.configure(experimental=True)

class Agent(dspy.Module):
    def __init__(self, dataset, max_iters=5, verbose=False):
        self.dataset = dataset
        self.max_iters = max_iters
        self.verbose = verbose
        self.react = dspy.Predict("task, trajectory, possible_actions: list[str] -> action")

    def forward(self, split="train"):
        trajectory_results = []

        # Chọn dataset tương ứng
        data_split = self.dataset[split]

        for idx, example in enumerate(data_split):
            question = example["question"]
            answer = example["answer"]

            trajectory = []
            task = question
            if self.verbose:
                print(f"Task: {task}")

            for _ in range(self.max_iters):
                trajectory_ = "\n".join(trajectory)
                possible_actions = [answer] + ["think: ${...thoughts...}"]
                prediction = self.react(task=task, trajectory=trajectory_, possible_actions=possible_actions)
                trajectory.append(f"> {prediction.action}")

                if prediction.action.startswith("think:"):
                    trajectory.append("OK.")
                    continue

                # Giả lập phản hồi (ở đây, ta chỉ so sánh với answer thực)
                obs = f"Expected: {answer}, Predicted: {prediction.action}"
                reward = 1 if prediction.action == answer else 0
                done = prediction.action == answer
                trajectory.append(obs)

                if self.verbose:
                    print("\n".join(trajectory[-2:]))

                if done:
                    break

            trajectory_results.append({
                "trajectory": trajectory,
                "success": reward
            })

        return trajectory_results


gms8k = load_dataset("openai/gsm8k","main")

# Transform the test dataset into the expected format
class Example(dict):
    def inputs(self):
        return {"split": "test"}

test_data = [Example(x) for x in gms8k['test']][:1]

INSTRUCTIONS = """
Interact with a simulated household to achieve a high-level goal. Make sure to plan, track subgoals,
determine likely locations for common household items (e.g. desklamps will likely be on desks, shelfs, or dressers),
and explore systematically (e.g. check all desks one by one for desklamp).
""".strip()

agent = Agent(gms8k)
agent.set_lm(llm)
agent.verbose = True
agent.forward("train")
metric = lambda x, y, trace=None: y.success

#evaluate = dspy.Evaluate(devset=test_data, metric=metric, display_progress=True, num_threads=16)
#evaluate(agent)
