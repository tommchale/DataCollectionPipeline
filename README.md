# WebScaper
Module to pull relevant infomation from Last Man Stands cricket website
## Why Last Man Stands

Last Man Stands (LMS) is a great site for the collection of data related to amateur cricket games. I captain an LMS side so thought it would be a good oppurtunity to collect and maintain a database for all the cricket stats for my team.

There is a lot of data avaiable on the LMS site but it is stored in a large number of different locations so the motivation behind this project was to store it in a central repository.

Link to site: https://www.lastmanstands.com/

## Technologies used

I created a general Scraper class using Selenium. In the constructor, the Selenium Chrome webdriver is initialised. WebDriverManager, in this case ChromeDriverManager, is used to automate the management of the drivers required by Selenium WebDriver.

## Methods used

* load_and_accept_cookies(self) -> webdriver.Chrome: : 
      ** this loads the last mans stands home team page and clicks "accept cookies button".
      ** due to inconsistent load times for the cookies container used a "WebDriverWait instead of a simple time delay
* get_player_list_container(self) -> Container:
      * simple method to return a list of the link to each individual player page from the main team page
      * again required a WebDriverWait to wait for the table containing the links to each player to load when clicked.
* create_master_list(self) -> list:
      * creates list where each player dictionary will be stored
      * also outlines the player dictionary with locations for collected data to be stored
      * player names and profile links are added to each dictionary programatically from the player_list_container
* collect_scoreboard_ids_and_profile_image_link(self):
      * this method was required to access each player page and collect:
              * each player profile image link
              * the fixture id's of all the games in which that player has played
                      * some players play different games for multiple teams
* retrieve_all_player_data(self):
       * method to load scorecard of each fixture that each player played in and collect:
              * player data for 1st innings
              * player data for second innings
              * player data if they had one Most Valuable Player/Batter/Bowler
       * difficulties with this method where:
              *  it is inconsitent is the player batted/bowled in each innings
              *  whether batting or bowling required different format of data collection
              *  had to run search for each row of scorecard table for the player name
              *  sometimes a row did not contained player name tag text data such as table headings
              *  used a try/except for a NoSuchElementException if the element where the name would be contained was not present in a row
* _create_player_directory_structure(self, player_dictionary)
        * method to create two folders
              * PlayerName for full player data dictionary storage
              * playerName > Images - for offline image storage
* _save_player_dictionary_to_file(self, player_dictionary) -> json:
         * save each player dictionary to player directory folder
         * called during data collection to limit failure of crawler fails during scraping
* _download_and_save_images(self, player_dictionary) -> image:
         * download and save jpgs for each image links to image folder
         * called during data collection to limit failure of crawler fails during scraping   
         
