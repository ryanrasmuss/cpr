from api_headers import api_call, login
from helper import helper, subjects
from getpass import getpass as gp
from os import stat
from sys import argv
import urllib3
import csv, json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session_file = 'session.txt'
out_file = 'output.txt'

def help():

    print("\nUsage:  cpr.sh login [mgmt_ip_addr] [port#] [username]")
    print("\tcpr.sh [command] {parameters}")
    print("\tcpr.sh [command] -csv [filename.csv]")
    print("\tcpr.sh publish")
    print("\tcpr.sh logout")
    print("\tcpr.sh help (for more details)\n")


def detailed_help():

    help()

    print("Supported commands:")

    for key,val in subjects.items():
        print("\t" + val[0])

    # print("Run \"./cpr.sh [command]\" for a list of commands and parameters")


# Retrieve Session Information from file
def get_session_data(session_file):

    with open(session_file) as f:
        data = f.read()

    # split content of file 
    # expecting [ site, port, sid ]
    data = data.split('\n')
    f.close()
    
    return data


# takes user input parameters and converts it to a json for POST
def get_payload(requirements):

    return_me = {}
    nested = 0

    # expect even number of args. If not, then user did not follow documentation
    if len(requirements) % 2 != 0:
        print("Error: expecting even number of arguments aside from command")
        return return_me

    # build the key-value pairs
    # handle embedded key-value(s) denoted by ':'
    # handle lists with ','
    ''' iterate over every other two '''
    for i in range(0, len(requirements), 2):
        if ':' in requirements[i+1]:
            return_me[requirements[i]] = list_parser(requirements[i + 1])
        elif ',' in requirements[i+1]:
            return_me[requirements[i]] = requirements[i + 1].split(',')
        else:
            return_me[requirements[i]] = requirements[i+1]

    return return_me


# performs login and creates the session.txt file
def setup(params):

    # expecting [ site, port, user ]

    if len(params) != 3:
        print("Login parameters seem weird. Try again.")
        help()
        return None

    site, port, user = params[0], params[1], params[2]

    if port == 'default':
        port = '443'

    password = gp("Password: ")

    # make login POST
    sid = login(user, password, site, port)

    # if sid is None, then we did not login successfully
    if None == sid:
        print("Failed to login...")
        return None

    # otherwise prepare to write session info to session.txt
    f = open(session_file, "w+")
    
    # check size of session.txt for content
    filesize = stat(session_file).st_size
    
    # if the session.txt file is not empty, then someone did not terminate their session 
    if filesize != 0:
        print("There seems to be another session already established.")
        with open(session_file, "r") as f:
            print (f.read())
        print("Please terminate this session before logging in. Try logout.")
        return None

    # if file is empty, then we can write out session to the file
    f.write(site + '\n')
    f.write(port + '\n')
    f.write(sid)
    f.close()

    print("Done setting up")
    print ("Created session file: " + session_file)


# handles response codes and prints data to screen
def handle_response(command, response):

    specials = [ 'publish', 'discard', 'logout', 'help' ]
    immutable = 'show'

    # get response
    data = response.json()
    # clean up response, so user can read
    pretty_print = json.dumps(data, indent=4, sort_keys=False)

    # write the response to output file
    with open(out_file, 'w') as f:
        f.write(pretty_print)

    f.close()

    print("Wrote response content to %s" % out_file)

    status = str(response.status_code)

    print("Status code :%s" % status)

    # if response is 200 (good) make sure we don't tell user to publish if they run publish,discard,logout,help,or show(s)
    if (status == '200' and (command not in specials) and (immutable not in command)):
        print("\n\tRemember to publish changes via: \"./cpr.sh publish\"\n")
        return '200'
    elif status == '409':
        print("\n\tProblem with locks. Make sure you are publishing and terminating sessions properly.\n")
        return '409'
    elif status == '404':
        print("\nI don't recognize the command: %s\n" % (command))
        helper(command)
        return '404'
    elif status == '400':
        print("\nError or missing command parameters. Refer to output.txt\n")
        return '400'
    elif status == '401':
        print("\nSession Expired. You need to login.\n")
        session_fd = open(session_file, 'w')
        session_fd.truncate()
        session_fd.close()
        return '401'
    else:
        print('Response: %s (Check output.txt for more)' % (response.status_code))
        return None

# python3 cpr.py add-host -csv hosts.csv 
# converts content in csv to json and makes POST per line
def csv_mode(command, params, address, port, sid):

    # expecting [-csv. filename.csv]

    # XXX can't handle lists sub lists yet

    filename = params[1]
    # open csv file
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        columns = 0
        headers = []
        # iterate through rows of csv file
        for row in csv_reader:
            if line_count == 0:
                # this is the first row, which have the headers. need to count them
                for item in row:
                    # add each column name to our headers list
                    headers.append(item)
                line_count += 1
            else:
                payload = {}
                # this means we are not looking at the header anymore
                # for every column build [header_name] : [value] pair
                for i in range(0, len(headers)):
                    # name : example1
                    payload[headers[i]] = row[i]
                line_count += 1
                payload["ignore-warnings"] = "true"
                # print(payload)
                # make POST 
                response = api_call(address, port, command, payload, sid)
                # deal with response from server
                response_code = handle_response(command, response)
                # if we run into problem - abort
                if response_code != '200':
                    print("Problem - Recommend to review output.txt and run ./cpr.sh discard")
                    csv_file.close()
                    return None

    csv_file.close()
    print(f'Processed {line_count} lines (including the header).')


def main():

    # Expected User Input

    # python3 cpr.py [command] {params | -b file}
    # python3 cpr.py login [ip] [port] [user]
    # python3 cpr.py [publish]
    # python3 cpr.py [discard]
    # python3 cpr.py [logout]
    # python3 cpr.py add-host name [name] [ipv4] 
    # csv mode
    # python3 cpr.py [command] -csv [filename.csv]
    # python3 cpr.py add-host -csv [filename.csv]
    # python3 cpr.py delete-host -csv deletehosts.csv

    if len(argv) == 1:
        help()
        return None

    command = argv[1]
    params = argv[2:]

    if command == 'login':
        setup(params)
        return None
    if command == 'help':
        detailed_help()
        return None

    # Other commands mean we should already be logged in. let's get that data
    try:
        session_data = get_session_data(session_file)
        address, port, sid = session_data[0], session_data[1], session_data[2]
    except:
        print('\nLogin first please')
        help()
        return None

    # digest parameters from user to make payload
    # are we given file or command line input?
    if (len(params) != 0) and (params[0] == '-csv'):
        # filemode
        csv_mode(command, params, address, port, sid)
    else:
        # parse user command line input
        payload = get_payload(params)
        #print(payload)
        # make POST 
        response = api_call(address, port, command, payload, sid)
        # deal with response
        resp_code = handle_response(command, response)
        # if logout, clear the session file; only if we successfully logged out
        if (command == 'logout') and ('200' == resp_code):
            session_fd = open(session_file, 'w')
            session_fd.truncate()
            session_fd.close()
            print("Cleared session file")

if __name__ == '__main__':
    main()
