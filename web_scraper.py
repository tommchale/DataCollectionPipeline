from email.mime import image
from typing import Container
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import time
import uuid
import os
import json
import requests
import pandas as pd
from sqlalchemy import create_engine


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
                           'ScorecardIds': [], 'ScorecardBattingData': [], 'ScorecardBowlingData': [], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}]
        self.test_list_2 = [{'PlayerName': 'Freddie Simon', 'UUID': '5b857df2-b7e5-490c-bf96-23a261398afd', 'PlayerLink': 'https://www.lastmanstands.com/cricket-player/t20?playerid=291389', 'ImageLink': ['https://admin.lastmanstands.com/SpawtzApp/Images/User/291389_UserProfileImage.jpeg?646828954'], 'ScorecardIds': ['345124', '345121'], 'ScorecardBattingData': [{'How Out': 'Terrible Bloke', 'Runs': '112', 'Balls': '34',
                                                                                                                                                                                                                                                                                                                                                                             'Fours': '7', 'Sixes': '9', 'SR': '329.41'}, {'How Out': 'Caught', 'Runs': '9', 'Balls': '4', 'Fours': '2', 'Sixes': '0', 'SR': '225.00'}], 'ScorecardBowlingData': [{'Overs': '4.0', 'Runs': '38', 'Wickets': '1', 'Maidens': '0', 'Economy': '9.50'}, {'Overs': '2.1', 'Runs': '11', 'Wickets': '1', 'Maidens': '0', 'Economy': '5.24'}], 'Awards': {'MostValuablePlayer': 1, 'MostValuableBatter': 1, 'MostValuableBowler': 0}}]

    def ask_local_or_online_storage(self):
        self.user_choice = input(
            ' \n Please press 1 for local storage, 2 for online (RDS) or 3 for both \n')

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

        Returns
        -------
        self.driver: webdriver.Chrome

        '''
        self.driver = webdriver.Chrome()

        (self.driver).get(self.URL)
        delay = 10
        try:
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="gdpr-popup-container"]')))
            print("Frame Ready!")
            accept_cookies_button = WebDriverWait(self.driver, delay).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="gdpr-accept-btn"]')))
            print("Accept Cookies Button Ready!")
            accept_cookies_button.click()
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
                uuid.uuid4()), "PlayerLink": link, 'ImageLink': [], "ScorecardIds": [], "ScorecardBattingData": [], "ScorecardBowlingData": [], "Awards": {"MostValuablePlayer": 0, "MostValuableBatter": 0, "MostValuableBowler": 0}}
            self.master_list.append(player_dictionary)

    def collect_scoreboard_ids_and_profile_image_link(self):
        '''_collect_scoreboard_ids_and_profile_image_link 

        1. Load each Player Link
        2. Collect player profile photo link
        3. Navigate to Scorecard Link
        4. Collect list of scorecard links and add to player dictionary

        '''

        for player_dictionary in self.master_list:

            (self.driver).get(player_dictionary['PlayerLink'])
            ((self.driver).find_element(By.XPATH,
                                        '//*[@id="pp-sm-batting"]')).click()
            ((self.driver).find_element(By.XPATH,
                                        '//*[@id="batting-history-link-current"]')).click()

            self._get_player_profile_photo(player_dictionary)
            self._get_scoreboard_ids(player_dictionary)

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

    def _get_scoreboard_ids(self, player_dictionary) -> list:
        '''_get_scoreboard_ids 
        This function locates and stores id of games each player is involved with.    

        1. Wait for the player game table to load.
        2. Once loaded locate and create a list of scoreboard links on that page.
        Arguments:
            player_dictionary -- dictionary individual to each player to place collected data
        Returns:
            a list of scoreboard links
        '''

        delay = 10
        try:
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located(
                (By.XPATH, '//table[@class="rank-table"]')))
            scorecard_container = (self.driver).find_element(
                By.XPATH, '//table[@class="rank-table"]')
            time.sleep(1)
        except TimeoutException:
            print("Loading took too much time!")

        scorecard_container_body = scorecard_container.find_element(
            By.XPATH, './tbody')
        scorecard_container_list = scorecard_container_body.find_elements(
            By.XPATH, './tr')
        self.scorecard_id_list = []

        for row in scorecard_container_list:
            a_tag = row.find_element(By.TAG_NAME, 'a')
            link = a_tag.get_attribute('href')
            fixture_id = (link.split("="))[1]
            if fixture_id == "0":
                continue
            else:
                self.scorecard_id_list.append(fixture_id)

        player_dictionary['ScorecardIds'] = self.scorecard_id_list

    def retrieve_and_save_all_player_data(self):
        ''' 
        This method locates, pulls and save fixture information relevant to each player.

        1. Load each relevant page for each fixture id.
        2. Run collection methods to gather batter, bowler and award data.
        3. Run method to programatically store player data.
        '''

        for player_dictionary in self.master_list:
            for id in player_dictionary['ScorecardIds']:

                ((self.driver)).get(
                    f"https://www.lastmanstands.com/leagues/scorecard/1st-innings?fixtureid={id}")
                self._get_scorecard_player_data(player_dictionary)
                ((self.driver)).get(
                    f"https://www.lastmanstands.com/leagues/scorecard/2nd-innings?fixtureid={id}")
                self._get_scorecard_player_data(player_dictionary)
                ((self.driver)).get(
                    f"https://www.lastmanstands.com/leagues/scorecard/stats?fixtureid={id}")
                self._get_player_awards(player_dictionary)
            if self.user_choice == "1" or self.user_choice == "3":
                self._create_player_directory_structure(player_dictionary)
                self._save_player_dictionary_to_file(player_dictionary)
                self._download_and_save_images(player_dictionary)
            elif self.user_choice == "2" or self.user_choice == "3":
                self._create_pandas_dataframes(player_dictionary)
                self._upload_dataframes_to_rds()

    def _get_scorecard_player_data(self, player_dictionary):
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

        bowling_data_body = scorecard_data_table_list[1].find_element(
            By.XPATH, './tbody')
        bowling_data_list = bowling_data_body.find_elements(
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

        # create player, uuid, scorecarddata frames

        self.players = pd.DataFrame(player_dictionary, columns=[
            'PlayerName', 'UUID', 'PlayerLink'], index=[0])
        uuid = pd.DataFrame(player_dictionary, columns=['UUID'], index=[0])
        scorecards = pd.DataFrame(player_dictionary, columns=[
                                  'ScorecardIds', 'UUID'])

        # rename player, scorecard and uuid df

        self.players = self.players.rename(
            columns={"PlayerName": "name", "UUID": "uuid", "PlayerLink": "lms_profile_link"})
        scorecards = scorecards.rename(
            columns={"ScorecardIds": "scorecard_id", "UUID": "uuid"})
        uuid = uuid.rename(columns={"UUID": "uuid"})

        # set players and scorecards dtypes

        self.players['name'] = self.players['name'].astype('string')
        self.players['uuid'] = self.players['uuid'].astype('string')
        self.players['lms_profile_link'] = self.players['lms_profile_link'].astype(
            'string')

        scorecards['scorecard_id'] = scorecards['scorecard_id'].astype('int64')
        scorecards['uuid'] = scorecards['uuid'].astype('string')

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
                scorecards, batting_data, left_index=True, right_index=True)
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
                scorecards, bowling_data, left_index=True, right_index=True)
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

    def _upload_dataframes_to_rds(self):

        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'aicoredb.cz91qpjes5tm.us-east-1.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = 'AlbertKingClarks8*'
        PORT = 5432
        DATABASE = 'lms_db'

        engine = create_engine(
            f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")

        self.players.to_sql('players', engine, if_exists='append')
        self.combine_awards.to_sql(
            'awards', engine, if_exists='append')
        if self.combine_batting is not None:
            self.combine_batting.to_sql(
                'batting', engine, if_exists='append')
        if self.combine_bowling is not None:
            self.combine_bowling.to_sql(
                'bowling', engine, if_exists='append')

    def run_crawler(self):
        '''run_crawler 
        Calling method to call other methods.
        '''
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
