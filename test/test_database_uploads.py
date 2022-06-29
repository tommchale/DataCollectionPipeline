import unittest
from unittest.mock import MagicMock
import os
import json
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
from decouple import config
import boto3
from web_scraper import LastManStandsScraper


class WebScraperTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper = LastManStandsScraper()
        self.test_list_2 = [{"PlayerName": "Tom Arnold", "UUID": "ea545ce0-0bb5-4cec-8ea4-0a039d0f2983", "PlayerLink": "https://www.lastmanstands.com/cricket-player/t20?playerid=291385", "ImageLink": ["https://www.lastmanstands.com/images/player-silhouette.png"], "ScorecardBattingIds": ["345123"], "ScorecardBowlingIds": ["345121"],
                             "ScorecardBattingData": [{"How Out": "Not Out", "Runs": "7", "Balls": "9", "Fours": "1", "Sixes": "0", "SR": "77.78"}], "ScorecardBowlingData": [{"Overs": "3.0", "Runs": "30", "Wickets": "1", "Maidens": "0", "Economy": "10.00"}], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}]

        self.test_list_extra_id = [{"PlayerName": "Freddie Simon", "UUID": "e2cd3758-f23a-4e9a-9666-77e98ff06d28", "PlayerLink": "https://www.lastmanstands.com/cricket-player/t20?playerid=291389", "ImageLink": ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?1681425044"],
                                    "ScorecardBattingIds": ["345139", "345136", "345123", "345121", '345169'], "ScorecardBowlingIds": ["345139", "345136", "345123", "345121"], "ScorecardBattingData": [], "ScorecardBowlingData": [], "Awards": {"MostValuablePlayer": 1, "MostValuableBatter": 1, "MostValuableBowler": 0}}]
        return super().setUp()

    @unittest.skip
    def test_data_frame_created(self):

        expected_total_runs_scored = 7

        DATABASE_TYPE = config('RDS_DATABASE_TYPE')
        DBAPI = config('RDS_DBAPI')
        ENDPOINT = config('RDS_ENDPOINT')
        USER = config('RDS_USER')
        PASSWORD = config('RDS_DATABASE_PASSWORD')
        PORT = 5432
        DATABASE = config('RDS_DATABASE')

        engine = create_engine(
            f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")

        for player_dictionary in self.test_list_2:
            self.scraper._create_pandas_dataframes(player_dictionary)
            self.scraper._upload_dataframes_to_rds()
            batting = pd.read_sql_query(
                '''SELECT * FROM batting JOIN players ON players.uuid = batting.uuid WHERE players.name = 'Tom Arnold' ''', engine)
            self.assertEqual(batting['runs_scored'].sum(),
                             expected_total_runs_scored)

    @unittest.skip
    def test_s3_upload(self):

        s3_client = boto3.client('s3')

        bucket_name = config('S3_BUCKET_NAME')
        for player_dictionary in self.test_list_2:
            folder_name = f"{player_dictionary['PlayerName']}"
            result = s3_client.list_objects(
                Bucket=bucket_name, Prefix=folder_name)
            if 'Contents' in result:
                file_created = True
            else:
                file_created = False
        self.assertTrue(file_created)

    def test_remove_id_if_exists_in_RDS(self):

        self.scraper.master_list = self.test_list_extra_id

        for player_dictionary in self.scraper.master_list:
            self.scraper._remove_scorecard_id_if_exists_in_RDS(
                player_dictionary)

            self.assertEqual(
                player_dictionary['ScorecardBattingIds'], ['345169'])
            self.assertEqual(player_dictionary['ScorecardBowlingIds'], [])

    def tearDown(self) -> None:

        del self.scraper
        return super().tearDown()


unittest.main(argv=['first-arg-is-ignored'], exit=False)
