from typing import Container
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import time
import uuid


class LastManStandsScraper:
    def __init__(self):
        self.URL = (
            "https://www.lastmanstands.com/team-profile/t20/?teamid=20327")
        self.master_list = []

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
        '''create_master_list creates template for the list where collceted data will be stored
        Adds Player Name and Player Link to each unique entry.

        Returns:
            master_list: list with template for data storage
        '''

        for row in self.player_list_container:
            name = row.find_element(By.TAG_NAME, 'a').text
            a_tag = row.find_element(By.TAG_NAME, 'a')
            link = a_tag.get_attribute('href')
            player_dictionary = {"PlayerName": name, "UUID": str(
                uuid.uuid4()), "PlayerLink": link, "ScorecardIds": [], "ScorecardData": []}
            self.master_list.append(player_dictionary)

        print(self.master_list)

    def collect_scoreboard_ids(self):
        '''collect_scoreboard_ids 
        1. Load each Player Link
        2. Navigate to Scorecard Link
        3. Collect list of scorecard links and add to player dictionary

        '''

        for player_dictionary in self.master_list:
            (self.driver).get(player_dictionary['PlayerLink'])
            ((self.driver).find_element(By.XPATH,
             '//*[@id="pp-sm-batting"]')).click()
            ((self.driver).find_element(By.XPATH,
             '//*[@id="batting-history-link-current"]')).click()
            self.get_scoreboard_ids()
            player_dictionary['ScorecardLinks'].append(
                self.scorecard_id_list)

    def get_scoreboard_ids(self) -> list:
        '''get_scoreboard_ids 
        1. Wait for the player game table to load.
        2. Once loaded locate and create a list of scoreboard links on that page.

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
            self.scorecard_id_list.append(fixture_id)

    def retrieve_player_data(self):
        # for player_dictionary in self.master_list:
        #   for id in player_dictionary['ScorecardIds']:
        #      ((self.driver)).get(f"https://www.lastmanstands.com/leagues/scorecard/1st-innings?fixtureid={id}")
        #   (self.driver).find_element(By.XPATH, '//*[@id="scorecard-2020-table-block"]')
        ((self.driver)).get(
            f"https://www.lastmanstands.com/leagues/scorecard/1st-innings?fixtureid=345123")

        # find whether batting or bowling first.

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

        for row in batting_data_list:
            try:
                player_name = row.find_element(By.TAG_NAME, 'a').text
                if player_name == "Freddie Simon":
                    print("Name found")
                    data_list = row.find_elements(By.XPATH, './td')
                    batting_dictionary = {"How Out": (data_list[0].text).split("\n")[1], "Runs": data_list[1].text, "Balls": data_list[2].text,
                                          "Fours": data_list[3].text, "Sixs": data_list[4].text, "SR": data_list[5].text}
                    print(batting_dictionary)
            except NoSuchElementException:
                continue

        for row in bowling_data_list:
            try:
                player_name = row.find_element(By.TAG_NAME, 'a').text
                if player_name == "Freddie Simon":
                    print("Name found")
                    data_list = row.find_elements(By.XPATH, './td')
                    bowling_dictionary = {"Overs": data_list[1].text, "Runs": data_list[2].text,
                                          "Wickets": data_list[3].text, "Maidens": data_list[4].text, "Economy": data_list[5].text}
                    print(bowling_dictionary)
            except NoSuchElementException:
                continue

    ''' if row.find_element(By.XPATH, './td[@class="sc-name-section"]') in row:
    print("This one contains a name")
    if row.find_element(By.TAG_NAME, 'a').text == "Freddie Simon":
        print("Name found")
        data_list = row.find_elements(By.XPATH, './td')
        print(data_list)
        batting_dictionary = {"Runs": data_list[0], "Balls": data_list[1],
                                "Fours": data_list[2], "Sixs": data_list[3], "SR": data_list[4]}
        break
else:
    print("Name not in this row")
    '''

    # print(batting_dictionary)

    def run_crawler(self):
        self.load_and_accept_cookies()
        # self.get_player_list_container()
        # self.create_master_list()
        # self.collect_scoreboard_ids()
        # print(self.master_list)
        self.retrieve_player_data()


def run():
    crawler = LastManStandsScraper()
    crawler.run_crawler()


if __name__ == "__main__":

    run()
