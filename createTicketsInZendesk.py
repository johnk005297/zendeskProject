import json
import requests
import time


class zendesk:

    organizationIdAndName = dict()
    organizationId_and_usersId = dict()

    user = 'login@domain.com' + '/token'
    pwd = 'token'
    headers = {'content-type': 'application/json'}

    organizationsUrl = "https://domain.zendesk.com/api/v2/organizations.json"
    ticketsUrl = "https://domain.zendesk.com/api/v2/tickets.json"
    usersUrl = "https://domain.zendesk.com/api/v2/users.json"

    subject = 'Title of the ticket!'
    body = '''
            This is the text of the ticket you create.
          '''


    def getOrganizationIdAndName(self):

        while self.organizationsUrl is not None:

            # Do the HTTP get request
            r = requests.get(self.organizationsUrl, auth=(self.user, self.pwd), headers=self.headers)

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
                    if line["id"] not in self.organizationIdAndName:
                        self.organizationIdAndName[line["id"]] = line["name"]


            self.organizationsUrl = data["next_page"]
        return self.organizationIdAndName


    def getOrganizationId_and_usersId(self):

        while self.usersUrl is not None:

            # Do the HTTP get request
            r = requests.get(self.usersUrl, auth=(self.user, self.pwd), headers=self.headers)

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
                if line["user_fields"]["updateinfo"] is True and line["organization_id"] in self.organizationIdAndName:
                    if line["organization_id"] not in self.organizationId_and_usersId:
                        self.organizationId_and_usersId[line["organization_id"]] = []
                    self.organizationId_and_usersId[line["organization_id"]] += [line["id"]]

            self.usersUrl = data["next_page"]

        return self.organizationId_and_usersId


    def createNewTicket(self):

        # Package the data into a dictionary matching the expected JSON
        count = 0
        for key,value in self.organizationId_and_usersId.items():
            data = {
                    'ticket': {
                            "subject": self.subject,
                            "comment": { 'body': self.body  },
                            "priority": "low", # Possible priorities values: "urgent", "high", "normal", "low"
                            "status": "pending", # Possible status values: "new", "open", "pending", "hold", "solved", "closed"
                            "organization_id": key,
                            "requester_id": value[0],
                            "collaborator_ids": value[1:],
                            "submitter_id": 368808167351,
                            "tags": "add_tags",
                            "is_public": True,
                            "type": "task"  #"problem", "incident", "question" or "task"
                              }
                    }

            # Transform the data to create a JSON payload
            payload = json.dumps(data)

            # Do the HTTP post request
            r = requests.post(self.ticketsUrl, data=payload, auth=(self.user, self.pwd), headers=self.headers)

            # Check for HTTP codes other than 201 (Created)
            if r.status_code != 201:
                print('Status:', r.status_code, 'Problem with the request. Exiting.')
                exit()

            # Report if success
            if key in self.organizationIdAndName:
                count += 1
                print(count, self.organizationIdAndName.get(key))
            time.sleep(1)

        print("\n\nDone! Total tickets:", count)


z = zendesk()
z.getOrganizationIdAndName()           # Getting a dictionary {int[organizationId]:str"organizationName"}
z.getOrganizationId_and_usersId()      # Getting a dictionary {int[organizationId]:int[usersId]}, users only with updateinfo flag!
z.createNewTicket()                    # Method creates multiple tickets and assign them to users with updateinfo flags!
