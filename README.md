# Autonomous Entity Resolution AI Agent

An intelligent, multi-agent AI system for automated entity resolution. This system leverages a chain of specialized agents and Hudl's AWS Bedrock-provisioned models to dynamically identify, match, and resolve different entity types like teams and fixtures from various data sources.

## Overview

The Autonomous Entity Resolution AI Agent performs intelligent entity resolution through a modular, chain-of-agents approach:

- **Dynamic Agent Orchestration**: A main orchestrator (`src/main.py`) configures and chains agents based on user-defined tasks.
- **Specialized Agents**:
  - **Data Gathering Agent**: Fetches entity IDs from specified data sources (PostgreSQL or CSV).
  - **Entity Resolution Agent**: Performs the core matching logic using a dynamically selected set of tools and audit rules based on the entity type (e.g., 'team', 'fixture').
- **Flexible Data Sourcing**: Ingests data from PostgreSQL databases or local CSV files.
- **Advanced Matching Logic**: Utilizes sophisticated, weighted audit rules tailored to each entity type. For instance, fixture matching is based on a detailed audit of the associated teams.
- **Extensible Framework**: Easily add new entity types, data sources, or audit rules by extending the configuration in `src/main.py` and `src/sys_prompts.py`.

## Prerequisites

Before running this application, ensure you have:

- AWS CLI configured with Hudl main account access
- Python 3.8+ installed
- Access to a PostgreSQL database (if using it as a data source)

## Installation & Setup

### 1. AWS Authentication

Authenticate with the Hudl main account using AWS CLI:

```bash
aws sso login --profile hudl_aws_main_account_profile_name
```

### 2. Python Environment

Create and activate a Python virtual environment:

```bash
python -m venv entity-matching-env
source entity-matching-env/bin/activate  # On macOS/Linux
# or
entity-matching-env\Scripts\activate     # On Windows
```

### 3. Environment Variable Configuration

This project uses a `.env` file to manage environment variables. Create a file named `.env` in the root directory of the project and add the following variables.

```
# Hudl API Key for GraphQL endpoint
HUDL_API_KEY="your_hudl_api_key_here"

# AWS Profile for Boto3
AWS_PROFILE="your_hudl_aws_main_account_profile_name"

# PostgreSQL Database Credentials (only required if using postgres data source)
DB_HOST="your_db_host"
DB_NAME="your_db_name"
DB_USER="your_db_user"
DB_PASS="your_db_password"
DB_PORT="5432"
```

### 4. Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

The primary way to run the system is through the command-line interface of the main orchestrator script.

### Command-Line Execution

Execute the agent from your terminal using the following command structure:

```bash
python src/main.py {entity_type} {data_source} {source_input}
```

**Arguments:**

- `entity_type`: The type of entity to process.
  - Supported: `team`, `fixture`
- `data_source`: The source of the entity IDs.
  - Supported: `csv`, `postgres`
- `source_input`: The location of the data.
  - For `csv`: The absolute file path to your input CSV.
  - For `postgres`: The name of the table containing the IDs.

### Example Scenarios

**1. Matching Teams from a CSV File:**

```bash
python src/main.py team csv "/Users/suraj.salunke/Desktop/teams_to_match.csv"
```

_The CSV file must contain a header named `source_gsl_id`._

**2. Matching Fixtures from a PostgreSQL Table:**

```bash
python src/main.py fixture postgres "sports_fixtures_table"
```

### Output

The agent will print its progress to the console and save the final results to a new CSV file in the `results/` directory. The output filename will be dynamically generated based on the entity type and data source (e.g., `output_team_csv.csv`).

## Development & Notebooks

The original Jupyter notebooks (`langchain_ob/`) are still available for development, testing, and exploration purposes but are not part of the main autonomous workflow.
