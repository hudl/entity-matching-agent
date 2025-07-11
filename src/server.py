from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from er_agent import create_entity_matching_agent, run_single_process
from sys_prompts import get_entity_matching_system_prompt
from tools import get_agent_tools, add_multiple_numbers


app = FastAPI(
    title="Entity Matching Agent Server",
    description="An API to interact with the entity matching agent.",
    version="1.0.0",
)

# Add CORS middleware
# This will allow requests from any origin
# For production, you should restrict this to specific domains

origins = [
    "https://localhost.app.admin.thorhudl.com:8095",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the agent on startup
# entity_matching_agent = create_entity_matching_agent(
#     get_entity_matching_system_prompt("weighted", "fixture"),
#     [
#         *get_agent_tools("fixture"),
#         add_multiple_numbers,
#     ],
# )

entity_matching_agent = create_entity_matching_agent(
    get_entity_matching_system_prompt("weighted", "team"),
    [
        *get_agent_tools("team"),
        add_multiple_numbers,
    ],
)


@app.get("/match/")
def match_entity(source_gsl_id: str):
    """
    Processes a single source GSL ID to find a matching entity.
    - **source_gsl_id**: The GSL ID of the source entity to process.
    """
    if not source_gsl_id:
        raise HTTPException(
            status_code=400, detail="source_gsl_id query parameter cannot be empty."
        )

    result = run_single_process(
        agent_executor=entity_matching_agent, source_id=source_gsl_id
    )

    if result is None:
        raise HTTPException(status_code=500, detail="Agent returned an empty result.")

    if (
        result.get("best_match_gsl_id") == "processing error"
        or result.get("best_match_gsl_id") == "decoding error"
    ):
        raise HTTPException(
            status_code=500, detail=f"Agent processing error: {result.get('score')}"
        )

    if result.get("best_match_gsl_id") == "no match found":
        return HTTPException(
            status_code=404, detail=f"No match found for source GSL ID {source_gsl_id}."
        )

    return result


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5000)
