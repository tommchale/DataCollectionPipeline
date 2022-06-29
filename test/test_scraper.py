import unittest
from unittest.mock import MagicMock
import os
import json

from web_scraper import LastManStandsScraper


class WebScraperTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper = LastManStandsScraper()
        (self.scraper).create_data_storage_folder()
        (self.scraper).load_and_accept_cookies()

        return super().setUp()

    def test_collect_scoreboard_bowling_ids_and_profile_image_link(self):

        (self.scraper).master_list = [{'PlayerName': 'Tom Arnold', 'UUID': '36499cc5-5918-4e61-9c63-c619e3a1acdf', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291385',
                                       'ImageLink': [], 'ScorecardBattingIds': [], 'ScorecardBowlingIds': [], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], 'Awards': {'MostValuablePlayer': 0, 'MostValuableBatter': 0, 'MostValuableBowler': 0}}]

        (self.scraper).collect_scoreboard_ids_and_profile_image_link()
        expected_dictionary = {'PlayerName': 'Tom Arnold', 'UUID': '36499cc5-5918-4e61-9c63-c619e3a1acdf', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291385', 'ImageLink': [
            'https://www.lastmanstands.com/images/player-silhouette.png'], 'ScorecardBattingIds': ['345139', '345125', '345123'], 'ScorecardBowlingIds': ['345139', '345125', '345123', '345121'], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], 'Awards': {'MostValuablePlayer': 0, 'MostValuableBatter': 0, 'MostValuableBowler': 0}}

        for player_dictionary in (self.scraper.master_list):

            self.assertEqual(
                expected_dictionary['ScorecardBowlingIds'], player_dictionary['ScorecardBowlingIds'])

            self.assertIsNotNone(player_dictionary['ImageLink'])

    def test_collect_scoreboard_batting_ids(self):

        (self.scraper).master_list = [{'PlayerName': 'Tom Arnold', 'UUID': '36499cc5-5918-4e61-9c63-c619e3a1acdf', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291385',
                                       'ImageLink': [], 'ScorecardBattingIds': [], 'ScorecardBowlingIds': [], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], 'Awards': {'MostValuablePlayer': 0, 'MostValuableBatter': 0, 'MostValuableBowler': 0}}]

        (self.scraper).collect_scoreboard_ids_and_profile_image_link()
        expected_dictionary = {'PlayerName': 'Tom Arnold', 'UUID': '36499cc5-5918-4e61-9c63-c619e3a1acdf', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291385', 'ImageLink': [
            'https://www.lastmanstands.com/images/player-silhouette.png'], 'ScorecardBattingIds': ['345139', '345125', '345123'], 'ScorecardBowlingIds': ['345139', '345125', '345123', '345121'], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], 'Awards': {'MostValuablePlayer': 0, 'MostValuableBatter': 0, 'MostValuableBowler': 0}}

        for player_dictionary in (self.scraper.master_list):

            self.assertEqual(
                expected_dictionary['ScorecardBattingIds'], player_dictionary['ScorecardBattingIds'])

    def test_retrieve_and_save_all_player_data_master_list(self):

        self.scraper.user_choice = "1"

        expected_dictionary = {"PlayerName": "Freddie Simon", "UUID": "62dafa1f-3fc9-428f-bce1-afba3c579853", "PlayerLink": "https://www.lastmanstands.com/cricket-player/t20?playerid=291389", "ImageLink": ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"], "ScorecardBattingIds": ["345123", "345121"], "ScorecardBowlingIds": ["345123", "345121"], "ScorecardBattingData": [
            {"How Out": "Not Out", "Runs": "112", "Balls": "34", "Fours": "7", "Sixes": "9", "SR": "329.41"}, {"How Out": "Caught", "Runs": "9", "Balls": "4", "Fours": "2", "Sixes": "0", "SR": "225.00"}], "ScorecardBowlingData": [{"Overs": "4.0", "Runs": "38", "Wickets": "1", "Maidens": "0", "Economy": "9.50"}, {"Overs": "2.1", "Runs": "11", "Wickets": "1", "Maidens": "0", "Economy": "5.24"}], "Awards": {"MostValuablePlayer": 1, "MostValuableBatter": 1, "MostValuableBowler": 0}}

        (self.scraper).master_list = [{'PlayerName': 'Freddie Simon', 'UUID': '62dafa1f-3fc9-428f-bce1-afba3c579853', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291389', 'ImageLink': ['https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717'],
                                       'ScorecardBattingIds': ['345123', '345121'], 'ScorecardBowlingIds': ['345123', '345121'], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], 'Awards': {'MostValuablePlayer': 0, 'MostValuableBatter': 0, 'MostValuableBowler': 0}}]

        (self.scraper).retrieve_and_save_all_player_data()

        self.sub_test_retrieve_data(expected_dictionary)
        self.sub_test_save_data(expected_dictionary)
        self.sub_test_image_exists()

    def sub_test_retrieve_data(self, expected_dictionary):

        for player_dictionary in (self.scraper.master_list):
            self.assertEqual(
                player_dictionary['ScorecardBattingData'], expected_dictionary['ScorecardBattingData'])
            self.assertEqual(
                player_dictionary['ScorecardBowlingData'], expected_dictionary['ScorecardBowlingData'])
            self.assertEqual(
                player_dictionary['Awards'], expected_dictionary['Awards'])

    def sub_test_save_data(self, expected_dictionary):

        os.chdir(self.scraper.player_dir)
        with open("data.json", "r") as fp:
            player_dictionary = json.load(fp)
        self.assertEqual(player_dictionary, expected_dictionary)
        fp.close()

    def sub_test_image_exists(self):

        os.chdir(self.scraper.image_dir)
        self.assertTrue(os.path.exists('0.jpg'))

    def test_get_batting_data(self):

        (self.scraper).master_list = [{'PlayerName': 'Freddie Simon', 'UUID': '62dafa1f-3fc9-428f-bce1-afba3c579853', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291389', 'ImageLink': ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"],
                                       "ScorecardBattingIds": ["345123", "345121"], "ScorecardBowlingIds": ["345123", "345121"], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}]

        expected_dictionary = {"PlayerName": "Freddie Simon", "UUID": "62dafa1f-3fc9-428f-bce1-afba3c579853", "PlayerLink": "https://www.lastmanstands.com/cricket-player/t20?playerid=291389", "ImageLink": ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"], "ScorecardBattingIds": ["345123", "345121"], "ScorecardBowlingIds": ["345123", "345121"], "ScorecardBattingData": [
            {"How Out": "Not Out", "Runs": "112", "Balls": "34", "Fours": "7", "Sixes": "9", "SR": "329.41"}, {"How Out": "Caught", "Runs": "9", "Balls": "4", "Fours": "2", "Sixes": "0", "SR": "225.00"}], "ScorecardBowlingData": [{"Overs": "4.0", "Runs": "38", "Wickets": "1", "Maidens": "0", "Economy": "9.50"}, {"Overs": "2.1", "Runs": "11", "Wickets": "1", "Maidens": "0", "Economy": "5.24"}], "Awards": {"MostValuablePlayer": 1, "MostValuableBatter": 1, "MostValuableBowler": 0}}

        for player_dictionary in self.scraper.master_list:

            for id in player_dictionary['ScorecardBattingIds']:

                ((self.scraper.driver)).get(
                    f"https://www.lastmanstands.com/leagues/scorecard/1st-innings?fixtureid={id}")

                self.scraper._get_scorecard_batting_data(player_dictionary)

                ((self.scraper.driver)).get(
                    f"https://www.lastmanstands.com/leagues/scorecard/2nd-innings?fixtureid={id}")

                self.scraper._get_scorecard_batting_data(player_dictionary)

            self.assertEqual(
                player_dictionary['ScorecardBattingData'], expected_dictionary['ScorecardBattingData'])

    def test_get_bowling_data(self):

        (self.scraper).master_list = [{'PlayerName': 'Freddie Simon', 'UUID': '62dafa1f-3fc9-428f-bce1-afba3c579853', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291389', 'ImageLink': ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"],
                                       "ScorecardBattingIds": ["345123", "345121"], "ScorecardBowlingIds": ["345123", "345121"], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}]

        expected_dictionary = {"PlayerName": "Freddie Simon", "UUID": "62dafa1f-3fc9-428f-bce1-afba3c579853", "PlayerLink": "https://www.lastmanstands.com/cricket-player/t20?playerid=291389", "ImageLink": ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"], "ScorecardBattingIds": ["345123", "345121"], "ScorecardBowlingIds": ["345123", "345121"], "ScorecardBattingData": [
            {"How Out": "Not Out", "Runs": "112", "Balls": "34", "Fours": "7", "Sixes": "9", "SR": "329.41"}, {"How Out": "Caught", "Runs": "9", "Balls": "4", "Fours": "2", "Sixes": "0", "SR": "225.00"}], "ScorecardBowlingData": [{"Overs": "4.0", "Runs": "38", "Wickets": "1", "Maidens": "0", "Economy": "9.50"}, {"Overs": "2.1", "Runs": "11", "Wickets": "1", "Maidens": "0", "Economy": "5.24"}], "Awards": {"MostValuablePlayer": 1, "MostValuableBatter": 1, "MostValuableBowler": 0}}

        for player_dictionary in self.scraper.master_list:

            for id in player_dictionary['ScorecardBowlingIds']:

                ((self.scraper.driver)).get(
                    f"https://www.lastmanstands.com/leagues/scorecard/1st-innings?fixtureid={id}")

                self.scraper._get_scorecard_bowling_data(player_dictionary)

                ((self.scraper.driver)).get(
                    f"https://www.lastmanstands.com/leagues/scorecard/2nd-innings?fixtureid={id}")

                self.scraper._get_scorecard_bowling_data(player_dictionary)

            self.assertEqual(
                player_dictionary['ScorecardBowlingData'], expected_dictionary['ScorecardBowlingData'])

    def test_get_mvp_mvb_award_data(self):

        (self.scraper).master_list = [{'PlayerName': 'Freddie Simon', 'UUID': '62dafa1f-3fc9-428f-bce1-afba3c579853', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291389', 'ImageLink': ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"],
                                       "ScorecardBattingIds": ["345123", "345121"], "ScorecardBowlingIds": ["345123", "345121"], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}]

        expected_dictionary = {"PlayerName": "Freddie Simon", "UUID": "62dafa1f-3fc9-428f-bce1-afba3c579853", "PlayerLink": "https://www.lastmanstands.com/cricket-player/t20?playerid=291389", "ImageLink": ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"], "ScorecardBattingIds": ["345123", "345121"], "ScorecardBowlingIds": ["345123", "345121"], "ScorecardBattingData": [
            {"How Out": "Not Out", "Runs": "112", "Balls": "34", "Fours": "7", "Sixes": "9", "SR": "329.41"}, {"How Out": "Caught", "Runs": "9", "Balls": "4", "Fours": "2", "Sixes": "0", "SR": "225.00"}], "ScorecardBowlingData": [{"Overs": "4.0", "Runs": "38", "Wickets": "1", "Maidens": "0", "Economy": "9.50"}, {"Overs": "2.1", "Runs": "11", "Wickets": "1", "Maidens": "0", "Economy": "5.24"}], "Awards": {"MostValuablePlayer": 1, "MostValuableBatter": 1, "MostValuableBowler": 0}}

        for player_dictionary in self.scraper.master_list:

            for id in player_dictionary['ScorecardBattingIds']:

                ((self.scraper.driver)).get(
                    f"https://www.lastmanstands.com/leagues/scorecard/stats?fixtureid={id}")

                self.scraper._get_most_valuable_player_award(player_dictionary)
                self.scraper._get_most_valuable_batter_award(player_dictionary)

            self.assertEqual(
                player_dictionary['Awards'], expected_dictionary['Awards'])

    def test_get_mvbowler_award_data(self):

        (self.scraper).master_list = [{'PlayerName': 'Freddie Simon', 'UUID': '62dafa1f-3fc9-428f-bce1-afba3c579853', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291389', 'ImageLink': ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"],
                                       "ScorecardBattingIds": ["345123", "345121"], "ScorecardBowlingIds": ["345123", "345121"], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}]

        expected_dictionary = {"PlayerName": "Freddie Simon", "UUID": "62dafa1f-3fc9-428f-bce1-afba3c579853", "PlayerLink": "https://www.lastmanstands.com/cricket-player/t20?playerid=291389", "ImageLink": ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"], "ScorecardBattingIds": ["345123", "345121"], "ScorecardBowlingIds": ["345123", "345121"], "ScorecardBattingData": [
            {"How Out": "Not Out", "Runs": "112", "Balls": "34", "Fours": "7", "Sixes": "9", "SR": "329.41"}, {"How Out": "Caught", "Runs": "9", "Balls": "4", "Fours": "2", "Sixes": "0", "SR": "225.00"}], "ScorecardBowlingData": [{"Overs": "4.0", "Runs": "38", "Wickets": "1", "Maidens": "0", "Economy": "9.50"}, {"Overs": "2.1", "Runs": "11", "Wickets": "1", "Maidens": "0", "Economy": "5.24"}], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}

        for player_dictionary in self.scraper.master_list:

            for id in player_dictionary['ScorecardBowlingIds']:

                ((self.scraper.driver)).get(
                    f"https://www.lastmanstands.com/leagues/scorecard/stats?fixtureid={id}")

                self.scraper._get_most_valuable_bowler_award(player_dictionary)

            self.assertEqual(
                player_dictionary['Awards'], expected_dictionary['Awards'])

    def tearDown(self) -> None:
        self.scraper.driver.quit()
        del self.scraper
        return super().tearDown()


unittest.main(argv=['first-arg-is-ignored'], exit=False)
