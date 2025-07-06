import base64
import json
import os
import requests
from typing import List, Dict, Any

from langchain_core.tools import tool

# from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel, Field

# API Keys
HUDL_API_KEY = os.getenv("HUDL_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Validate that all required variables are set
if not all([HUDL_API_KEY, TAVILY_API_KEY]):
    raise ValueError("One or more environment variables are not set.")

GRAPHQL_ENDPOINT = "https://master.thorhudl.com/api/graphql/query"
HEADERS = {
    "Authorization": f"Bearer {HUDL_API_KEY}",
    "Content-Type": "application/json",
}


# ---Step 1: Tool Definitions ---


# --- Tool 1: Get Team by ID ---
class GetTeamByIdInput(BaseModel):
    team_id: str = Field(description="The unique ID of the team to retrieve.")


@tool(args_schema=GetTeamByIdInput)
def get_team_by_id(team_id: str) -> Dict[str, Any]:
    """Fetches the full details for a single team by its unique ID."""
    get_team_query = f"""
        query getTeams {{
          searchableTeams(query: [{{ field: ID, operator: EQUALS, values: ["{team_id}"] }}]) {{
            items {{ id name sport gender regionName teamType teamMembers {{ preferredJersey individual {{ id commonName {{ fullName }} }} }} competitions {{ id name }} }}
          }}
        }}
    """
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            headers=HEADERS,
            data=json.dumps({"query": get_team_query}),
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            return {"error": "GraphQL query failed.", "details": data["errors"]}

        items = data.get("data", {}).get("searchableTeams", {}).get("items", [])
        return (
            items[0] if items else {"error": f"No entity found with GSL ID {team_id}"}
        )

    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}
    except (json.JSONDecodeError, IndexError):
        return {"error": "Failed to parse API response or find entity."}


# --- Tool 2: Search for Matching Teams ---
class FindMatchingTeamsInput(BaseModel):
    source_team_id: str = Field(description="The ID of the source team")
    search_term: str = Field(
        description="A name or keyword to search for matching teams."
    )


@tool(args_schema=FindMatchingTeamsInput)
def find_matching_teams(source_team_id: str, search_term: str) -> List[Dict[str, Any]]:
    """Searches for teams by a keyword and returns a list of potential matches."""

    encoded_source_id = base64.b64encode(
        f"GSLSearchableTeam{source_team_id}".encode("utf-8")
    ).decode("utf-8")

    get_teams_query = f"""
        query searchTeams {{
          searchableTeams(searchTerm: "{search_term}") {{
            items {{ id }}
          }}
        }}
    """
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            headers=HEADERS,
            data=json.dumps({"query": get_teams_query}),
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            print(f"GraphQL API returned an error: {data['errors']}")
            return []

        searched_items = (
            data.get("data", {}).get("searchableTeams", {}).get("items", [])
        )

        return [item for item in searched_items if item.get("id") != encoded_source_id]

    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return []
    except json.JSONDecodeError:
        print("Failed to parse API response.")
        return []


# --- Tool 3: Decode Base64 encoded ids ---
class Base64DecodeInput(BaseModel):
    encoded_id: str = Field(description="The base64 encoded id string to decode.")


@tool(args_schema=Base64DecodeInput)
def decode_base64_id(encoded_id: str) -> str:
    """Decodes a base64 encoded string and returns the original value."""
    try:
        encoded_id = encoded_id.strip()

        decoded_bytes = base64.b64decode(encoded_id)
        decoded_string = decoded_bytes.decode("utf-8")

        return decoded_string

    except Exception as e:
        print(f"Error decoding base64 string '{encoded_id}': {e}")
        return ""


# --- Tool 4: Add Multiple Numbers ---
class AddNumbersInput(BaseModel):
    numbers: List[float] = Field(description="A list of numbers to add together.")


@tool(args_schema=AddNumbersInput)
def add_multiple_numbers(numbers: List[float]) -> int:
    """Adds multiple numbers together and returns the sum."""
    try:
        if not numbers:
            return 0

        total = sum(numbers)

        return total

    except Exception as e:
        print(f"Error adding numbers: {e}")
        return 0


# --- Tool 5: Get Fixture by ID ---
class GetFixtureByIdInput(BaseModel):
    fixture_id: str = Field(description="The unique ID of the fixture to retrieve.")


@tool(args_schema=GetFixtureByIdInput)
def get_fixture_by_id(fixture_id: str) -> Dict[str, Any]:
    """Fetches the full details for a single fixture by its unique ID."""
    query = f"""
        query getFixtures {{
          searchableFixtures(searchTerm: "{fixture_id}") {{
            nodes {{ id localDate homeTeam {{ id name }} awayTeam {{ id name }} sport competitionName result {{ scores {{ teamId standardScore additionalScore }} }} individuals {{ nodes {{ id commonName {{ fullName }} }} }} fixtureRosters {{ nodes {{ individualId teamId jersey qualifier }} }}
            }}
          }}
        }}
    """
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            headers=HEADERS,
            data=json.dumps({"query": query}),
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            return {"error": "GraphQL query failed.", "details": data["errors"]}

        nodes = data.get("data", {}).get("searchableFixtures", {}).get("nodes", [])
        return (
            nodes[0] if nodes else {"error": f"No fixture found with ID {fixture_id}"}
        )

    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}
    except (json.JSONDecodeError, IndexError):
        return {"error": "Failed to parse API response or find fixture."}


# --- Tool 6: Find Matching Fixtures ---
class FindMatchingFixturesInput(BaseModel):
    source_fixture_id: str = Field(description="The ID of the source fixture")
    search_term: str = Field(
        description="A name or keyword to search for matching fixtures."
    )


@tool(args_schema=FindMatchingFixturesInput)
def find_matching_fixtures(
    source_fixture_id: str, search_term: str
) -> List[Dict[str, Any]]:
    """Searches for fixtures by a keyword and returns a list of potential matches."""

    encoded_source_id = base64.b64encode(
        f"GSLSearchableFixture{source_fixture_id}".encode("utf-8")
    ).decode("utf-8")

    query = f"""
        query searchFixtures {{
          searchableFixtures(searchTerm: "{search_term}") {{
            nodes {{ id }}
          }}
        }}
    """
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            headers=HEADERS,
            data=json.dumps({"query": query}),
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            print(f"GraphQL API returned an error: {data['errors']}")
            return []

        searched_items = (
            data.get("data", {}).get("searchableFixtures", {}).get("nodes", [])
        )
        return [item for item in searched_items if item.get("id") != encoded_source_id]

    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return []
    except json.JSONDecodeError:
        print("Failed to parse API response.")
        return []


# --- Tool 8: The Google Search Tool ---
# tavily_tool = TavilySearchResults(max_results=3)
# tavily_tool.name = "tavily_search_results_json"


def get_agent_tools(entity_type: str) -> List[Any]:
    """Returns a list of tools based on the entity type."""
    if entity_type.lower() == "team":
        return [get_team_by_id, find_matching_teams]
    elif entity_type.lower() == "fixture":
        return [get_fixture_by_id, find_matching_fixtures]
    else:
        raise ValueError(f"Unsupported entity type: {entity_type}")
