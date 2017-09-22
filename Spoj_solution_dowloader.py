import os
import requests
import grequests
from bs4 import BeautifulSoup

session = requests.session()

USERNAME = ''
PASSWORD = ''
BASE_URL = "http://www.spoj.com"
accepted_code = {}


# find/create valid path
def basePath():
    while 1:
        path = input('Enter a path to save all files: ').strip()
        if (path.startswith('~/')):
            path = path.replace('~', os.path.expanduser('~'), 1)
        if not os.path.exists(path):
            print('Path does not exists: ' + path)
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
    path = basePath()
    print('Saving files...')
    total = len(problemCode)
    no=0
    for i in range(total):
        if results[i]==None:
            no+=1
            continue
        extension = results[i].headers['Content-Disposition'].split('-src')[1]
        sourceFile = open(path + problemCode[i] + extension, "w")
        sourceFile.write((results[i].text).encode('ascii', 'ignore').decode('ascii'))
        sourceFile.close()
    print('Total files saved: ' + str(no))

# fetch all submissions
def process(soup):
    problemCode = []
    problemUrl = []
    r = session.get('http://www.spoj.com/status/'+USERNAME+'/signedlist/')
    signList = r.text
    f = open('data.txt', 'w+')
    f.write(signList)
    f.close()

    f = open('data.txt', 'r')
    data = f.readlines()
    for i in range(9, len(data) - 15):
        row = data[i].split('|')
        status = row[4].strip()
        pcode = row[3].strip()
        pid = row[1].strip()
        if status == 'AC' or status.isnumeric():
            accepted_code[pid] = pcode

    for code in accepted_code:
        problemCode.append(accepted_code[code]+code)
        problemUrl.append('/files/src/save/'+code+'/')

    u_request = (grequests.get(BASE_URL + url, session=session) for url in problemUrl)
    results = grequests.map(u_request)
    os.remove('data.txt')
    createFiles(results, problemCode)


def main():
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
