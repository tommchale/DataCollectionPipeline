# WebScaper
Module to pull relevant infomation from Last Man Stands cricket website
## Why Last Man Stands

Last Man Stands (LMS) is a great site for the collection of data related to amateur cricket games. I captain an LMS side so thought it would be a good oppurtunity to collect and maintain a database for all the cricket stats for my team.

There is a lot of data avaiable on the LMS site but it is stored in a large number of different locations so the motivation behind this project was to store it in a central repository.

Link to site: https://www.lastmanstands.com/

## Technologies used

I created a general Scraper class using Selenium. In the constructor, the Selenium Chrome webdriver is initialised. WebDriverManager, in this case ChromeDriverManager, is used to automate the management of the drivers required by Selenium WebDriver.
