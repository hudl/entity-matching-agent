import re
import base64
from typing import Tuple


def parse_agent_output(output_text: str) -> Tuple[str, str, str]:
    """Parses the agent's final answer to extract the best match ID and justification."""

    match_id = "no match found"
    justification = output_text
    match = re.search(r"Best Match ID:\s*(.*)", output_text, re.IGNORECASE)
    if match:
        match_id = match.group(1).strip()
    score_text = re.search(r"Score:\s*(.*)", output_text, re.IGNORECASE)
    if score_text:
        score = score_text.group(1).strip()
    justification_split = re.split(r"Justification:", output_text, flags=re.IGNORECASE)
    if len(justification_split) > 1:
        justification = justification_split[1].strip()

    if match_id != "no match found":
        try:
            decoded_bytes = base64.b64decode(match_id)
            decoded_id = decoded_bytes.decode("utf-8")

            match_id = re.sub(r"^GSLSearchable(Team|Fixture)", "", decoded_id)

        except Exception as e:
            print(f"Could not Base64 decode '{match_id}': {e}")
            match_id = "decoding_error"

    return match_id, justification, score
