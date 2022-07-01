# This file will contain the class that represents the pipedrive
import sys
import requests


sys.path.append("C:/Users/ti/Desktop/web_manager/modules")
import constants as const
from auvo.auvo import Auvo_api
from sysop.sysop import Sysop
from costumer import Costumer, CostumerPipe

class Pipedrive:
    def __init__(self):
        self.costumers = []

    def getCostumers(self):
        """
            Will request to the api all the costumers
        """
        response = requests.get('https://reflexapersianas.pipedrive.com/api/v1/persons:(id,name,add_time,phone,org_id,email)?filter_id=64&limit=20&sort=add_time DESC&api_token='+const.PIPE_TOKEN)
        response = response.json()
        response = response['data']

        return response

    def createCostumers(self, costumers):
        """
            Given a list of costumers, will create objects of the class Costumer
        """

        auvo = Auvo_api()
        auvo.createCostumers(auvo.getCostumers())
        
        #sysop = Sysop()
        #sysop.createCostumers(sysop.getCostumers())


        for i in costumers:
            if i['phone'][0]['value'] != "":
                phone = i['phone'][0]['value'].replace("(", "").replace(")", "").replace("+", "").replace(" ", "").replace("-", "")
                phone = phone if phone[0] != "0" else phone[1:len(phone)]
                phone = phone if phone[0:2] != "55" else phone[2:len(phone)]
                

            if i['org_id'] is not None and i['org_id']['address'] is not None:
                separator = '|' if '|' in i['org_id']['address'] else ',' 
                address = i['org_id']['address'].split(separator)
                street = address[0]
                district = address[1]
                city = address[2].split(' - ')[0] if len(address) >= 3 else ''

                try:
                    state = address[2].split(' - ')[1]
                except:
                    state = address[3] if len(address) >= 4 else ''
            else:
                street = ''
                district = ''
                city = ''
                state = ''

            response = auvo.existsInAuvo(Costumer(i['name'], '', i['add_time'], i['phone'][0]['value'].replace("(", "").replace(")", ""), street, district, city, state, [i['email'][0]['value']]))
            if response == []:
                self.costumers.append(CostumerPipe(i['name'], '', i['add_time'], phone, street, district, city, state, [i['email'][0]['value']], False, False, i['id']))
        
        for i in self.costumers:
            print(i)

