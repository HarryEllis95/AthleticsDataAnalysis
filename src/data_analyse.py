def get_event_units(event_display_name: str) -> str:
    name_lower = event_display_name.lower()

    # Sprints
    if any(word in name_lower for word in ["60", "100", "200", "400", "relay", "hurdles"]):
        return "seconds"

    # Distance
    if any(word in name_lower for word in ["800", "1500", "mile","3000","5000", "10000", "steeplechase"]):
        return "seconds"

    if any(word in name_lower for word in ["marathon", "walk"]):
        return "seconds"

    if any(word in name_lower for word in ["jump", "throw", "vault", "discus", "shot put", "javelin", "hammer"]):
        return "metres"

    if "decathlon" in name_lower or "heptathlon" in name_lower:
        return "points"

    return "units"