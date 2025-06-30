# Entity Matching AI Agent

An intelligent agentic AI system for automated entity matching and resolution. This agent leverages multiple data sources and Hudl's AWS Bedrock provisioned models to identify and match entities across different datasets.

## Overview

The Entity Matching AI Agent performs intelligent entity resolution by:

- **Data Retrieval**: Fetches source entity data using provided tools
- **Context Enhancement**: Adds contextual information through Google Search integration
- **Candidate Discovery**: Identifies potential matching candidates from target datasets
- **Intelligent Matching**: Compares source entities with candidates using Hudl's AWS Bedrock provisioned models
- **Result Ranking**: Provides ranked suggestions for the most suitable target candidates

## Prerequisites

Before running this application, ensure you have:

- AWS CLI configured with Hudl main account access
- Python 3.8+ installed
- Tavily AI API access
- Jupyter Notebook environment

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

### 3. API Configuration And Setting Env Varible

Obtain your Tavily AI API key and set it as an environment variable:

```bash
export TAVILY_API_KEY="your_tavily_api_key_here"
export AWS_PROFILE="hudl_aws_main_account_profile_name"
```

### 4. Dependencies

Install the required Python packages:

```bash
pip install -U requests langchain langchain-aws langchain-community pydantic boto3 tavily-python
```

## Usage

### 1. Prepare Input Data

Before running the agent, create a CSV file on your desktop with the GSL entity IDs that need to be resolved and merged:

1. Create a new CSV file on your desktop (e.g., `input_ids.csv`)
2. Add a column header named `source_gsl_id`
3. Add the GSL entity IDs that need to be resolved, one per row
4. Update the script with the csv file paths.

**Example CSV structure:**

```csv
source_gsl_id
12345
67890
11111
22222
```

### 2. Execute the Agent

Launch the Jupyter notebook:

```bash
jupyter notebook er_agent.ipynb
```

Navigate to the notebook in your browser and run all cells to start the entity matching process.

## Technologies Used

- **LangChain**: Agent framework and tool orchestration
- **AWS Bedrock**: Large language model inference
- **Tavily AI**: Web search and context enhancement
- **Boto3**: AWS SDK for Python
- **Jupyter**: Interactive development environment
