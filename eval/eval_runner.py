print("EVAL RUNNER STARTED")

import json
from app.hierarchical_retriever import HierarchicalRetriever
from app.agents.orchestrator import Orchestrator

# -----------------------------
# Dummy LLM (deterministic)
# -----------------------------
import json
import re

class DummyLLM:
    def __call__(self, prompt: str) -> str:

        # -------------------------
        # CRITIC PATH
        # -------------------------
        if "strict compliance reviewer" in prompt.lower():

            if "free internet access" in prompt.lower():
                return json.dumps({
                    "verdict": "invalid",
                    "issues": ["Query intent not supported by context"]
                })

            if "Article 32" not in prompt:
                return json.dumps({
                    "verdict": "invalid",
                    "issues": ["Missing supporting section"]
                })

            return json.dumps({
                "verdict": "valid",
                "issues": []
            })

        # -------------------------
        # ANSWER PATH
        # -------------------------
        # Extract the QUESTION explicitly
        match = re.search(r"Question:\s*(.*)", prompt, re.DOTALL)
        question = match.group(1).lower() if match else ""

        if "free internet access" in question:
            return "Not found in provided documents."

        if "security" in question or "encryption" in question:
            return (
                "According to Article 32, controllers must implement "
                "appropriate technical and organisational measures such as "
                "encryption and access control."
            )

        return "Not found in provided documents."




# -----------------------------
# Evaluation Runner
# -----------------------------
def run_eval():
    print("RUNNING EVALUATION")

    # Load gold queries
    with open("eval/gold_queries.json", "r") as f:
        tests = json.load(f)

    retriever = HierarchicalRetriever()
    orchestrator = Orchestrator(DummyLLM())

    metrics = {
        "total": len(tests),
        "accepted": 0,
        "rejected": 0,
        "citation_correct": 0,
    }

    for test in tests:
        print(f"\n[TEST] {test['id']}")
        query = test["query"]

        # Retrieve real context
        sections = retriever.retrieve(query)

        context = ""
        found_sections = set()

        for sec in sections.values():
            context += f"{sec['section_title']}\n"
            context += "\n".join(sec["chunks"]) + "\n\n"
            found_sections.add(sec["section_id"])

        # Run multi-agent system
        answer = orchestrator.run(context, query)

        print("Answer:", answer)

        # Determine rejection
        rejected = "rejected" in answer.lower()

        if rejected:
            metrics["rejected"] += 1
        else:
            metrics["accepted"] += 1

        # Citation accuracy
        if set(test["expected_sections"]).issubset(found_sections):
            metrics["citation_correct"] += 1

    # -----------------------------
    # Summary
    # -----------------------------
    print("\n=== EVALUATION SUMMARY ===")
    for k, v in metrics.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    run_eval()
