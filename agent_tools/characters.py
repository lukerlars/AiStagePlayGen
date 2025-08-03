from langchain_core.tools import tool 
from db.handler import add_entry, Character, Relationships


@tool
def create_character(
    character_name : str,
    age : int,
    gender: str,
    disposition: str,
    relationships_out: dict[str, str],
    relationships_in : dict[str, str],
    )-> str:
    """Create a new character

      inputs
        character_name (str): Name of character
        age (int): Age of character
        gender (str): Gender of character
        disposition (str) : One-word characteristic describing the characters personality
        
        relationships_out (dict[str,str]): Dict containing the outgoing relationships for 
            the characters. That is, how *this* character relates *to* the other. Dict key
            is name of other character, value is nature of relationship. Example: 
            If creating a character named Victoria, and passing relationships_in =
                {"Martinques": "Husband", "Evangeline": "Bitter enemy and rival", ...}
            Means Victoria regards Martiniques as her husband, and Evangeline as her bitter 
            enemy and rival.
       
        relationships_in: Dict containing the incoming relationship of the character. How
            the other characters relates to the created character. Example: 
            If creating a character named Victoria and passign relationship_out =
            {"Velasques": "Insignificant ambivalence", "Evangeline": "Secret crush", ...}
            Means Velasques regards Victoria with insignificant ambivalencel, and Evangeline
            has a secret crush on Victoria
    """

    character = Character(
        name = character_name,
        gender= gender,
        age = age, 
        disposition= disposition
        )

    try:  
        add_entry(character)
    except Exception as e:
        print(f"error creating character {e}")

    # Add character outwards facing relationships
    for recipient, relation  in relationships_out.items():
        relationship = Relationships(
            character = character_name,
            recipient_character = recipient,
            relationship = relation,
        )
        try:
            add_entry(relationship) 
        except Exception as e:
            print(f"Error creating outwards relationship {e}")
    
    # Add characters inward facing relationships
    for deemer, relation  in relationships_in.items():
        relationship = Relationships(
            character = deemer,
            recipient_character = character_name,
            relationship = relation,
        )
        try:
            add_entry(relationship) 
        except Exception as e:
            print(f"Error creating inwards relationship {e}")
     

    return f"character {character_name} created" 


