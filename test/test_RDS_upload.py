import unittest
from unittest.mock import MagicMock
import os
import json
from sqlalchemy import create_engine
import pandas as pd
import psycopg2

from web_scraper import LastManStandsScraper


class WebScraperTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper = LastManStandsScraper()
        return super().setUp()

    def test_data_frame_created(self):
        test_list_2 = [{'PlayerName': 'Freddie Simon', 'UUID': '5b857df2-b7e5-490c-bf96-23a261398afd', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291389', 'ImageLink': ['https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?646828954'], 'ScorecardIds': ['345123', '345121'], 'ScorecardBattingData': [{'How Out': 'Not Out', 'Runs': '112', 'Balls': '34', 'Fours': '7',
                                                                                                                                                                                                                                                                                                                                                                        'Sixes': '9', 'SR': '329.41'}, {'How Out': 'Caught', 'Runs': '9', 'Balls': '4', 'Fours': '2', 'Sixes': '0', 'SR': '225.00'}], 'ScorecardBowlingData': [{'Overs': '4.0', 'Runs': '38', 'Wickets': '1', 'Maidens': '0', 'Economy': '9.50'}, {'Overs': '2.1', 'Runs': '11', 'Wickets': '1', 'Maidens': '0', 'Economy': '5.24'}], 'Awards': {'MostValuablePlayer': 1, 'MostValuableBatter': 1, 'MostValuableBowler': 0}}]

        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        # Change it for your AWS endpoint
        ENDPOINT = 'aicoredb.cz91qpjes5tm.us-east-1.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = os.getenv("PASSWORD")
        PORT = 5432
        DATABASE = 'lms_db'

        engine = create_engine(
            f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        batting = pd.read_sql_table('combine_batting', engine)

        for player_dictionary in test_list_2:
            self.scraper._create_pandas_dataframes(player_dictionary)
            self.assertEqual(batting, (self.scraper.combine_batting))

    def tearDown(self) -> None:

        del self.scraper
        return super().tearDown()


unittest.main(argv=['first-arg-is-ignored'], exit=False)
