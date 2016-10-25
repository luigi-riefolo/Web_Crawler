CONTENTS OF THIS FILE
---------------------
   
 * Introduction
 * Requirements
 * Description
 * Author


INTRODUCTION
------------
web-crawler.py 1.0 is a simple web crawler implemented in Python.
Crawling is limited to one domain, thus any link outside
the main domain will not be considered.


REQUIREMENTS
------------
The script requires the "requests" Python module 
(http://docs.python-requests.org/en/master/)


DESCRIPTION
-----------
web-crawler.py takes a root URL and collects its links and static assets.
For each scanned URL, if a new:
	- link is found, then it is added to a list of links to crawl; 
	- asset is found, then it is added to a list of global assets;

Results are written by default to STDOUT. Using '--out' results can be
written to an output file.

Localised links are not processed. A localised link is a link that
contains any locale identifier listed in languages.txt or locales.txt (data).


AUTHOR
------
Luigi Riefolo <luigi.riefolo@gmail.com>
