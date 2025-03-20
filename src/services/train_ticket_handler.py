temp = 'https://www.nationalrail.co.uk/journey-planner/?type=single&origin=MDE&destination=NRW&leavingType=departing&leavingDate=180325&leavingHour=21&leavingMin=45&adults=1&extraTime=0#O'

foo = 'https://www.nationalrail.co.uk/journey-planner/?type=return&origin=SOU&destination=NOT&leavingType=departing&leavingDate=180325&leavingHour=22&leavingMin=00&returnType=departing&returnDate=190325&returnHour=00&returnMin=00&adults=4&children=3&railcards=HOW%7C1&extraTime=0#O'

# https://www.nationalrail.co.uk/journey-planner/?type=return&origin=SOU&destination=NOT&leavingType=departing&leavingDate=180325&leavingHour=22&leavingMin=00&returnType=departing&returnDate=190325&returnHour=00&returnMin=00&adults=4&children=3&railcards=HOW%7C3&railcards=HMF%7C4&extraTime=0#O

def get_single_ticket_url(origin, destination, date, hour, minute):
    return f'https://www.nationalrail.co.uk/journey-planner/?type=single&origin={origin}&destination={destination}&leavingType=departing&leavingDate={date}&leavingHour={hour}&leavingMin={minute}&adults=1&children={children}&railcards={railcard}&extraTime=0#O'