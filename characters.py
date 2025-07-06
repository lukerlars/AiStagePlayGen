from dataclasses import dataclass

@dataclass
class Character:
    name : str
    gender: str
    age : int
    disposition: str

    relationships : dict[str, str]


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

characters = {"Luna": character_luna, 
              "Swedenborg": character_swedenborg}