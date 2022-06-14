from typing import Container
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import uuid


class LastManStandsScraper:
    def __init__(self):
        self.URL = (
            "https://www.lastmanstands.com/team-profile/t20/?teamid=20327")

        self.player_link_list = []
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
                uuid.uuid4()), "PlayerLink": link, "ScorecardLinks": [], "ScorecardData": []}
            self.master_list.append(player_dictionary)

    def get_player_links(self) -> list:

        for item in self.player_list_container:
            a_tag = item.find_element(By.TAG_NAME, 'a')
            link = a_tag.get_attribute('href')
            self.player_link_list.append(link)

        print(self.player_link_list)

    def load_player_links(self):
        '''
        Return content from each player page
        '''

        for link in self.player_link_list:
            (self.driver).get(link)
            ((self.driver).find_element(By.XPATH,
             '//*[@id="pp-sm-batting"]')).click()
            ((self.driver).find_element(By.XPATH,
             '//*[@id="batting-history-link-current"]')).click()
            self.get_scorecard_links()

    def get_scorecard_links(self) -> list:

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
        self.scorecard_link_list = []

        for row in scorecard_container_list:
            a_tag = row.find_element(By.TAG_NAME, 'a')
            link = a_tag.get_attribute('href')
            self.scorecard_link_list.append(link)

    def add_scorecard_link_to_player_dict(self) -> dict:

        for value in self.player_dictionary:
            value.setdefault("scorecard_links", self.scorecard_link_list)

    def run_crawler(self):
        self.load_and_accept_cookies()
        self.get_player_list_container()
        self.create_master_list()
        # self.get_player_links()
        # self.load_player_links()
        # self.get_scorecard_links()


def run():
    crawler = LastManStandsScraper()
    crawler.run_crawler()


if __name__ == "__main__":

    run()
