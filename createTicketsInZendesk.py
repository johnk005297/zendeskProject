import json
import requests
import time


def getData():

    user = 'login@domain.com' + '/token'
    pwd = ''
    headers = {'content-type': 'application/json'}

    organizationsUrl = "https://domain.zendesk.com/api/v2/organizations.json"
    ticketsUrl = "https://domain.zendesk.com/api/v2/tickets.json"
    usersUrl = "https://domain.zendesk.com/api/v2/users.json"

    organizationId_and_usersId = dict() ### Main dictionary for Update tickets
    listOfOrganizationsId = list()
    listOfOrganizationsNames = ""   ### In case we need to look at the list of the Organizations ###
    organizationIdAndName = dict()

    while organizationsUrl is not None:

        # Do the HTTP get request
        r = requests.get(organizationsUrl, auth=(user, pwd), headers=headers)

        # Check for HTTP codes other than 200
        if r.status_code != 200:
            print('Status:', r.status_code, 'Problem with the request. Exiting.')
            exit()

        # Decode the JSON response into a dictionary and use the data
        data = r.json()

        # Set good json view (форматированная строка JSON) if we want to see the structure
        js = json.dumps(data, sort_keys=False, indent=2)

        ### Only current clients and ONLY mainstream ###
        for line in data["organizations"]:
            if line["organization_fields"]["currentclient"] is True and line["organization_fields"]["custom_client"] is False and line["organization_fields"]["english"] is False:
                listOfOrganizationsId.append(line["id"])
                listOfOrganizationsNames += (line["name"]) + "\n"
                if line["id"] not in organizationIdAndName:
                    organizationIdAndName[line["id"]] = line["name"]


        organizationsUrl = data["next_page"]

        # Now we have list of Organizations Id #


    while usersUrl is not None:

        # Do the HTTP get request
        r = requests.get(usersUrl, auth=(user, pwd), headers=headers)

        # Check for HTTP codes other than 200
        if r.status_code != 200:
            print('Status:', r.status_code, 'Problem with the request. Exiting.')
            exit()

        # Decode the JSON response into a dictionary and use the data
        data = r.json()

        # Set good json view (форматированная строка JSON) if we want to see the structure
        js = json.dumps(data, sort_keys=False, indent=2)

        ### Getting the dictionary of organizationID: [user(s)] - ONLY currentclient and mainstream client ###
        for line in data["users"]:
            if line["user_fields"]["updateinfo"] is True and line["organization_id"] in listOfOrganizationsId:
                if line["organization_id"] not in organizationId_and_usersId:
                    organizationId_and_usersId[line["organization_id"]] = []
                organizationId_and_usersId[line["organization_id"]] += [line["id"]]

        usersUrl = data["next_page"]
    return organizationId_and_usersId, organizationIdAndName  ### The dictionary of organizationID: [user(s)]

fromGetDataFunc = getData()

# fromGetDataFunc[0] = organizationId_and_usersId
# fromGetDataFunc[1] = organizationIdAndName

def createNewTicket(fromGetDataFunc):

    # Set the request parameters
    url = 'https://boardmaps.zendesk.com/api/v2/tickets.json'
    user = 'ikutuzov@boardmaps.com' + '/token'
    pwd = 'PwWDWXQYQvTKglDHagRF12fOkrZGMtPkWO0MXyQ4'
    headers = {'content-type': 'application/json'}

    subject = 'Enter the title'
    body = '''
            Enter the text body message here

	      '''

    # Package the data in a dictionary matching the expected JSON
    count = 0
    for key,value in fromGetDataFunc[0].items():
        data = {
                'ticket': {
                        "subject": subject,
                        "comment": { 'body': body  },
                        "priority": "low", # Possible priorities values: "urgent", "high", "normal", "low"
                        "status": "new", # Possible values: "new", "open", "pending", "hold", "solved", "closed"
                        "organization_id": key,
                        "requester_id": value[0],
                        "collaborator_ids": value[1:],
                        "submitter_id": 368808167351,
                        "tags": "обновление_системы",
                        "is_public": True,
                        "type": "task",  #"problem", "incident", "question" or "task"
                        "custom_fields": [{"id": 25092043, "value": "3"},{"id": 360000317531, "value": "обновление_системы"}]
                          }
                }
        count += 1
        # Transform the data to create a JSON payload
        payload = json.dumps(data)

        # Do the HTTP post request
        r = requests.post(url, data=payload, auth=(user, pwd), headers=headers)

        # Check for HTTP codes other than 201 (Created)
        if r.status_code != 201:
            print('Status:', r.status_code, 'Problem with the request. Exiting.')
            exit()

        # Report if success
        if key in fromGetDataFunc[1]:
            print(count, fromGetDataFunc[1].get(key))
        time.sleep(1)
        print("\n\nDone! Total tickets", count)


createNewTicket(fromGetDataFunc)
