"""
Panchayat Bridge — LangChain Tool Wrappers
============================================
Wraps data/ tool functions with LangChain @tool decorator
so LangGraph agents can use them for tool-augmented reasoning.
"""
import requests
from langchain_core.tools import tool
from data.manifesto_bank import MANIFESTO_BANK, claim_manifesto

@tool
def search_ideology_db(archetype: str, category: str) -> str:
    """Search real-world Indian political scenarios matching a candidate archetype's ideology and a policy category.
    
    Args:
        archetype: One of 'dharma_rakshak', 'vikas_purush', 'jan_neta', 'mukti_devi'
        category: One of 'agriculture', 'technology', 'economy', 'social_welfare', 'governance'
    """
    from data.tools import search_ideology_db as _fn
    return _fn(archetype, category)


@tool
def get_past_policies(archetype: str) -> str:
    """Get the manifesto policies and historical precedents for a candidate archetype.
    
    Args:
        archetype: One of 'dharma_rakshak', 'vikas_purush', 'jan_neta', 'mukti_devi'
    """
    from data.tools import get_past_policies as _fn
    return _fn(archetype)


@tool
def analyze_player_move(action: str, archetype: str) -> str:
    """Analyze how a specific candidate archetype would perceive and react to the player's policy action.
    
    Args:
        action: Description of the player's policy action
        archetype: The AI candidate analyzing this action
    """
    from data.tools import analyze_player_move as _fn
    return _fn(action, archetype)


@tool
def get_demographic_sentiment(group_name: str) -> str:
    """Get current mood, demands, and sentiment of a voter demographic group.
    
    Args:
        group_name: One of 'kisan', 'yuva', 'vyapari', 'sarkari', 'gramin_nari'
    """
    from data.tools import get_demographic_sentiment as _fn
    return _fn(group_name)


@tool
def search_scenario_impact(policy_keyword: str) -> str:
    """Search for real-world impacts of similar policies from the Indian political scenarios database.
    
    Args:
        policy_keyword: A keyword or phrase to search for (e.g., 'MSP', 'digital', 'subsidy')
    """
    from data.tools import search_scenario_impact as _fn
    return _fn(policy_keyword)


@tool
def get_candidate_weakness(candidate_id: str) -> str:
    """Get scandal and weakness data for a candidate that opponents could exploit.
    
    Args:
        candidate_id: One of 'dharma_rakshak', 'vikas_purush', 'jan_neta', 'mukti_devi'
    """
    from data.tools import get_candidate_weakness as _fn
    return _fn(candidate_id)

@tool
def update_voter_share_in_db(candidate_id: str, group_id: int, shift_amount: float) -> str:
    """
    CRITICAL: Use this tool to actually change the election results.
    
    Args:
        candidate_id: 'vikas_purush', 'dharma_rakshak', etc.
        group_id: 0:Farmers, 1:Students, 2:Tech, 3:Labor, 4:Youth
        shift_amount: How much % you gain (0.5 to 3.0). 
                    This will be 'stolen' from your opponents automatically.
    """
    # 1. Map the string names the AI uses to the integer IDs in your Mongo init_db.py
    cid_map = {
        "vikas_purush": 0, 
        "dharma_rakshak": 1, 
        "jan_neta": 2, 
        "mukti_devi": 3,
        "player": 4 
    }
    
    uint_cid = cid_map.get(candidate_id)
    if uint_cid is None:
        return f"Error: Unknown candidate_id '{candidate_id}'"

    try:
        # 2. Hit your NEW FastAPI endpoint (running on port 8000)
        resp = requests.post("http://localhost:8000/api/apply-manifesto", json={
            "candidate_id": uint_cid,
            "group_id": group_id,
            "shift_amount": shift_amount
        }, timeout=5)
        
        if resp.status_code == 200:
            return f"Success: Voter share updated in Cloud MongoDB. Response: {resp.json()}"
        else:
            return f"Failed: Backend returned {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"System Error: Could not reach FastAPI server. Ensure uvicorn is running. Details: {e}"


@tool
def claim_and_deploy_manifesto(manifesto_id: int, candidate_id: int) -> str:
    """
    Selects a manifesto from the bank and applies its hardcoded effects 
    to the voter shares. This is the only way to shift the election numbers.
    
    Args:
        manifesto_id: The ID from the MANIFESTO_BANK (e.g., 201)
        candidate_id: Your integer ID (0-3 for NPCs)
    """
    # 1. Check if available and mark as used
    manifesto = claim_manifesto(manifesto_id, candidate_id)
    
    if not manifesto:
        return "Error: This manifesto ID is invalid or has already been claimed by someone else."

    # 2. Extract hardcoded effects
    target_group = manifesto["target_group_id"]
    shift = manifesto["shift_amount"]

    # 3. Hit your FastAPI Backend to run the Waterfall Math
    try:
        resp = requests.post("http://localhost:8000/api/apply-manifesto", json={
            "candidate_id": candidate_id,
            "group_id": target_group,
            "shift_amount": shift
        })
        
        if resp.status_code == 200:
            return f"SUCCESS: Deployed '{manifesto['title']}'. Shifted {shift}% in Group {target_group}."
        else:
            return f"FAILED: Backend error {resp.status_code}"
    except Exception as e:
        return f"CONNECTION ERROR: {e}"


def get_all_tools():
    """Return all available LangChain tools."""
    return [
        search_ideology_db,
        get_past_policies,
        analyze_player_move,
        get_demographic_sentiment,
        search_scenario_impact,
        get_candidate_weakness,
        update_voter_share_in_db,
    ]
