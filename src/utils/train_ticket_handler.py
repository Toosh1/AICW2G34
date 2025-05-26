NATIONAL_RAIL_URL: str = 'https://www.nationalrail.co.uk/journey-planner/'


def get_locations(origin: str, destination: str) -> str:
    """
    Constructs a query string for the origin and destination locations using CRS codes.

    :param origin: The CRS code of the origin station.
    :param destination: The CRS code of the destination station.
    :returns: A query string in the format "&origin={origin}&destination={destination}".
    """
    return f"&origin={origin}&destination={destination}"

def get_departure_time(method: str, type: str, date: str, hour: str, min: str) -> str:
    """
    Constructs a query string for the departure or return time.

    :param method: Specifies whether the time is for 'leaving' or 'return'.
    :param type: The type of departure or return (e.g., 'departing', 'arriving').
    :param date: The date in the format 'DDMMYY'.
    :param hour: The hour in the format 'HH'.
    :param min: The minute in the format 'MM'.
    :returns: A query string in the format "&{method}Type={type}&{method}Date={date}&{method}Hour={hour}&{method}Min={min}".
    """
    return f"&{method}Type={type}&{method}Date={date}&{method}Hour={hour}&{method}Min={min}"


def get_passengers(adults: int, children: int) -> str:
    """
    Constructs a query string for the number of passengers.

    :param adults: The number of adult passengers.
    :param children: The number of child passengers.
    :returns: A query string in the format "&adults={adults}&children={children}".
    """
    return f"&adults={adults}&children={children}"

def get_single_ticket_url(origin: str, destination: str, leaving_type: str, leaving_date: str, leaving_hour: str, leaving_min: str, adults: int = 1) -> str:
    """
    Constructs a URL for a single train ticket.

    :param origin: The CRS code of the origin station.
    :param destination: The CRS code of the destination station.
    :param leaving_date: The departure date in the format 'DDMMYY'.
    :param leaving_hour: The departure hour in the format 'HH'.
    :param leaving_min: The departure minute in the format 'MM'.
    :param adults: The number of adult passengers (default is 1).
    :returns: The constructed URL for the single train ticket.
    """
    return f"{NATIONAL_RAIL_URL}?type=single{get_locations(origin, destination)}{get_departure_time('leaving', leaving_type, leaving_date, leaving_hour, leaving_min)}&adults={adults}"

def get_return_ticket_url(origin: str, destination: str, leaving_type: str, leaving_date: str, leaving_hour: str, leaving_min: str, returning_type: str, return_date: str, return_hour: str, return_min: str, adults: int = 1) -> str:
    """
    Constructs a URL for a return train ticket.

    :param origin: The CRS code of the origin station.
    :param destination: The CRS code of the destination station.
    :param leaving_type: The type of departure (e.g., 'departing', 'arriving').
    :param leaving_date: The departure date in the format 'DDMMYY'.
    :param leaving_hour: The departure hour in the format 'HH'.
    :param leaving_min: The departure minute in the format 'MM'.
    :param returning_type: The type of return (e.g., 'departing', 'arriving').
    :param return_date: The return date in the format 'DDMMYY'.
    :param return_hour: The return hour in the format 'HH'.
    :param return_min: The return minute in the format 'MM'.
    :param adults: The number of adult passengers (default is 1).
    :returns: The constructed URL for the return train ticket.
    """
    return f"{NATIONAL_RAIL_URL}?type=return{get_locations(origin, destination)}{get_departure_time('leaving', leaving_type, leaving_date, leaving_hour, leaving_min)}{get_departure_time('return', returning_type, return_date, return_hour, return_min)}&adults={adults}"

if __name__ == "__main__":
    url = get_single_ticket_url("MDE", "NRW", "departing", "300525", "10", "30")
    print(url)