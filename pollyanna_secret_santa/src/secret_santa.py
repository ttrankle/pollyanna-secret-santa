from typing import Dict

import random
import copy

from logging import getLogger

logger = getLogger(__name__)

def secret_santa(participants) -> Dict:
    names_list = list(participants.keys())
    remaining = copy.copy(names_list)
    result = {}

    for name in names_list:
        available_names = [n for n in remaining if n != name]
        chosen = random.choice(available_names)
        result[name] = chosen
        remaining.remove(chosen)

    return result


def generate_secret_santa_results(participants: Dict, prior_year: Dict):
    """
    Generates a Secret Santa pairing result for a group of participants while avoiding
    conflicts based on previous years' results and preventing a person from drawing themselves.

    This function aims to assign two names (a "Genuine Gift" and a "Gag Gift") to each participant
    such that:
    1. No participant is assigned themselves for either gift.
    2. No participant receives the same person they had in the prior year (for either gift).

    The function ensures that the assignments are valid by repeatedly generating random
    assignments until all conflicts are resolved.

    Args:
        participants (dict): A dictionary where the keys are the names of participants and 
                             the values are their email addresses.
                             Example: {'Alice': 'alice@example.com', 'Bob': 'bob@example.com'}
        
        prior_year (dict): A dictionary where the keys are participant names and the values are lists
                           of names that the participant had in previous years (for both the genuine and gag gifts).
                           Example: {'Alice': ['Bob', 'Charlie'], 'Bob': ['Alice', 'David']}

    Returns:
        dict: A dictionary where each key is a participant's name and the value is a list with 
              two names [genuine gift, gag gift], representing the people they will be gifting.
              Example: {'Alice': ['Charlie', 'David'], 'Bob': ['Alice', 'Eve']}

    The algorithm works as follows:
    1. It repeatedly generates two sets of gift assignments: one for the genuine gift and one for the gag gift.
    2. It checks if any participant has been assigned themselves for either gift, or if a participant has received 
       the same person they gifted in the previous year.
    3. If conflicts are found, the process is restarted. Otherwise, the result is returned.
    """
    
    # Flag to indicate if a valid assignment has been found
    finished = False
    
    # Dictionary to store the final valid results
    result = {}

    # Repeat until a valid result is generated
    while not finished:
        try:
            # Generate two separate Secret Santa assignments
            gift_givers = secret_santa(participants)  # Assigns participants for genuine gifts
            gag_givers = secret_santa(participants)   # Assigns participants for gag gifts
        except Exception as e:
            # If there is an error in generating assignments, log it and try again
            logger.warning(f"Error occurred: {e}")
            continue

        # Assume no conflicts initially
        is_conflict = False
        
        # Temporary dictionary to store the generated pairings
        temp_result = {}

        # Iterate over participants and their assigned gift recipients (both genuine and gag)
        for person, (gift, gag) in zip(gift_givers.keys(), zip(gift_givers.values(), gag_givers.values())):
            # Check if the participant has drawn themselves for either gift
            if gift == gag or gift in prior_year.get(person, []) or gag in prior_year.get(person, []):
                # Conflict detected if a person is gifting themselves or someone they had last year
                is_conflict = True
                break 
            
            # No conflicts for this participant, store the pairing
            temp_result[person] = [gift, gag]

        # If no conflicts are found for all participants, the result is valid
        if not is_conflict:
            result = temp_result
            finished = True  # Mark the process as finished, we have valid assignments

    # Return the final Secret Santa assignments
    return result