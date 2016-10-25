#!/usr/bin/env python

import sys
import re
import fcntl
import os    
from urlparse import urlparse
from io import BytesIO
import argparse
try:
    import requests
except ImportError:
    print("Need to install request module")
    sys.exit(1)


me = os.path.basename(sys.argv[0])
__version__ = "1.0"

# Usage utilities
class style:
    BOLD = "\033[1m"
    BLUE = "\033[94m"
    END = "\033[0m"
    GREEN = "\033[92m"


def desc():
    return ("{0}SYNOPSIS{1}\n"
	    "\tweb-crawler.py [-h,--help] [-l, --links] [-o, --out] "
            "[-s, --strict] [-q, --quiet] [-v,--verbose] [--version] url\n\n"
	    "{0}DESCRIPTION{1}\n"
    	"\tA simple web crawler.\n\n"
        "{0}OPTIONS{1}\n".format(style.BOLD, style.END))


def epilog():
	return ("{1}EXAMPLES{2}\n"
        "\t{0} www.domain.com\n"
        "\t{0} www.domain.com -o out-file.txt\n"
        "\t{0} http://www.domain.com --links 3\n\n"
        "\tFor additional information see the README file.\n\n"
        "{1}EXIT STATUS{2}\n"
        "\t0 - Success\n"
        "\t1 - Failure\n\n"
        "{1}AUTHOR{2}\n"
        "\tLuigi Riefolo <luigi.riefolo@gmail.com>\n\n"
        "{1}LICENSE{2}\n"
        "\tThis script is in the public domain, free from copyrights or restrictions.\n\n"
        "{1}VERSION{2}\n"
        "\t{3}\n".format(me, style.BOLD, style.END, __version__))


# Global variables
args = None
locales = dict()
outFile = None
assetDic = dict()

# Exit codes
SUCCESS = 0
FAIL = 1


def write(msg):
    if args.out is not None:
        msg = re.sub(r"\033\[\d{1,2}m", "", msg)
        args.out.write(msg + "\n")
    else:
        print(msg)

 
def abort(msg):
    m = "[ERROR] " + me + ": " + msg
    write(m)
    sys.exit(FAIL)


# Valiate the command-line arguments
def validate():
    urlErr = ("Please supply a valid URL, e.g. "
        "www.domain.com or http://www.domain.com")
    try:
        r = urlparse(args.url)
        regex = re.compile(r'^(?:http)s?://')
        isHttp = re.match(regex, args.url)
        if r.scheme != "" and not isHttp:
            abort("Only supported protocol is http[s]")

        proto = "http://"
        if r.scheme == "":
            args.url = proto + args.url 
            return validate()
        
        if r.netloc == "":
            abort(urlErr)

        return True
    except argparse.ArgumentError as e:
        print("Could not process the command line arguments: " + e)


