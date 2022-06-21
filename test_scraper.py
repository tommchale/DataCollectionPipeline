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

    def test_collect_scoreboard_ids_and_profile_image_link(self):

        (self.scraper).master_list = [{'PlayerName': 'Freddie Simon', 'UUID': '62dafa1f-3fc9-428f-bce1-afba3c579853', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291389', 'ImageLink': [],
                                      'ScorecardIds': [], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}]
        (self.scraper).collect_scoreboard_ids_and_profile_image_link()
        expected_dictionary = {'PlayerName': 'Freddie Simon', 'UUID': '62dafa1f-3fc9-428f-bce1-afba3c579853', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291389', 'ImageLink': ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"],
                               'ScorecardIds': ["345123", "345121"], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}

        for player_dictionary in (self.scraper.master_list):

            self.assertEqual(
                expected_dictionary['ScorecardIds'], player_dictionary['ScorecardIds'])
            self.assertIsNotNone(player_dictionary['ImageLink'])

    def test_retrieve_and_save_all_player_data_master_list(self):

        expected_dictionary = {"PlayerName": "Freddie Simon", "UUID": "62dafa1f-3fc9-428f-bce1-afba3c579853", "PlayerLink": "https://www.lastmanstands.com/cricket-player/t20?playerid=291389", "ImageLink": ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"], "ScorecardIds": ["345123", "345121"], "ScorecardBattingData": [
            {"How Out": "Not Out", "Runs": "112", "Balls": "34", "Fours": "7", "Sixes": "9", "SR": "329.41"}, {"How Out": "Caught", "Runs": "9", "Balls": "4", "Fours": "2", "Sixes": "0", "SR": "225.00"}], "ScorecardBowlingData": [{"Overs": "4.0", "Runs": "38", "Wickets": "1", "Maidens": "0", "Economy": "9.50"}, {"Overs": "2.1", "Runs": "11", "Wickets": "1", "Maidens": "0", "Economy": "5.24"}], "Awards": {"MostValuablePlayer": 1, "MostValuableBatter": 1, "MostValuableBowler": 0}}

        (self.scraper).master_list = [{'PlayerName': 'Freddie Simon', 'UUID': '62dafa1f-3fc9-428f-bce1-afba3c579853', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291389', 'ImageLink': ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"],
                                       'ScorecardIds': ["345123", "345121"], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}]

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

    def tearDown(self) -> None:
        self.scraper.driver.quit()
        del self.scraper
        return super().tearDown()


unittest.main(argv=['first-arg-is-ignored'], exit=False)
