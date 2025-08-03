from dataclasses import dataclass
from langchain_core.tools import tool 

@dataclass
class Character:
    name : str
    gender: str
    age : int
    disposition: str

    relationships : dict[str, str]

    def describe(self):
        return f"""
            name : {self.name}
            gender: {self.gender}
            age: {self.age}
            disposition : {self.disposition}
            Relationships : {'\n'.join([f'{u} : {v}' for u,v in self.relationships.items()])}"""



character_luna = Character(
    name="Luna",
    gender= "F", 
    age=16,
    disposition= "Sassy",
    relationships= {"Swedenborg": "Aimicable"})

character_swedenborg = Character(
    name="Swedenborg",
    gender= "M", 
    age=15,
    disposition= "Melancholic",
    relationships= {"Luna": "Unrequited Infatuation"})


roster = {"Luna": character_luna, 
              "Swedenborg": character_swedenborg}



## tool callling 
@tool
def get_character_description(character_name: str) -> str:
    """Get a short description for a character"""
    # TODO make better descriptions: add more thorough characted desc
    # to character dataclass 
    return str(roster[character_name])


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
            Means Velasques regard Victoria with insignificant ambivalencel, and Evnageline
            has a secret crush on Victoria
            Will error if referring to non existing character.
    """

    roster[character_name] = Character(name = character_name,
                     gender= gender,
                     age = age, 
                     disposition= disposition,
                     relationships= relationships_out)

    # Update relatinships for other character instances
    for character in relationships_in:
        try: 
            roster[character].relationships[character_name] = relationships_in[character]
        except Exception:
            raise ValueError(f"""Character :{character}, is not instantiated. Make sure to create 
                             the character before assigning relatinship""") 

    return f"caracter {character_name} created" 


