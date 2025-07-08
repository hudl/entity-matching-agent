import argparse
from er_agent import create_entity_matching_agent, run_batch_process
from sys_prompts import get_entity_matching_system_prompt
from data_sources import fetch_ids_from_csv, fetch_ids_from_postgres
from tools import get_agent_tools, add_multiple_numbers

# --- Configuration ---

# 1. Toolset Definitions
DATA_RETRIEVER = {
    "csv": [fetch_ids_from_csv],
    "postgres": [fetch_ids_from_postgres],
}


# --- Main Orchestration Logic ---


def main(
    entity_type: str,
    data_source: str,
    source_input: str,
    scoring_method: str,
    output_path: str,
):
    """
    Orchestrates a chain of agents to perform entity resolution.
    """

    print(f"--- Starting Autonomous ER Agent Chain ---")
    print(f"Entity Type: {entity_type}")
    print(f"Data Source: {data_source}")
    print(f"Scoring Method: {scoring_method}")

    if data_source == "csv":
        source_ids = fetch_ids_from_csv(source_input, 100)
    elif data_source == "postgres":
        source_ids = fetch_ids_from_postgres(source_input, 100)

    data_tools = [
        *get_agent_tools(entity_type.to_lower()),
        add_multiple_numbers,
    ]
    if not data_tools:
        print(f"Error: Invalid entity type '{entity_type}'.")
        return

    agent_prompt = get_entity_matching_system_prompt(
        scoring_method="weighted", entity_type=entity_type.to_lower()
    )
    agent = create_entity_matching_agent(scoring_prompt=agent_prompt, tools=data_tools)

    run_batch_process(agent, source_ids, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Autonomous Entity Resolution Agent Chain"
    )
    parser.add_argument(
        "entity_type",
        type=str,
        choices=["team", "fixture"],
        help="The type of entity to process.",
    )
    parser.add_argument(
        "data_source",
        type=str,
        choices=["csv", "postgres"],
        help="The data source to use.",
    )
    parser.add_argument(
        "source_input",
        type=str,
        help="File path for CSV or table name for Postgres.",
    )
    parser.add_argument(
        "--scoring_method",
        type=str,
        choices=["weighted", "binary"],
        default="weighted",
        help="The scoring method to use for matching.",
    )
    parser.add_argument(
        "output_path",
        type=str,
        help="File path for CSV for output results.",
    )
    args = parser.parse_args()

    main(
        args.entity_type,
        args.data_source,
        args.source_input,
        args.scoring_method,
        args.output_path,
    )
