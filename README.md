```
#               ██████╗ ██████╗ ███████╗███╗   ██╗                 
#              ██╔═══██╗██╔══██╗██╔════╝████╗  ██║                 
#              ██║   ██║██████╔╝█████╗  ██╔██╗ ██║                 
#              ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║                 
#              ╚██████╔╝██║     ███████╗██║ ╚████║                 
#               ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝                 
#                                                                  
#  ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗ ███████╗
#  ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝
#  ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝███████╗
#  ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗╚════██║
#  ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║███████║
#  ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝
#                                                                  
```

Welcome to OpenScrapers Project,

This project is in hopes to unify the community and contribute to one scraper pack for multi scraper add-ons and not
having the repo go dead or disappear. The goal is to stop the drama, the egos, everything and work together and make
this a great scraper pack so the community can benefit. Addons4Kodi takes no credit for putting this together, and we
thank all devs that have contributed to multiple projects over time.

# OpenScrapers Repo

You can add the source directory to your own repository for convenience and updates
```
<dir>
    <info compressed="false">https://raw.githubusercontent.com/a4k-openproject/repository.openscrapers/master/zips/addons.xml</info>
    <checksum>https://raw.githubusercontent.com/a4k-openproject/repository.openscrapers/master/zips/addons.xml.md5</checksum>
    <datadir zip="true">https://raw.githubusercontent.com/a4k-openproject/repository.openscrapers/master/zips/</datadir>
</dir>
```
# How to Import Open Scrapers Into Any Addon

Any multi-source Kodi addon can be altered to use these new scrapers instead of its own, you can follow the
instructions below to get things updated. When appling to a different addon, change "name_of_addon" with the name
of the addon.

Open the `addons/plugin.video.name_of_addon/addon.xml`.

Add the following line to the addon.xml file:

`<import addon=”script.module.openscrapers”/>`

Open addons/script.module.name_of_addon/lib/resources/lib/modules/sources.py

Add the following line to the `sources.py` file:

`import openscrapers`

Add it right after the line that says:

`import re

You will also need to change a few lines in the def `getConstants(self)` function in `sources.py` file:

Find the line that says:

`from resources.lib.sources import sources`

Comment out that line by adding a pound/hashtag at the beginning like this:

`#from resources.lib.sources import sources`

add the following:

`from openscrapers import sources`

# External Scraper Tester

With the help of Jabaxtor, we now have an external scraper tester that can test any scraper folder in
the lib\openscrapers\sources_openscrapers and this also means your can bring in scraper folders from other addons
and add them to this directory, but you will have to do a lil bit of work to get it working right, read below for more info.

In the root directory of OpenScrapers you will find two files

`scrape-test.py and Scraper Tester.bat`

scrape-test.py is where all the magic happens.

REQUIREMENTS
Python2 latest version
install bs4 dependency for Python

`pip install bs4`

# Command Arguments

folders=(name of scraper folder ie:en,en_DebridOnly)

test_type=(1 or 0)

test_mode=(movie or episode)

timeout_mode=(true, y, True, false, False, n)

number_of_tests=(1-500)

# Argument Explanations

folders: Specifies the folder or folders you want to test, test multiple with a comma separator

test_type: Specifies if you'd like to test all scrapers in the folder or just a specific one

test_mode: Specifies the type of test you'd like to run such as testing scrapers against a set of movies or episodes

timeout_mode: Specifies if you would like to use timeout of 60 or not. If set to true, True, or y then it will force number_of_tests to 1

number_of_tests: Specifies the amount of sources you'd like to test against the scrapers, such as 10 movies on trakts popular list

# Example Scraper Command

Requires python to run

scrape-test.py folders=en,en_DebridOnly test_type=1 test_mode=movie timeout_mode=false number_of_tests=10

This will test all scrapers in en and en_DebridOnly with 10 movies sources from trakts popular movie list
and will continue until the scrape finishes

# Adding Scrapers from other addons

First copy the scraper folder, usually called something like "en", from an addon like EggScrapers for instance,
rename it to something other than what's already `lib\openscrapers\sources_openscrapers`, for instance,
for eggscrapers call the folder: scrapertest-egg

Then you'll need to copy the init.py file from any other folder such as en and add it to this new one

Then open all the scrapers in something like Notepad++ and replace

`from resources.lib.modules`

with

`from openscrapers.modules`

in all open files.

This is only because it would need to use the modules from OpenScrapers instead of an external addon

Now you're ready to run your command make the folder argument folder=scrapertest-egg

# Scraper Tester Batch

I made an easy to use batch file pre-configured for OpenScrapers, EggScrapers, Yoda, and Scrubs

Once you open it you will get your options to test different addons, pretty easy to follow along :)

Preset folder names in the batch file for external addons are below so please follow last section and use these
folder names to test external scrapers from preset addons

`scrapertest-egg, scrapertest-yoda, scrapertest-scrubs`

Only thing you should know is that if a scraper hangs, it will stall the whole test, you can check by opening the
test-results folder and opening the txt file results for the file you're testing. If you see the same set of scrapers
repeating over and over, then there's an issue with those scrapers. Close the window or press ctrl+c to terminate
the batch so you can move those scrapers out and try again!

Enjoy!
