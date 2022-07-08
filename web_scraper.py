import time
import uuid
import sys
import os
import json


from email.mime import image
from typing import Container
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from decouple import config

import requests
import pandas as pd
from sqlalchemy import create_engine, inspect
import boto3


class LastManStandsScraper:
    ''' This class is used to represent a web scraper

    Attribues:
    URL (str): The url of website to be scraped
    master_list: List where scraped data to be stored
    test_list: List to substitute in for master list to test specific methods

    '''

    def __init__(self):
        '''
        See help(Date) for accurate signature
        '''
        self.URL = (
            "https://www.lastmanstands.com/team-profile/t20/?teamid=20327")
        self.master_list = []
        self.test_list = [{'PlayerName': 'Freddie Simon', 'UUID': '62dafa1f-3fc9-428f-bce1-afba3c579853', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291389', 'ImageLink': ["https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?190859717"],
                           'ScorecardIds': ['345121'], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}]
        self.test_list_2 = [{'PlayerName': 'Freddie Simon', 'UUID': '5b857df2-b7e5-490c-bf96-23a261398afd', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291389', 'ImageLink': ['https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?646828954'], 'ScorecardIds': ['345124', '345121'], 'ScorecardBattingData': [{'How Out': 'Terrible Bloke', 'Runs': '112', 'Balls': '34',
                                                                                                                                                                                                                                                                                                                                                                             'Fours': '7', 'Sixes': '9', 'SR': '329.41'}, {'How Out': 'Caught', 'Runs': '9', 'Balls': '4', 'Fours': '2', 'Sixes': '0', 'SR': '225.00'}], 'ScorecardBowlingData': [{'Overs': '4.0', 'Runs': '38', 'Wickets': '1', 'Maidens': '0', 'Economy': '9.50'}, {'Overs': '2.1', 'Runs': '11', 'Wickets': '1', 'Maidens': '0', 'Economy': '5.24'}], 'Awards': {'MostValuablePlayer': 1, 'MostValuableBatter': 1, 'MostValuableBowler': 0}}]
        self.user_choice = "1"

    def ask_local_or_online_storage(self):
        self.user_choice = input(
            ' \n Please press 1 for local storage, 2 for online (RDS - table, S3 - images) or 3 for both: \n')

    def create_data_storage_folder(self):
        '''save_data_collected

        1. Check and create raw_data folder for data storage
        Returns:
            create raw_data file

        Could this be static?
        '''
        # create raw_data if it doesn't exist
        if self.user_choice == "1" or self.user_choice == "3":
            path = os.getcwd()
            self.dir = os.path.join(path, "raw_data")
            # create folder for each player's data
            if not os.path.exists(self.dir):
                os.mkdir(self.dir)

    def load_and_accept_cookies(self) -> webdriver.Chrome:
        '''
        Open Last Man Stands Site and accept cookies
        Set driver to google Chrome Beta version sue to bug in driver v 103

        Returns
        -------
        self.driver: webdriver.Chrome

        '''
        options = Options()

        OS = sys.platform

        if OS == "darwin":
            options.binary_location = "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"
            options.headless = True

        if OS == "linux":
            options.binary_location = "/usr/bin/google-chrome-beta"
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('window-size=1920,1080')
            options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(chrome_options=options)
        (self.driver).get(self.URL)
        delay = 10
        try:
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="gdpr-popup-container"]')))
            print("Frame Ready!")
            accept_cookies_button = WebDriverWait(self.driver, delay).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="gdpr-accept-btn"]')))
            print("Accept Cookies Button Ready!")
            accept_cookies_button.click()dock
            time.sleep(1)
        except TimeoutException:
            print("Loading took too much time!")

    def get_player_list_container(self) -> Container:
        '''
        Returns a container containing all player information
        Parameters
        ----------
        driver: webdriver.Chrome
            The driver that contains information about the current page

        Returns
        -------
        player_list_container: a container within which all player information is contained
        '''

        # finds the container within which the full list of player links are contained

        batting_button = (self.driver).find_element(
            By.XPATH, '//*[@id="tp-sm-batting"]')
        batting_button.click()

        delay = 10
        try:
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="team-profile-2021-batting-stats"]')))
            player_link_container = self.driver.find_element(
                By.XPATH, '//*[@id="team-profile-2021-batting-stats"]')
            time.sleep(1)
        except TimeoutException:
            print("Loading took too much time!")
        player_link_body = player_link_container.find_element(
            By.XPATH, './tbody')
        self.player_list_container = player_link_body.find_elements(By.XPATH,
                                                                    './/tr')

    def create_master_list(self) -> list:
        '''_create_master_list creates template for the list where collected data will be stored
        Adds Player Name and Player Link to each unique entry.

        Returns:
            master_list: list with template for data storage
        '''

        for row in self.player_list_container:
            name = row.find_element(By.TAG_NAME, 'a').text
            a_tag = row.find_element(By.TAG_NAME, 'a')
            link = a_tag.get_attribute('href')
            player_dictionary = {"PlayerName": name, "UUID": str(
                uuid.uuid4()), "PlayerLink": link, 'ImageLink': [], "ScorecardBattingIds": [], "ScorecardBowlingIds": [], "ScorecardBattingData": [], "ScorecardBowlingData": [], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}
            self.master_list.append(player_dictionary)

    def collect_scoreboard_ids_and_profile_image_link(self):
        '''_collect_scoreboard_ids_and_profile_image_link

        1. Load each Player Link
        2. Collect player profile photo link
        3. Navigate to Scorecard Link
        4. Collect list of scorecard links and add to player dictionary

        '''
        # TODO: Need this for both batting and bowling scorecards -> done just need to test it!

        for player_dictionary in self.master_list:

            (self.driver).get(player_dictionary['PlayerLink'])

            ((self.driver).find_element(By.XPATH,
                                        '//*[@id="pp-sm-batting"]')).click()
            ((self.driver).find_element(By.XPATH,
                                        '//*[@id="batting-history-link-current"]')).click()

            self._get_player_profile_photo(player_dictionary)
            self._get_scoreboard_ids_batting(player_dictionary)
            ((self.driver).find_element(By.XPATH,
                                        '//*[@id="pp-sm-bowling"]')).click()
            ((self.driver).find_element(By.XPATH,
                                        '//*[@id="bowling-history-link-current"]')).click()
            self._get_scoreboard_ids_bowling(player_dictionary)

    def _get_player_profile_photo(self, player_dictionary):
        '''_get_player_profile_photo This function is to get link for player profile photo

        Once the link is location on the page, it is added to the player dictionary]

        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        '''
        image_container = (self.driver).find_element(
            By.XPATH, '//div[@id="player-profile-2020-top-block-pic"]')
        image_tag = image_container.find_element(By.TAG_NAME, 'img')
        image_link = image_tag.get_attribute('src')
        player_dictionary["ImageLink"].append(image_link)

    def _get_scoreboard_ids_batting(self, player_dictionary) -> list:
        '''_get_scoreboard_ids
        This function locates and stores id of games each player batted in.

        1. Wait for the player game table to load.
        2. Once loaded locate and create a list of scoreboard links on that page.
        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        Returns:
            a list of scoreboard links
        '''
        scorecard_div = (self.driver).find_element(
            By.XPATH, '//div[@id="pp-batting-history-container-current"]')
        delay = 10
        try:
            WebDriverWait(scorecard_div, delay).until(EC.presence_of_element_located(
                (By.XPATH, './table[@class="rank-table"]')))
            scorecard_container = scorecard_div.find_element(
                By.XPATH, './table[@class="rank-table"]')
            time.sleep(1)
        except TimeoutException:
            print("Loading took too much time!")
            scorecard_container = None

        if scorecard_container is not None:
            scorecard_container_body = scorecard_container.find_element(
                By.XPATH, './tbody')
            scorecard_container_list = scorecard_container_body.find_elements(
                By.XPATH, './tr')
            self.scorecard_batting_id_list = []

            for row in scorecard_container_list:
                a_tag = row.find_element(By.TAG_NAME, 'a')
                link = a_tag.get_attribute('href')
                fixture_id = (link.split("="))[1]
                # 0 is used for blank summary scorecard ids and therefore not required to be collected in scraper
                if fixture_id == "0":
                    continue
                else:
                    self.scorecard_batting_id_list.append(fixture_id)

        player_dictionary['ScorecardBattingIds'] = self.scorecard_batting_id_list

    def _get_scoreboard_ids_bowling(self, player_dictionary) -> list:
        '''_get_scoreboard_ids
        This function locates and stores id of games each player is bowled in.

        1. Wait for the player game table to load.
        2. Once loaded locate and create a list of scoreboard links on that page.
        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        Returns:
            a list of scoreboard links
        '''
        scorecard_div = (self.driver).find_element(
            By.XPATH, '//div[@id="pp-bowling-history-container-current"]')
        delay = 10
        try:
            WebDriverWait(scorecard_div, delay).until(EC.presence_of_element_located(
                (By.XPATH, './table[@class="rank-table"]')))
            scorecard_container = scorecard_div.find_element(
                By.XPATH, './table[@class="rank-table"]')
            time.sleep(1)
        except TimeoutException:
            print("Loading took too much time!")
            scorecard_container = None

        if scorecard_container is not None:
            scorecard_container_body = scorecard_container.find_element(
                By.XPATH, './tbody')
            scorecard_container_list = scorecard_container_body.find_elements(
                By.XPATH, './tr')
            self.scorecard_bowling_id_list = []

            for row in scorecard_container_list:
                a_tag = row.find_element(By.TAG_NAME, 'a')
                link = a_tag.get_attribute('href')
                fixture_id = (link.split("="))[1]
                # 0 is used for blank summary scorecard ids and therefore not required to be collected in scraper
                if fixture_id == "0":
                    continue
                else:
                    self.scorecard_bowling_id_list.append(fixture_id)

            player_dictionary['ScorecardBowlingIds'] = self.scorecard_bowling_id_list

    def retrieve_and_save_all_player_data(self):
        '''
        This method locates, pulls and save fixture information relevant to each player.

        1. Load each relevant page for each fixture id.
        2. Run collection methods to gather batter, bowler and award data.
        3. Run method to programatically store player data.
        4. Following removal of pre-uploaded data:
            i. only collect data is scorecard ids exist
            ii. only create and upload dataframes if scorecard data exists

        '''

        for player_dictionary in self.master_list:
            if self.user_choice == "2" or self.user_choice == "3":
                self._remove_scorecard_id_if_exists_in_RDS(player_dictionary)

            if player_dictionary['ScorecardBattingIds']:
                for id in player_dictionary['ScorecardBattingIds']:

                    ((self.driver)).get(
                        f"https://www.lastmanstands.com/leagues/scorecard/1st-innings?fixtureid={id}")

                    self._get_scorecard_batting_data(player_dictionary)

                    ((self.driver)).get(
                        f"https://www.lastmanstands.com/leagues/scorecard/2nd-innings?fixtureid={id}")

                    self._get_scorecard_batting_data(player_dictionary)

                    ((self.driver)).get(
                        f"https://www.lastmanstands.com/leagues/scorecard/stats?fixtureid={id}")

                    self._get_most_valuable_player_award(
                        player_dictionary)
                    self._get_most_valuable_batter_award(
                        player_dictionary)
            if player_dictionary['ScorecardBowlingIds']:
                for id in player_dictionary['ScorecardBowlingIds']:

                    ((self.driver)).get(
                        f"https://www.lastmanstands.com/leagues/scorecard/1st-innings?fixtureid={id}")

                    self._get_scorecard_bowling_data(player_dictionary)

                    ((self.driver)).get(
                        f"https://www.lastmanstands.com/leagues/scorecard/2nd-innings?fixtureid={id}")

                    self._get_scorecard_bowling_data(player_dictionary)

                    ((self.driver)).get(
                        f"https://www.lastmanstands.com/leagues/scorecard/stats?fixtureid={id}")

                    self._get_most_valuable_bowler_award(player_dictionary)

            if player_dictionary['ScorecardBattingIds'] or player_dictionary['ScorecardBowlingIds']:
                if self.user_choice == "1" or self.user_choice == "3":
                    self._create_player_directory_structure(player_dictionary)
                    self._save_player_dictionary_to_file(player_dictionary)
                    self._download_and_save_images(player_dictionary)
                if self.user_choice == "2" or self.user_choice == "3":
                    self._create_pandas_dataframes(player_dictionary)
                    self._upload_dataframes_to_rds()
                    self._upload_images_to_s3_bucket(player_dictionary)

    def _get_scorecard_batting_data(self, player_dictionary):
        '''_get_scorecard_player_data Locate and add batting and bowling data to each player dictionary

        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        '''

        # Create tables for battings data and bowling data as information stored in different format for each one
        scorecard_data_table_list = (self.driver).find_elements(
            By.XPATH, './/table')

        batting_data_body = scorecard_data_table_list[0].find_element(
            By.XPATH, './tbody')
        batting_data_list = batting_data_body.find_elements(
            By.XPATH, './tr')

        # If name exists in batting data - find data

        for row in batting_data_list:
            try:
                player_name = row.find_element(By.TAG_NAME, 'a').text
                if player_name == player_dictionary["PlayerName"]:
                    print(player_name)
                    data_list = row.find_elements(By.XPATH, './td')
                    batting_dictionary = {"How Out": (data_list[0].text).split("\n")[1], "Runs": data_list[1].text, "Balls": data_list[2].text,
                                          "Fours": data_list[3].text, "Sixes": data_list[4].text, "SR": data_list[5].text}
                    player_dictionary["ScorecardBattingData"].append(
                        batting_dictionary)
            except NoSuchElementException:
                continue

    def _get_scorecard_bowling_data(self, player_dictionary):
        '''_get_scorecard_bowling_data 
        Locate and add bowling data to each player dictionary

        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        '''
        # Create tables for battings data and bowling data as information stored in different format for each one
        scorecard_data_table_list = (
            self.driver).find_elements(By.XPATH, './/table')
        bowling_data_body = scorecard_data_table_list[1].find_element(
            By.XPATH, './tbody')
        bowling_data_list = bowling_data_body.find_elements(
            By.XPATH, './tr')

        # If name exists in bowling data - find data

        for row in bowling_data_list:
            try:
                player_name = row.find_element(By.TAG_NAME, 'a').text
                if player_name == player_dictionary["PlayerName"]:
                    print(player_name)
                    data_list = row.find_elements(By.XPATH, './td')
                    bowling_dictionary = {"Overs": data_list[1].text, "Runs": data_list[2].text,
                                          "Wickets": data_list[3].text, "Maidens": data_list[4].text, "Economy": data_list[5].text}
                    player_dictionary["ScorecardBowlingData"].append(
                        bowling_dictionary)
            except NoSuchElementException:
                continue

    def _get_player_awards(self, player_dictionary):
        '''_get_player_awards 
        Run methods to collect information on player awards

        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        '''

        self._get_most_valuable_player_award(player_dictionary)
        self._get_most_valuable_batter_award(player_dictionary)
        self._get_most_valuable_bowler_award(player_dictionary)

    def _get_most_valuable_player_award(self, player_dictionary):
        '''_get_most_valuable_player_award 
        Method to find if MVP award won by player

        If award won, add value to count of awards
        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        '''
        mvp_container = (self.driver).find_element(
            By.XPATH, '//div[@id="scorecard-2020-stats-block-mvp"]')
        mvp_list = mvp_container.find_elements(By.XPATH, './div')
        for item in mvp_list:
            try:
                player_name = item.text
                if player_name == player_dictionary["PlayerName"]:
                    (player_dictionary["Awards"])["MostValuablePlayer"] += 1
                    break
                else:
                    continue

            except NoSuchElementException:
                continue

    def _get_most_valuable_batter_award(self, player_dictionary):
        '''_get_most_valuable_batter_award 
        method to find if Most Valuable Batter award won

        If award won, add value to count of awards
        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        '''
        mvb_container = (self.driver).find_element(
            By.XPATH, '//div[@id="scorecard-2020-stats-block-mvbat"]')
        mvb_list = mvb_container.find_elements(By.XPATH, './div')
        for item in mvb_list:
            try:
                player_name = item.text
                if player_name == player_dictionary["PlayerName"]:
                    (player_dictionary["Awards"])["MostValuableBatter"] += 1
                    break
                else:
                    continue

            except NoSuchElementException:
                continue

    def _get_most_valuable_bowler_award(self, player_dictionary):
        '''_get_most_valuable_bowler_award 
        Method to find if Most Valuable Bowler award won

        If award won, add value to count of awards
        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        '''
        mvb_container = (self.driver).find_element(
            By.XPATH, '//div[@id="scorecard-2020-stats-block-mvbowl"]')
        mvb_list = mvb_container.find_elements(By.XPATH, './div')
        for item in mvb_list:
            try:
                player_name = item.text
                if player_name == player_dictionary["PlayerName"]:
                    (player_dictionary["Awards"])["MostValuableBowler"] += 1
                    break
                else:
                    continue

            except NoSuchElementException:
                continue

    def _create_player_directory_structure(self, player_dictionary):
        '''_create_player_directory_structure 
        Method to create player directory structure for each player

        1. Create player folder if does not exist
        2. Create image folder if does not exist
        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        Returns:
            Directory in raw_data folder of "PlayerName" -> "Images"
        '''

        # create folder for each player id
        self.player_dir = os.path.join(
            self.dir, player_dictionary["PlayerName"])
        if not os.path.exists(self.player_dir):
            os.mkdir(self.player_dir)
        # create image folder
        self.image_dir = os.path.join(self.player_dir, "images")
        if not os.path.exists(self.image_dir):
            os.mkdir(self.image_dir)

    def _save_player_dictionary_to_file(self, player_dictionary) -> json:
        '''_save_player_dictionary_to_file 
        This method saves each player dictionary in the player directory

        Method desgined to be called programatically as data collected for each player

        1. Change file path to player directory path
        2. Dump player dictionary in data.json file
        Arguments:
            player_dictionary -- _description_
        '''
        os.chdir(self.player_dir)
        with open("data.json", "w") as fp:
            json.dump(player_dictionary, fp)

    def _download_and_save_images(self, player_dictionary) -> image:
        '''_download_images 
        This method downloads and saves each player profile photo

        Each image is saved to the images file
        Returns:
            JPG file
        '''
        os.chdir(self.image_dir)
        index = 0
        for link in player_dictionary["ImageLink"]:
            img_data = requests.get(link).content
            with open(f"{index}.jpg", 'wb') as handler:
                handler.write(img_data)
            index += 1

    def _create_pandas_dataframes(self, player_dictionary):
        '''_create_pandas_dataframes 
        This method converts data collected in dictionaries into pandas dataframes

        1. Create required dataframes from the data
        2. Rename columns into SQL friendly format
        3. Set dtype to relevant d types
        4. Option to not create a datframe if player has no batting/bowling data.

        Arguments:
            player_dictionary -- _description_
        '''

        # create player, uuid, scorecarddata frames

        self.players = pd.DataFrame(player_dictionary, columns=[
            'PlayerName', 'UUID', 'PlayerLink'], index=[0])
        uuid = pd.DataFrame(player_dictionary, columns=['UUID'], index=[0])
        batting_scorecards = pd.DataFrame(player_dictionary, columns=[
            'ScorecardBattingIds', 'UUID'])
        bowling_scorecards = pd.DataFrame(player_dictionary, columns=[
            'ScorecardBowlingIds', 'UUID'])

        # rename player, scorecard and uuid df

        self.players = self.players.rename(
            columns={"PlayerName": "name", "UUID": "uuid", "PlayerLink": "lms_profile_link"})
        batting_scorecards = batting_scorecards.rename(
            columns={"ScorecardBattingIds": "scorecard_batting_id", "UUID": "uuid"})
        bowling_scorecards = bowling_scorecards.rename(
            columns={"ScorecardBowlingIds": "scorecard_bowling_id", "UUID": "uuid"})
        uuid = uuid.rename(columns={"UUID": "uuid"})

        # set players and scorecards dtypes

        self.players['name'] = self.players['name'].astype('string')
        self.players['uuid'] = self.players['uuid'].astype('string')
        self.players['lms_profile_link'] = self.players['lms_profile_link'].astype(
            'string')

        batting_scorecards['scorecard_batting_id'] = batting_scorecards['scorecard_batting_id'].astype(
            'int64')
        batting_scorecards['uuid'] = batting_scorecards['uuid'].astype(
            'string')

        bowling_scorecards['scorecard_bowling_id'] = bowling_scorecards['scorecard_bowling_id'].astype(
            'int64')
        bowling_scorecards['uuid'] = bowling_scorecards['uuid'].astype(
            'string')

        # create, rename and merge awards with uuid
        awards = pd.DataFrame(player_dictionary['Awards'], index=[0])
        awards = awards.rename(columns={"MostValuablePlayer": "most_valuable_player",
                               "MostValuableBatter": "most_valuable_batter", "MostValuableBowler": "most_valuable_bowler"})
        self.combine_awards = pd.merge(
            uuid, awards, left_index=True, right_index=True)
        self.combine_awards['uuid'] = self.combine_awards['uuid'].astype(
            'string')

        # as some players may not have batting data
        if player_dictionary['ScorecardBattingData']:
            batting_data = pd.DataFrame(
                player_dictionary['ScorecardBattingData'])
            batting_data = batting_data.rename(columns={"How Out": "how_out", "Runs": "runs_scored",
                                                        "Balls": "balls_faced", "Fours": "fours", "Sixes": "sixes", "SR": "strike_rate"})
            self.combine_batting = pd.merge(
                batting_scorecards, batting_data, left_index=True, right_index=True)
            self.combine_batting['how_out'] = self.combine_batting['how_out'].astype(
                'category')
            self.combine_batting['runs_scored'] = self.combine_batting['runs_scored'].astype(
                'int64')
            self.combine_batting['balls_faced'] = self.combine_batting['balls_faced'].astype(
                'int64')
            self.combine_batting['fours'] = self.combine_batting['fours'].astype(
                'int64')
            self.combine_batting['sixes'] = self.combine_batting['sixes'].astype(
                'int64')
            self.combine_batting['strike_rate'] = self.combine_batting['strike_rate'].astype(
                'float64')
        elif not player_dictionary['ScorecardBattingData']:
            self.combine_batting = None

        # some player may not have bowling data
        if player_dictionary['ScorecardBowlingData']:
            bowling_data = pd.DataFrame(
                player_dictionary['ScorecardBowlingData'])
            bowling_data = bowling_data.rename(columns={
                "Overs": "overs", "Runs": "runs_conceeded", "Wickets": "wickets", "Maidens": "maidens", "Economy": "economy"})
            self.combine_bowling = pd.merge(
                bowling_scorecards, bowling_data, left_index=True, right_index=True)
            self.combine_bowling['overs'] = self.combine_bowling['overs'].astype(
                'float64')
            self.combine_bowling['runs_conceeded'] = self.combine_bowling['runs_conceeded'].astype(
                'int64')
            self.combine_bowling['wickets'] = self.combine_bowling['wickets'].astype(
                'int64')
            self.combine_bowling['maidens'] = self.combine_bowling['maidens'].astype(
                'int64')
            self.combine_bowling['economy'] = self.combine_bowling['economy'].astype(
                'float64')
        # reset df in case no data present
        elif not player_dictionary['ScorecardBowlingData']:
            self.combine_bowling = None

    def _connect_to_RDS(self) -> create_engine:
        '''_connect_to_RDS 
        Method to craete connection to RDS database using sqlalchemy

        Returns:
            self.engine - connection

        '''
        DATABASE_TYPE = config('RDS_DATABASE_TYPE')
        DBAPI = config('RDS_DBAPI')
        ENDPOINT = config('RDS_ENDPOINT')
        USER = config('RDS_USER')
        PASSWORD = config('RDS_DATABASE_PASSWORD')
        PORT = 5432
        DATABASE = config('RDS_DATABASE')

        self.engine = create_engine(
            f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")

    def _upload_dataframes_to_rds(self):
        '''_upload_dataframes_to_rds 
        If dataframe exists, append it to SQL database.
        '''

        self._connect_to_RDS()
        self.players.to_sql('players', self.engine, if_exists='append')
        self.combine_awards.to_sql(
            'awards', self.engine, if_exists='append')
        if self.combine_batting is not None:
            self.combine_batting.to_sql(
                'batting', self.engine, if_exists='append')
        if self.combine_bowling is not None:
            self.combine_bowling.to_sql(
                'bowling', self.engine, if_exists='append')

    def _upload_images_to_s3_bucket(self, player_dictionary):
        '''_upload_images_to_s3_bucket 
        Method to upload collected images to S3 bucket

        1. Connect to S3 bucket using boto3
        2. Check if folder exists
        3. If folder exists do nothing, if not upload image file


        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        '''

        s3_client = boto3.client('s3')
        bucket_name = config('S3_BUCKET_NAME')
        folder_name = f"{player_dictionary['PlayerName']}"
        result = s3_client.list_objects(Bucket=bucket_name, Prefix=folder_name)
        if 'Contents' not in result:
            s3_client.put_object(Bucket=bucket_name, Key=(folder_name+'/'))
            index = 0
            for link in player_dictionary['ImageLink']:
                img_data = requests.get(link).content
                s3_client.put_object(Body=img_data, Bucket=bucket_name, Key=(
                    f"{folder_name}/{index}.jpg"))
                index += 1

    def _remove_scorecard_id_if_exists_in_RDS(self, player_dictionary):
        '''_remove_scorecard_id_if_exists_in_RDS 
        Method to prevent recraping of the same data

        1. Connect to RDS database using sqlalchemy
        2. Run sql query asking to return all scorecard id of all batting fixtures
        3. Convert pandas dataframe into string format
        4. Convert scorecard id column into a list
        5. Set the scorecard id list of the player dictinoary to the difference of two sets of the collected values

        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        '''

        self._connect_to_RDS()
        inspector = inspect(self.engine)
        if inspector.has_table('batting'):
            batting_query = f"(SELECT batting.scorecard_batting_id, players.name FROM batting JOIN players ON players.uuid = batting.uuid WHERE players.name = '{player_dictionary['PlayerName']}' GROUP BY batting.scorecard_batting_id, players.name)"
            batting_scorecard_id_table = pd.read_sql_query(
                batting_query, self.engine)
            batting_scorecard_id_table['scorecard_batting_id'] = batting_scorecard_id_table['scorecard_batting_id'].astype(
                'string')
            scraped_batting_fixture_list = batting_scorecard_id_table['scorecard_batting_id'].values.tolist(
            )
            player_dictionary['ScorecardBattingIds'] = list(
                set(player_dictionary['ScorecardBattingIds']) - set(scraped_batting_fixture_list))
        if inspector.has_table('bowling'):
            bowling_query = f"(SELECT bowling.scorecard_bowling_id, players.name FROM bowling JOIN players ON players.uuid = bowling.uuid WHERE players.name = '{player_dictionary['PlayerName']}' GROUP BY bowling.scorecard_bowling_id, players.name)"
            bowling_scorecard_id_table = pd.read_sql_query(
                bowling_query, self.engine)
            bowling_scorecard_id_table['scorecard_bowling_id'] = bowling_scorecard_id_table['scorecard_bowling_id'].astype(
                'string')
            scraped_bowling_fixture_list = bowling_scorecard_id_table['scorecard_bowling_id'].values.tolist(
            )
            player_dictionary['ScorecardBowlingIds'] = list(
                set(player_dictionary['ScorecardBowlingIds']) - set(scraped_bowling_fixture_list))

    def run_crawler(self):
        '''run_crawler 
        Calling method to call other methods.
        '''
        self.ask_local_or_online_storage()
        self.create_data_storage_folder()
        self.load_and_accept_cookies()
        self.get_player_list_container()
        self.create_master_list()
        self.collect_scoreboard_ids_and_profile_image_link()
        self.retrieve_and_save_all_player_data()


def run():

    crawler = LastManStandsScraper()
    crawler.run_crawler()


if __name__ == "__main__":

    run()
