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

`from resources.lib.modules import thexem`

You will also need to change a few lines in the def `getConstants(self)` function in `sources.py` file:

Find the line that says:

`from resources.lib.sources import sources`

Comment out that line by adding a pound/hashtag at the beginning like this:

`#from resources.lib.sources import sources`

add the following:

`from openscrapers import sources`
