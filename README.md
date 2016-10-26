CONTENTS OF THIS FILE
---------------------
   
 * Introduction
 * Requirements
 * Description
 * Options
 * Examples
 * License
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


OPTIONS
-------

Positional arguments:
  url              URL to crawl

Optional arguments:
  -h, --help       show this help message and exit
  -l n, --links n  maximum number of links to crawl
  -o of, --out of  write output to file (default STDOUT)
  -s, --strict     abort the execution if any page does not return a 200 code
  -q, --quiet      run in quiet mode; it can only be used with --out
  -v, --verbose    run in verbose mode
  --version        show program's version number and exit


EXAMPLES
--------
	./web-crawler.py www.domain.com
	./web-crawler.py www.domain.com -o out-file.txt
	./web-crawler.py http://www.domain.com --links 3
	

LICENSE
-------
This script is in the public domain, free from copyrights or restrictions.


AUTHOR
------
Luigi Riefolo <luigi.riefolo@gmail.com>
