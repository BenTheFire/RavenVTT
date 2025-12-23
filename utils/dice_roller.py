import re
import random


def roll_dice(num_dice, num_sides):
    """Rolls a specified number of dice and returns the list of results."""
    return [random.randint(1, num_sides) for _ in range(num_dice)]


def parse_and_roll(component):
    """Parses a single dice string component (e.g., '4d6kh3', '1d20A') and returns the rolls and total."""
    component = component.strip()
    
    # Regex to capture the core dice, and the optional modifier part
    match = re.match(r'(\d+)d(\d+)(.*)', component, re.IGNORECASE)
    if not match:
        # Handle flat numbers like "+ 5"
        if component.isdigit():
            val = int(component)
            return {'component': component, 'rolls': [val], 'total': val, 'text': f"{component} = {val}"}
        return None

    num_dice, num_sides, modifier = match.groups()
    num_dice, num_sides = int(num_dice), int(num_sides)
    modifier = modifier.lower()

    rolls = roll_dice(num_dice, num_sides)
    original_rolls = list(rolls)
    total = 0
    text_parts = [f"{component}: {original_rolls}"]

    # Handle Advantage/Disadvantage
    if 'a' in modifier:
        if num_dice != 1: # Advantage/Disadvantage typically applies to a single roll
            return None 
        second_roll = roll_dice(1, num_sides)
        original_rolls.extend(second_roll)
        total = max(rolls[0], second_roll[0])
        text_parts = [f"{component}: [{rolls[0]}, {second_roll[0]}] -> {total}"]
    elif 'd' in modifier:
        if num_dice != 1:
            return None
        second_roll = roll_dice(1, num_sides)
        original_rolls.extend(second_roll)
        total = min(rolls[0], second_roll[0])
        text_parts = [f"{component}: [{rolls[0]}, {second_roll[0]}] -> {total}"]
    
    # Handle Keep Highest/Lowest
    elif 'kh' in modifier:
        kh_match = re.search(r'kh(\d+)', modifier)
        if kh_match:
            keep_count = int(kh_match.group(1))
            rolls.sort(reverse=True)
            kept_rolls = rolls[:keep_count]
            total = sum(kept_rolls)
            text_parts.append(f"-> Kept {kept_rolls} = {total}")
    elif 'kl' in modifier:
        kl_match = re.search(r'kl(\d+)', modifier)
        if kl_match:
            keep_count = int(kl_match.group(1))
            rolls.sort()
            kept_rolls = rolls[:keep_count]
            total = sum(kept_rolls)
            text_parts.append(f"-> Kept {kept_rolls} = {total}")

    # Standard roll
    else:
        total = sum(rolls)
        text_parts.append(f"-> {total}")

    return {
        'component': component,
        'rolls': original_rolls,
        'total': total,
        'text': ' '.join(text_parts)
    }


def roll(dice_string):
    """Rolls a complex dice string and returns a list of results and the grand total."""
    components = dice_string.split('+')
    results = []
    grand_total = 0

    for comp in components:
        result = parse_and_roll(comp)
        if result:
            results.append(result)
            grand_total += result['total']
    
    return results, grand_total
