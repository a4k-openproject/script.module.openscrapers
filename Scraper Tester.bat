@ECHO OFF
CLS
GOTO Launch

:Launch
CLS
ECHO.
ECHO Welcome to Scraper Tester, Please Choose Your Option
ECHO.
ECHO 1. Test OpenScrapers En and En-Debrid
ECHO 2. Test OpenScrapers Foreign
ECHO 3. Test OpenScrapers Torrents
ECHO 4. Test Scrubs v2 Scrapers
ECHO 5. Exit
ECHO.

CHOICE /C 12345 /M "Enter your choice:"

:: Note - list ERRORLEVELS in decreasing order
IF ERRORLEVEL 5 GOTO End
IF ERRORLEVEL 4 GOTO Scrubs
IF ERRORLEVEL 3 GOTO OS-Torrents
IF ERRORLEVEL 2 GOTO OS-Foreign
IF ERRORLEVEL 1 GOTO OS-En-Deb

:OS-En-Deb
CLS
ECHO Choose what type of test you would like to run
ECHO 1. Movie Test
ECHO 2. Episode Test
ECHO.

CHOICE /C 12 /M "Enter your choice:"

IF ERRORLEVEL 2 GOTO OS-En-Deb-Episode
IF ERRORLEVEL 1 GOTO OS-En-Deb-Movie

:: Example cmd for movie test: python scrape-test.py folders= test_type=1 test_mode=movie timeout_mode=false number_of_tests=15
:: Example cmd for episode test: python scrape-test.py folders= test_type=1 test_mode=movie timeout_mode=false number_of_tests=15

:OS-En-Deb-Movie
CLS
ECHO Running Scraper Test
ECHO.
ECHO Please Wait As This Can take up to 10-20mins
ECHO.
ECHO If this hangs for more than 10mins check test-results folder
ECHO and open text file for this test and check hanging providers
ECHO so you can move to to_be_fixed folder and then test again
ECHO.
ECHO Close Window or Press CTRL+C to terminate test if it hangs
ECHO.
python scrape-test.py folders=en,en_DebridOnly test_type=1 test_mode=movie timeout_mode=false number_of_tests=15 > test-results\en-en_DebridOnly\os-en-and-debrid-movie-scrape-test.txt
GOTO Retest

:OS-En-Deb-Episode
CLS
ECHO Running Scraper Test
ECHO.
ECHO Please Wait As This Can take up to 10-20mins
ECHO.
ECHO If this hangs for more than 10mins check test-results folder
ECHO and open text file for this test and check hanging providers
ECHO so you can move to to_be_fixed folder and then test again
ECHO.
ECHO Close Window or Press CTRL+C to terminate test if it hangs
ECHO.
python scrape-test.py folders=en,en_DebridOnly test_type=1 test_mode=episode timeout_mode=false number_of_tests=15 > test-results\en-en_DebridOnly\os-en-and-debrid-episode-scrape-test.txt
GOTO Retest

:OS-Foreign
CLS
ECHO Choose what type of test you would like to run
ECHO 1. Movie Test
ECHO 2. Episode Test
ECHO.

CHOICE /C 12 /M "Enter your choice:"

IF ERRORLEVEL 2 GOTO OS-Foreign-Episode
IF ERRORLEVEL 1 GOTO OS-Foreign-Movie

:OS-Foreign-Movie
CLS
ECHO Running Scraper Test
ECHO.
ECHO Please Wait As This Can take up to 10-20mins
ECHO.
ECHO If this hangs for more than 10mins check test-results folder
ECHO and open text file for this test and check hanging providers
ECHO so you can move to to_be_fixed folder and then test again
ECHO.
ECHO Close Window or Press CTRL+C to terminate test if it hangs
ECHO.
python scrape-test.py folders=de,es,gr,pl test_type=1 test_mode=movie timeout_mode=false number_of_tests=15 > test-results\de,es,gr,pl\os-foreign-movie-scrape-test.txt
GOTO Retest

:OS-Foreign-Episode
CLS
ECHO Running Scraper Test
ECHO.
ECHO Please Wait As This Can take up to 10-20mins
ECHO.
ECHO If this hangs for more than 10mins check test-results folder
ECHO and open text file for this test and check hanging providers
ECHO so you can move to to_be_fixed folder and then test again
ECHO.
ECHO Close Window or Press CTRL+C to terminate test if it hangs
ECHO.
python scrape-test.py folders=de,es,gr,pl test_type=1 test_mode=episode timeout_mode=false number_of_tests=15 > test-results\de,es,gr,pl\os-foreign-episode-scrape-test.txt
GOTO Retest

