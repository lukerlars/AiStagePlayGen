import handler as db

### Characters  -------


character_luna = db.Character(
    name="Luna",
    gender= "F", 
    age=16,
    disposition= "Sassy"
)    

luna_relationships = [
    db.Relationships(
        character = "Luna",
        recipient_character = "Swedenborg",
        relationship = "Aimicable"
        ),
    db.Relationships(
        character = "Luna",
        recipient_character = "Captain Flask",
        relationship = "Veneration and slighthly frightened"
        ),
]


character_swedenborg = db.Character(
    name="Swedenborg",
    gender= "M", 
    age=15,
    disposition= "Melancholic",
)

swedenborg_relationships =[
    db.Relationships(
    character = "Swedenborg",
    recipient_character = "Luna",
    relationship = "Unrequited Infatuation"
    ),
    db.Relationships(
        character = "Swedenborg",
        recipient_character = "Captain Flask",
        relationship = "Veneration"
    ),
]

character_captain_flask = db.Character(
    name="Captain Flask",
    gender= "M", 
    age=55,
    disposition= "Seasoned seafaring captain",
)

captain_flask_relationships= [
    db.Relationships(
        character = "Captain Flask",
        recipient_character = "Luna",
        relationship = "Reminds him of lost youth and daughter that never was"
    ),
    db.Relationships(
        character = "Captain Flask",
        recipient_character = "Swedenborg",
        relationship = "Sees him as a young man with lots of potential"
    ),
]

if __name__ == "__main__":
    characters = [character_luna, character_swedenborg, character_captain_flask]
    relationships = luna_relationships +swedenborg_relationships + captain_flask_relationships

    for character in characters:
        db.add_entry(character)
    
    for relationship in relationships:
        db.add_entry(relationship)
