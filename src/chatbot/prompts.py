
def incorrect_station_prompt_builder(close_stations):
    suggestion = ", ".join(close_stations[1])
    return {
        "role": "system",
        "content": (
            "You are a railway assistant helping a user. The station "
            f"'{close_stations[0]}' was not recognised. Try: {suggestion}."
        )
    }

def reply_prompt_builder(reply):
    return {
        "role": "system",
        "content": (
            "You are a railway assistant helping a user. "
            "Only provide the user with the following information.\n" + reply
        )
    }

def reply_delay_builder(reply):
    return {
        "role": "system",
        "content": (
            "You are a railway assistant. You predict the train will be "
            f"{reply} minutes delayed. Be professional and discuss nothing else."
        )
    }

def route_prompt_builder(reply):
    return {
        "role": "system",
        "content": (
            "You are a railway assistant. Explain the entire route below. "
            "Provide the full route.\n" + reply
        )
    }

def add_focused_followup(keys):
    prompt = (
        "Just ask the user for the following missing information:\n" +
        "\n".join(f"- {key}" for key in keys) +
        "\nDo not discuss anything else."
    )
    return {"role": "assistant", "content": prompt}

def add_ticket_followup():
    prompt = "Tell the user that they can purchase their ticket using the link provided. Do not discuss anything else."
    return {"role": "assistant", "content": prompt}
