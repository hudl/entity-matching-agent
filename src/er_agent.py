import csv
from typing import List

# LangChain Imports...
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_aws import ChatBedrock
from langchain.agents import AgentExecutor, create_tool_calling_agent

from dotenv import load_dotenv

load_dotenv()

from tools import get_agent_tools, add_multiple_numbers
from util import parse_agent_output
from data_sources import fetch_ids_from_postgres, fetch_ids_from_csv
from sys_prompts import get_entity_matching_system_prompt


# --- Create the Agent with a Prompt ---


def create_entity_matching_agent(scoring_prompt: str, tools: list):
    """Creates an agent with a specific scoring prompt and tools."""

    llm = ChatBedrock(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_kwargs={"temperature": 0.0},
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", scoring_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=25)


# --- Main Batch Processing Logic ---


async def run_single_process(agent_executor: AgentExecutor, source_id: str):
    """Processes a single source ID with the agent and returns the result."""
    if not source_id:
        print("Error: No source ID provided.")
        return None

    print(f"\n--- Processing Source GSL ID: {source_id} ---")
    user_input = f"Please research and compare the entity with GSL ID {source_id} to find the best merge candidate. Follow your instructions precisely."

    try:
        response = await agent_executor.ainvoke({"input": user_input})
        output_data = response.get("output", [])
        output_text = ""
        if isinstance(output_data, list) and output_data:
            if isinstance(output_data[0], dict) and "text" in output_data[0]:
                output_text = output_data[0]["text"]
        elif isinstance(output_data, str):
            output_text = output_data

        best_match_id, justification, score = parse_agent_output(output_text)

        print(f"--- Result for {source_id}: Found match '{best_match_id}' ---")
        return {
            "source_gsl_id": source_id,
            "best_match_gsl_id": best_match_id,
            "score": score,
            "justification": justification,
        }

    except Exception as e:
        print(f"!! An error occurred while processing {source_id}: {e} !!")
        return {
            "source_gsl_id": source_id,
            "best_match_gsl_id": "processing error",
            "score": str(e),
            "justification": "",
        }


def run_batch_process(
    agent_executor: AgentExecutor, source_ids: List[str], output_file: str
):
    """Processes a list of source IDs with the agent and writes results to a CSV."""
    print(f"Starting batch process for {len(source_ids)} IDs...")

    with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(
            ["source_gsl_id", "best_match_gsl_id", "score", "justification"]
        )

        for source_id in source_ids:
            if not source_id:
                continue

            print(f"\n--- Processing Source GSL ID: {source_id} ---")
            user_input = f"Please research and compare the entity with GSL ID {source_id} to find the best merge candidate. Follow your instructions precisely."

            try:
                response = agent_executor.invoke({"input": user_input})
                output_data = response.get("output", [])
                output_text = ""
                if isinstance(output_data, list) and output_data:
                    if isinstance(output_data[0], dict) and "text" in output_data[0]:
                        output_text = output_data[0]["text"]
                elif isinstance(output_data, str):
                    output_text = output_data

                best_match_id, justification, score = parse_agent_output(output_text)

                print(f"--- Result for {source_id}: Found match '{best_match_id}' ---")
                writer.writerow([source_id, best_match_id, score, justification])

            except Exception as e:
                print(f"!! An error occurred while processing {source_id}: {e} !!")
                writer.writerow([source_id, "processing error", str(e), ""])

    print(f"\nBatch process complete. Results saved to '{output_file}'.")


if __name__ == "__main__":
    # This part remains for potential direct execution,
    # but the main orchestration will be in main.py
    ids_to_process = fetch_ids_from_csv(
        file_path="/Users/suraj.salunke/Desktop/teams_mock_data.csv", limit=100
    )

    if ids_to_process:
        output_csv_file = "results/f_output_results_weighted_iter-4.csv"
        # Create an agent with the default weighted prompt
        entity_matching_agent = create_entity_matching_agent(
            get_entity_matching_system_prompt("weighted", "fixture"),
            [
                *get_agent_tools("fixture"),
                add_multiple_numbers,
            ],
        )
        run_batch_process(
            agent_executor=entity_matching_agent,
            source_ids=ids_to_process,
            output_file=output_csv_file,
        )
    else:
        print("No IDs fetched from the database. Halting process.")
