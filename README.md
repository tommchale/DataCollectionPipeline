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


## Testing

* Using unittest, a unittest TestCase class was created to check scraper was pulling the correct information.
* test_collect_scoreboard_ids_and_profile_image_link(self) checks that the information collected for each scorecard associated with each player and that the scraper has located an image link
* test_retrieve_and_save_all_player_data_master_list(self) this replaces the "master_list" with a mocked list to restrict data collection to one player.
          * retrieved data is then checked against a known accurate dictionary
          * saved data is also check it is stored int he correct location and contains accurate information
          * saved images are also checked that they exist in the correct location and match the correct format. 
## RDS and S3 data uploads

* Included functionality to upload data scraped to RDS SQL database
* Database is hosted in pgAdmin 
* Data collected from website in a dictionary where _create_pandas_dataframes converts in Pandas dataframes
* Learning points here were correct data types and naming conventions to allow for utilisation of SQL queries
* scraper required modification as not all players have batting and bowling data
* Data then uploaded to RDS using sqalchemy
* Scraped image data hosted in an s3 bucket uploaded using boto3
* Functionality also added to provide user option for local or online data storage
* env file added to ensire security of credentials for connecting to databases.

## Preventing recraping Data

* To prevent rescraping and uploading the same data to the RDS database, the _remove_scorecard_id_if_exists_in_RDS() connects to the RDS database and runs a query to pull all the batting and bowling ids in teh database. 
* The scorecard ids are then converted into a list and compared to the batting and bowling ids collected for each player.
* Any matching ids are removed and then the scraper continues for scorecard ids not already in the database.

## Docker

Following final testing and final refactor of code, scraper set to headless mode and conatinerised. This was acheieved by creating a Docker image to run the scraper, pushing it to Dockerhub, creating a new EC2 instance, pull the docker container onto that instance and running the scraper from there. 

## Prometheus

Prometheus was then ysing to monitor the EC2 instance and docker container that runs the scraper. Once configured a dashboard was created with Grafana to monitor the metrics of the containers and the hardware metrics of the EC2 instance.
