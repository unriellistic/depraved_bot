import disnake
from depraved_bot.config import *

def check_roles(member: disnake.Member, required_kinks: list[RequiredKink], optional_kinks: list[OptionalKink]):
    '''Checks a member's roles, and returns lists of required and optional roles that are missing.'''
    role_list =  [role.id for role in member.roles]

    missing_required = []
    missing_optional = []
    
    for kink in required_kinks:
        if kink.id not in role_list:
            missing_required.append(kink)
    
    for kink in optional_kinks:
        if not set(kink.flatten()) & set(role_list):
            missing_optional.append(kink)

    return missing_required, missing_optional