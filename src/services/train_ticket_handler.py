'''
    Example call:
        - get_return_ticket_url('SOU', 'NOT', 'departing', '210325', '19', '30', 'arriving', '220425', '21', '30', 2, 3, {'JCP': 3, 'YNG': 1}, 0)
'''

NATIONAL_RAIL_URL: str = 'https://www.nationalrail.co.uk/journey-planner/'


def get_locations(origin: str, destination: str) -> str:
    """
    Returns a string containing the origin and destination locations for a train ticket.
    - Locations use CRS Codes

    Parameters:
    origin (str): The origin location of the train ticket.
    destination (str): The destination location of the train ticket.

    Returns:
    str: A string containing the origin and destination locations in the format "&origin={origin}&destination={destination}".
    """
    return f"&origin={origin}&destination={destination}"


def get_departure_time(method: str, type: str, date: str, hour: str, min: str) -> str:
    """
    Constructs a departure time string based on the provided method, type, date, hour, and minute.
    - Departure time should not be in the past
    - Date format: DD-MM-YY

    Args:
        method (str): The method of departure.
        type (str): The type of departure.
        date (str): The date of departure.
        hour (str): The hour of departure.
        min (str): The minute of departure.

    Returns:
        str: The constructed departure time string.
    """
    return f"&{method}Type={type}&{method}Date={date}&{method}Hour={hour}&{method}Min={min}"


def get_passengers(adults: int, children: int) -> str:
    """
    Returns a string representation of the passengers for a train ticket.

    Args:
        adults (int): The number of adult passengers.
        children (int): The number of child passengers.

    Returns:
        str: A string representation of the passengers in the format "&adults={adults}&children={children}".
    """
    return f"&adults={adults}&children={children}"


def get_railcards(railcards: dict[str, int]) -> str:
    """
    Constructs a string representation of railcards and their quantities for a train ticket request.
    
    Args:
        railcards (dict[str, int]): A dictionary mapping railcard names to their quantities.

    Returns:
        str: A string representation of railcards and their quantities in the format "&railcards=railcard1%7Cquantity1&railcards=railcard2%7Cquantity2&..."

    """
    railcards_str = ""
    for railcard, quantity in railcards.items():
        railcards_str += f"&railcards={railcard}%7C{quantity}"
    return railcards_str


def get_extra_time(extra_time: int) -> str:
    """
    Returns a string representation of the extra time parameter for a train ticket.
    - Ensure extra time is between 0 and 4
        0: No extra time
        1: 30 minutes extra time
        2: 1 hour extra time
        3: 1 hour 30 minutes extra time
        4: 2 hours extra time


    Args:
        extra_time (int): The extra time in minutes.

    Returns:
        str: A string representation of the extra time parameter in the format "&extraTime={extra_time}".
    """
    return f"&extraTime={extra_time}"


def get_single_ticket_url(origin: str, destination: str, leaving_date: str, leaving_hour: str, leaving_min: str, adults: int, children: int, railcards: dict[str, int], extra_time: int) -> str:
    """
    Constructs a URL for a single train ticket based on the provided parameters.

    Args:
        origin (str): The origin station of the train journey.
        destination (str): The destination station of the train journey.
        leaving_date (str): The date of departure in the format 'YYYY-MM-DD'.
        leaving_hour (str): The hour of departure in the format 'HH'.
        leaving_min (str): The minute of departure in the format 'MM'.
        adults (int): The number of adult passengers.
        children (int): The number of child passengers.
        railcards (dict[str, int]): A dictionary mapping railcard names to the number of railcards to apply.
        extra_time (int): The extra time in minutes to add to the journey duration.

    Returns:
        str: The constructed URL for the single train ticket.

    """
    return f"{NATIONAL_RAIL_URL}?type=single{get_locations(origin, destination)}{get_departure_time('leaving', 'departing', leaving_date, leaving_hour, leaving_min)}{get_passengers(adults, children)}{get_railcards(railcards)}{get_extra_time(extra_time)}"


def get_return_ticket_url(origin: str, destination: str, leaving_type: str,  leaving_date: str, leaving_hour: str, leaving_min: str, returning_type: str, return_date: str, return_hour: str, return_min: str, adults: int, children: int, railcards: dict[str, int], extra_time: int) -> str:
    """
    Constructs and returns the URL for a return train ticket based on the provided parameters.

    Args:
        origin (str): The origin station.
        destination (str): The destination station.
        leaving_type (str): The type of leaving train (e.g., 'fast', 'slow').
        leaving_date (str): The leaving date in the format 'YYYY-MM-DD'.
        leaving_hour (str): The leaving hour in the format 'HH'.
        leaving_min (str): The leaving minute in the format 'MM'.
        returning_type (str): The type of returning train (e.g., 'fast', 'slow').
        return_date (str): The return date in the format 'YYYY-MM-DD'.
        return_hour (str): The return hour in the format 'HH'.
        return_min (str): The return minute in the format 'MM'.
        adults (int): The number of adult passengers.
        children (int): The number of child passengers.
        railcards (dict[str, int]): A dictionary mapping railcard types to the number of railcards.
        extra_time (int): The extra time in minutes to add to the journey.

    Returns:
        str: The constructed URL for the return train ticket.

    """
    return f"{NATIONAL_RAIL_URL}?type=return{get_locations(origin, destination)}{get_departure_time('leaving', leaving_type, leaving_date, leaving_hour, leaving_min)}{get_departure_time('return', returning_type, return_date, return_hour, return_min)}{get_passengers(adults, children)}{get_railcards(railcards)}{get_extra_time(extra_time)}"
