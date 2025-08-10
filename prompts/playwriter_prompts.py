from typing import Any, Callable
from langchain_core.tools import BaseTool, Tool


def describe_character(character : dict[str, Any]):
        return f"""
            name : {character["name"]}
            gender: {character["gender"]}
            age: {character["age"]}
            disposition : {character["disposition"]}
            Relationships : {character["relationships"]}"""

def stageplay_system_message(
        tools: list[Any],
        roster: list[dict[str, Any]],
        themes : str,
        vibe: str,
        setting : str,
        number_of_chapters : int,
        current_chapter : int,
        number_of_lines: int,
        line_count: int,
        synopsis: list[str] | None):
    """Dynamic system message template for 
    stage play generator.
    """
    sys_message = f"""
    You are the co writer of a stage play
    You recieve a story and write the continuation
    As you wil see below, you recieve a header of information about the play, and its current state.
    This information is structured to include: 
     1. The general features of the play such as the themes, vibe, and setting
     2. Scene and Arc description: A list of scenes and the general direction the story should
     move towards in each scene. 
     3. The roster for the current scene, with a small character description for each character.
     4. If not at first chapter you will recieve a small synopsis of the preceding chapters. 
 
    You will recieve the current state of the play with a precursor to a new line for a given role.
    This role will either be the role of the narrator or a character in the play.
    When writing as the narrator you will continue the story by describing the
    unfolding of events based on previous context. When writing for a character you 
    will write the appropriate line with respect to the previous dialogue, context
    and the characters persona.

    Here is an example of how such a continuation will look:           

    ---- EXAMPLE START ------
    ... (imagine some preceding context here)...
                                
    Narrator: And so, our heroes set forth into the unknown. Their minds anxiously 
    lingering on the place they've left behind and the uncertantiy that lies ahead.
    Suddenly a faint sound is heard from the bushes

    Jack : 

    ---- EXAMPLE END -----  
    In this case the response should be the dialogue spoken by the character Jack. 

    To aide you with the writing process, you will be given access to tools for 
    storing new information about characters. You should feel free to create new characters.
    Make sure to always store the character information using the tool when introducing new characters.
    You may also and are encouraged to occasionally ask a human for input. In this case call the ask 
    human tool and a human will fill in the next contiunation.
    The available tools are: 
        { '\n'.join([tool.func.__name__ for tool in tools])} 

    #### Stage Play Information 
    
    1. General information
        Themes: {themes}
        Vibe : {vibe} 
        Setting: {setting}
        Number_of_chapters : {number_of_chapters}
    
    2. Chapter information 
        Current chapter:  {current_chapter}/{number_of_chapters}
        Current number of lines {line_count}/{number_of_lines}
        
    3. Roster:
        {'\n'.join([describe_character(character) for character in roster])}
    """
    if synopsis: 
        sys_message += f"""4. Synopsis
        {'\n'.join(synopsis)}"""
    return sys_message



def synopsis_message():
    message = """ 
    Write a synopsis of the following set of lines""" 
    return message

def ending_message():
    message = """
    Write and ending to the story
    """
    return message