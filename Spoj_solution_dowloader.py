import os
import getpass
import requests
import grequests
from bs4 import BeautifulSoup

session = requests.session()

BASE_URL = "http://www.spoj.com"
accepted_code = {}


# find/create valid path
def basePath():
    while 1:
        path = input('Enter path to save files: ').strip()
        # complete home path
        if (path.startswith('~/')):
            path = path.replace('~', os.path.expanduser('~'), 1)

        # create path if not exists
        if not os.path.exists(path):
            print('Path not exists: ' + path)
            permission = input('Do you want to create this path? (Y/N) ')
            if (permission.upper() == 'Y'):
                os.makedirs(path)
            else:
                continue

        print('Valid Path: ' + path)
        permission = input('Save files to this path? (Y/N) ')
        if (permission.upper() == 'Y'):
            break
        else:
            continue
    return path + '/'


# save source code files
def createFiles(results, problemCode):
    path = basePath()  # path to save files
    print('Writing files...')
    total = len(problemCode)
    #print(results)
    no=0
    for i in range(total):
        #print(results[i])
        if results[i]==None:#print(problemCode[i]);
            no+=1;continue
        extension = results[i].headers['Content-Disposition'].split('-src')[1]
        #print(extension,problemCode[i])
        sourceFile = open(path + problemCode[i] + extension, "w")
        sourceFile.write((results[i].text).encode('ascii', 'ignore').decode('ascii'))
        sourceFile.close()
    print('Total files saved: ' + str(total))
    print(no)

# fetch all submissions
def process(soup):
    problemCode = []
    problemUrl = []
    r = session.get('http://www.spoj.com/status/rajat189/signedlist/')
    signList = r.text
    # print(signList)
    f = open('a.txt', 'w+')
    f.write(signList)
    f.close()

    f = open('a.txt', 'r')
    data = f.readlines()
    for i in range(9, len(data) - 15):
        row = data[i].split('|')
        status = row[4].strip()
        pcode = row[3].strip()
        pid = row[1].strip()
        if status == 'AC' or status.isnumeric():
            accepted_code[pid] = pcode

    #print(accepted_code)
    for code in accepted_code:
        problemCode.append(accepted_code[code]+code)
        problemUrl.append('/files/src/save/'+code+'/')
    #print(problemCode)

    unsent_request = (grequests.get(BASE_URL + url, session=session) for url in problemUrl)
    print(unsent_request)
    results = grequests.map(unsent_request)

    createFiles(results, problemCode)


def main():
    USERNAME = ''
    PASSWORD = ''
    payload={"login_user": USERNAME,"password": PASSWORD}

    print('Logging in...')
    result = session.post(BASE_URL + "/login/", data=payload)
    result = session.get(BASE_URL + "/status/" + USERNAME + "/all/")

    soup = BeautifulSoup(result.text, "html.parser")
    logout_btn = soup.find("a", {"href": "/logout"})
    if not logout_btn:
        print('Failed!')
        return
    user = soup.find('a', href="/users/" + USERNAME).text.strip()[:-1]
    print('Hello ' + user)
    process(soup)
if __name__ == '__main__':
    main()
