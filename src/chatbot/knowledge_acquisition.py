import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import services.national_rail.darwin_fetcher as darwin_fetcher
import services.national_rail.static_feed_fetcher as static_feed_fetcher
import services.stations_parser as stations_parser

if __name__ == "__main__":
    darwin_fetcher.retrieve_files_from_s3()
    static_feed_fetcher.extract_all_data()
    stations_parser.get_enhanced_stations()