def outFile():
    if args.out:
        if not args.quiet:
            print("Using out file: " + args.out.name)
        try:
            args.out = open(args.out.name, "wb")
            fcntl.flock(args.out, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError as e:
            abort("Could not open out file: " + e)

 
def loadLocales():
    locFiles = ["locales.txt", "languages.txt"]
    
    for locF in locFiles:
        try:
            f = open("data/" + locF, 'r')
        except IOError:
            abort("Cannot open " + locF)
        else:
            for l in f:
                locales[l.strip()] = True
            f.close()


# Defines whether a URL is localised
def isLocale(url):
    loc = url.lower()
    if loc[1:-1] in locales:
        return True
    match = re.match(r'/([\w-]+)/', url.lower(), flags=re.I)
    if match and match.group()[1:-1] in locales:
        return True
    return False


# Collect all the static assets in content
def getAssets(content):
    global assetDic
    newAssets = dict() 
    reg = re.compile(r'[src|href|content]="([^http][\w/\-:.@]+\.[\w]{1,5})"', flags=re.I)
    assets = re.findall(reg, content)

    cnt = 0
    if len(assets):
        for a in assets:
            cnt += 1
            if a not in assetDic:
                assetDic[a] = True
                newAssets[a] = True

        write("\t%sStatic assets found:%s\t%s" % 
            (style.GREEN, style.END, cnt))
        write("\t%sNew static assets:%s\t%s/%s" % 
            (style.GREEN, style.END, len(newAssets), cnt))
        for a in newAssets:
            write("\t\t%s" % (a))


def crawl(rootUrl):
    write("%sCrawling root URL:%s %s%s%s" % 
        (style.GREEN, style.END, style.BLUE, args.url, style.END))
    crawl = dict()
    crawl["/"] = True
    cnt = 1
    crawled = dict()
    deadLinks = []

    while len(crawl) > 0:
        if args.links > 0 and args.links < cnt:
            break

        curr = (crawl.popitem())[0]

        # Skip links that have 
        # already been collected
        if curr in crawled:
            continue

        write("\n%sCrawling:%s\t%s\t\t%s%s%s%s" % 
            (style.GREEN, style.END, cnt, style.BLUE, rootUrl, curr, style.END))
 
        # Update the link counter 
        if args.out and not args.quiet:
            sys.stdout.write("Crawling page:\t%s\r" % (cnt))
            sys.stdout.flush()

        r = requests.get(
            rootUrl + curr,
            verify=True,
            timeout=20)
        cnt += 1
        crawled[curr] = True

        getAssets(r.content)
        
        # Reset the encoding if necessary
        if not re.match(r'utf-8', r.encoding.lower(), flags=re.I):
            r.encoding = "utf-8"

        # Evaluate the response code
        if r.status_code != requests.codes.ok:
            write("[ERROR]\tCould not get content for " + rootUrl + curr)
            write("Response:\n" + str(r))
            if args.strict:
                r.raise_for_status()
            deadLinks.append(rootUrl + curr)

	    # Collect links on the current pages
        reg = re.compile(r'href="([\w/-]+)"', flags=re.I)
        links = re.findall(reg, str(r.content))
        if len(links):
            write("\t%sLinks found:%s\t\t%s" % 
                (style.GREEN, style.END, len(links)))

        newLinks = []
        for url in links:
            # Avoid locales
            if isLocale(url):
                continue          

            # Avoid circles
            if url not in crawl and url not in crawled:
                crawl[url] = True
                newLinks.append(url)

        write("\t%sNew links:%s\t\t%s/%s" % 
            (style.GREEN, style.END, len(newLinks), len(links))) 
        for l in newLinks:
            write("\t\t%s" % (l))

    write("%sDead links found:%s\t%s" % 
        (style.GREEN, style.END, len(deadLinks)))
    if args.verbose:
        for l in deadLinks:
            write(l)


def main():

    # Get the command-line arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
	    description=desc(),
        epilog=epilog())
    parser._positionals.title = 'Positional arguments'
    parser._optionals.title = 'Optional arguments'

    # Positional args
    parser.add_argument("url", 
            type=str, 
            help="URL to crawl")
    # Optional args
    parser.add_argument("-l", "--links",
            metavar="n", 
            type=int, 
            help="maximum number of links to crawl")
    parser.add_argument("-o", "--out",
            metavar="of", 
            type=argparse.FileType('w'), 
            help="write output to file (default STDOUT)")
    parser.add_argument("-s", "--strict",
            action="store_true",
            help="abort the execution if any page does not return a 200 code")
    parser.add_argument("-q", "--quiet",
            action="store_true",
            help="run in quiet mode; it can only be used with --out")
    parser.add_argument("-v", "--verbose",
            action="store_true",
            help="run in verbose mode")
    parser.add_argument('--version',
        action='version', 
        version='%(prog)s ' + __version__)

    global args
    args = parser.parse_args()

    if args.strict:
        print("Running in strict mode")    

    validate()
    outFile() 
    loadLocales()
    crawl(args.url)

    if args.out:
        fcntl.flock(args.out, fcntl.LOCK_UN)
        args.out.close()

    return SUCCESS

 
# Main 
if __name__ == "__main__":
    sys.exit(main())
    


