import requests, json

def api_call(ip_addr, port, command, json_payload, sid):

    # build url
    url = 'https://' + ip_addr + ':' + port + '/web_api/' + command

    # check we have sid
    if sid == '':
        # if empty, then we should be logging in
        request_headers = {'Content-Type' : 'application/json'}
    else:
        # otherwise, add sid to X-chkp-sid field in header
        request_headers = {'Content-Type' : 'application/json', 'X-chkp-sid' : sid}

    # make the post request to server
    r = requests.post(url,data=json.dumps(json_payload), headers=request_headers, verify=False)

    #debug_data = json.dumps(json_payload)
    #print(debug_data)
    return r

def login(user, password, addr, port):
    
    payload = {'user': user, 'password': password}

    response = api_call(addr, port, 'login', payload, '')

    code = str(response.status_code)

    if code != '200':
        print("Problem logging in")
        print(response.json())
        return None
    
    data = response.json()

    return data["sid"]