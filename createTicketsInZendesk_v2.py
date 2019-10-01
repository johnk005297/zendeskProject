import json
import requests
import time
import os
import sys

class zendesk:
    
    organizationIdAndName = dict()
    organizationId_and_usersId = dict()

    user = 'login@domen' + '/token'
    pwd = 'token'
    headers = {'content-type': 'application/json'}

    organizationsUrl = "https://company.zendesk.com/api/v2/organizations.json"
    ticketsUrl = "https://company.zendesk.com/api/v2/tickets.json"
    usersUrl = "https://company.zendesk.com/api/v2/users.json"

    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "update_message.txt")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            subject = file.readline()
            body = file.read()
    else:
        print("There is no such file 'update_message.txt' here. Check it!")
        sys.exit(0)



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

            ### Only current clients and ONLY mainstream ###
            for line in data["organizations"]:
                if line["organization_fields"]["current_client"] is True and line["organization_fields"]["custom_server_version"] is False and line["organization_fields"]["custom_localization"] is False:
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
            
            ### Getting the dictionary of organizationID: [user(s)] - ONLY current_client and mainstream client ###
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
                            "tags": "system_update", "обновление_системы"
                            "is_public": True,
                            "type": "task",  #"problem", "incident", "question" or "task"
                            "custom_fields": [{"id": 25092043, "value": "3"},{"id": 360000317531, "value": "обновление_системы"}]
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

        print("\nDone! Total tickets: " + str(count))

        

    def main(self):  
        start = time.time()              
        z = zendesk()
        z.getOrganizationIdAndName()          # Getting a dictionary {int[organizationId]:str"organizationName"}
        z.getOrganizationId_and_usersId()       # Getting a dictionary {int[organizationId]:int[usersId]}, users only with updateinfo flag!
        z.createNewTicket()                     # Method creates multiple tickets and assign them to users with updateinfo flags!
        end = time.time()
        print("\nTotal time: " + str(round(end - start, 3)) + "seconds")

if __name__ == "__main__":
    zendesk().main()