:OS-Torrents
CLS
ECHO Choose what type of test you would like to run
ECHO 1. Movie Test
ECHO 2. Episode Test
ECHO.

CHOICE /C 12 /M "Enter your choice:"

IF ERRORLEVEL 2 GOTO OS-Torrents-Episode
IF ERRORLEVEL 1 GOTO OS-Torrents-Movie

:OS-Torrents-Movie
CLS
ECHO Running Scraper Test
ECHO.
ECHO Please Wait As This Can take up to 10-20mins
ECHO.
ECHO If this hangs for more than 10mins check test-results folder
ECHO and open text file for this test and check hanging providers
ECHO so you can move to to_be_fixed folder and then test again
ECHO.
ECHO Close Window or Press CTRL+C to terminate test if it hangs
ECHO.
python scrape-test.py folders=en_Torrent test_type=1 test_mode=movie timeout_mode=false number_of_tests=15 > test-results\en_Torrent\os-torrents-movie-scrape-test.txt
GOTO Retest

:OS-Torrents-Episode
CLS
ECHO Running Scraper Test
ECHO.
ECHO Please Wait As This Can take up to 10-20mins
ECHO.
ECHO If this hangs for more than 10mins check test-results folder
ECHO and open text file for this test and check hanging providers
ECHO so you can move to to_be_fixed folder and then test again
ECHO.
ECHO Close Window or Press CTRL+C to terminate test if it hangs
ECHO.
python scrape-test.py folders=en_Torrent test_type=1 test_mode=episode timeout_mode=false number_of_tests=15 > test-results\en_Torrent\os-torrents-episode-scrape-test.txt
GOTO Retest

:Scrubs
CLS
ECHO Choose what type of test you would like to run
ECHO 1. Movie Test
ECHO 2. Episode Test
ECHO.

CHOICE /C 12 /M "Enter your choice:"

IF ERRORLEVEL 2 GOTO Scrubs-Episode
IF ERRORLEVEL 1 GOTO Scrubs-Movie

:Scrubs-Movie
CLS
ECHO Running Scraper Test
ECHO.
ECHO Please Wait As This Can take up to 10-20mins
ECHO.
ECHO If this hangs for more than 10mins check test-results folder
ECHO and open text file for this test and check hanging providers
ECHO so you can move to to_be_fixed folder and then test again
ECHO.
ECHO Close Window or Press CTRL+C to terminate test if it hangs
ECHO.
python scrape-test.py folders=scrapetest-scrubs test_type=1 test_mode=movie timeout_mode=false number_of_tests=15 > test-results\scrapetest-scrubs\scrubs-movie-scrapetest.txt
GOTO Retest

:Scrubs-Episode
CLS
ECHO Running Scraper Test
ECHO.
ECHO Please Wait As This Can take up to 10-20mins
ECHO.
ECHO If this hangs for more than 10mins check test-results folder
ECHO and open text file for this test and check hanging providers
ECHO so you can move to to_be_fixed folder and then test again
ECHO.
ECHO Close Window or Press CTRL+C to terminate test if it hangs
ECHO.
python scrape-test.py folders=scrapetest-scrubs test_type=1 test_mode=episode timeout_mode=false number_of_tests=15 > test-results\scrapetest-scrubs\scrubs-episode-scrapetest.txt)
GOTO Retest

:Retest
CLS
ECHO Would you like to start again or exit
ECHO 1. Start Again
ECHO 2. Exit
ECHO.

CHOICE /C 12 /M "Enter your choice:"

IF ERRORLEVEL 2 GOTO End
IF ERRORLEVEL 1 GOTO Launch

:End
CLS
ECHO Would you like to clean up .pyc files
ECHO 1. Yes
ECHO 2. No
ECHO.

CHOICE /C 12 /M "Enter your choice:"

IF ERRORLEVEL 2 GOTO End2
IF ERRORLEVEL 1 GOTO Cleanup

:Cleanup
CLS
ECHO Cleaning up .pyc files recursively...
del /s *.pyc
GOTO End2

:End2