import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import services.national_rail.darwin_fetcher as darwin_fetcher
import services.national_rail.static_feed_fetcher as static_feed_fetcher
import services.stations_parser as stations_parser
import services.national_rail.token_generator as token_generator

if __name__ == "__main__":
    darwin_fetcher.retrieve_files_from_s3()
    static_feed_fetcher.extract_all_data(token_generator.get_auth_token())
    stations_parser.get_enhanced_stations()
