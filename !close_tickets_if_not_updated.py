import json
import requests
import time
import os
import sys

class zendesk:
    
    tickets = list()    

    user = 'user@company.com' + '/token'
    pwd = 'token'
    headers = {'content-type': 'application/json'}
    organizationsUrl = "https://company.zendesk.com/api/v2/organizations.json"
    
    message = ''' Пишем сообщение... '''
 
            
    def getTickets(self):

        ticketsUrl = "https://company.zendesk.com/api/v2/tickets.json"
        while ticketsUrl is not None:

            resp = requests.get(ticketsUrl, auth=(self.user, self.pwd), headers=self.headers)
            if resp.status_code != 200:
                print("No good ", resp.status_code)
                exit()

            data = resp.json()
            for line in data["tickets"]:
                if line["status"] == "pending" and line["fields"][2]["value"] == "обновление_системы" and line["organization_id"] != 114113763252:                    
                    self.tickets.append(line["id"])                    
            
            ticketsUrl = data["next_page"]
        return self.tickets
        
    def closeTicketsAboutUpdates(self):
        count = 0
        for item in self.tickets:
            data = {
                    'ticket': {
                            "id": item,
                            "comment": {'body': self.message},                            
                            "status": "solved", # Possible status values: "new", "open", "pending", "hold", "solved", "closed"                            
                            "is_public": True                                                       
                          }
                    }

            payload = json.dumps(data)
            url = "https://company.zendesk.com/api/v2/tickets/" + str(item)+".json"
            r = requests.put(url, data=payload, auth=(self.user, self.pwd), headers=self.headers)

            # Check for HTTP codes other than 200 (Created)
            if r.status_code == 400 or r.status_code == 401:
                print('Status:', r.status_code, 'Problem with the request. Exiting.')
                exit()
            count += 1
            print("Ticket #" + str(item) + " is closed!")
            time.sleep(0.3)
        print()      
        print("Всё ок. Закрыто тикетов - " + str(count) + " шт.")
    
        
    def main(self):  

        start = time.time()
        z = zendesk()        
        z.getTickets()
        z.closeTicketsAboutUpdates()        
        end = time.time()
        print("\nTotal time: " + str(round(end - start, 3)) + "seconds")

if __name__ == "__main__":
    zendesk().main()
