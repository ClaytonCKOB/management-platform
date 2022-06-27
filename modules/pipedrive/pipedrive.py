# This file will contain the class that represents the pipedrive
import sys
import requests
sys.path.append("C:/Users/ti/Desktop/web_manager/modules")
import constants as const
from costumer import Costumer

class Pipedrivre:
    def __init__(self):
        self.costumers = []

    def getCostumers(self):
        """
            Will request to the api all the costumers
        """
        response = requests.get(f'https://reflexapersianas.pipedrive.com/api/v1/persons?api_token='+const.PIPE_TOKEN)
        response = response.json()
        response = response['data']

        return response

    def createCostumers(self, costumers):
        """
            Given a list of costumers, will create objects of the class Costumer
        """

        for i in costumers:
            if i['org_id'] is not None and i['org_id']['address'] is not None:
                separator = '|' if '|' in i['org_id']['address'] else ',' 
                address = i['org_id']['address'].split(separator)
                street = address[0]
                district = address[1]
                city = address[2].split(' - ')[0]

                try:
                    state = address[2].split(' - ')[1]
                except:
                    state = address[3] if len(address) >= 4 else ''

            self.costumers.append(Costumer(i['name'], '', i['add_time'], i['phone'][0]['value'].replace("(", "").replace(")", ""), street, district, city, state, [i['email'][0]['value']]))
        for i in self.costumers:
            print(i)

inst = Pipedrivre()
costumers = inst.getCostumers()
inst.createCostumers(costumers)