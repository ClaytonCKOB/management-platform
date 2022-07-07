# This file will contain the class that represents the pipedrive
import sys
import requests

sys.path.append("C:/Users/ti/Desktop/web_manager/modules")
import constants as const
from auvo.auvo import Auvo_api
from sysop.sysop import Sysop
from costumer import Costumer, CostumerPipe, Deal, Organization

class Pipedrive:
    def __init__(self):
        self.costumers = []
        self.deals = []

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


    def getDeals(self):
        """
            Will request the deals from the pipedrive
        """

        response = requests.get('https://reflexapersianas.pipedrive.com/api/v1/deals:(id,person_id,org_id,title,7a80f766077bc69dc36d870dc68ee41007fd28b8_street_number,7a80f766077bc69dc36d870dc68ee41007fd28b8_route,7a80f766077bc69dc36d870dc68ee41007fd28b8_sublocality,7a80f766077bc69dc36d870dc68ee41007fd28b8_admin_area_level_1,7a80f766077bc69dc36d870dc68ee41007fd28b8_admin_area_level_2,cc_email)?sort=add_time DESC&status=won&api_token='+const.PIPE_TOKEN)
        response = response.json()
        response = response['data']

        return response


    def getOrganization(self, id):
        """
            Will request the information of an organization
        """

        response = requests.get(f'https://reflexapersianas.pipedrive.com/api/v1/organizations/{id}?api_token='+const.PIPE_TOKEN)
        response = response.json()
        response = response['data']

        return response


    def getCostumer(self, id):
        """
            Will request the information of a single costumer
        """

        response = requests.get(f'https://reflexapersianas.pipedrive.com/api/v1/persons/{id}?api_token='+const.PIPE_TOKEN)
        response = response.json()
        response = response['data']

        return response


    def createDeals(self, request):
        """
            Will create the deal
        """
        for response in request:
            person = response['person_id']
            company = response['org_id']

            costumer = Costumer(person['value'], person['name'], person['email'][0]['value'], person['phone'][0]['value'])

            organization = Organization(company['name'], company['address'], company['value'], '') if company is not None else None

            self.deals.append(Deal(response['id'], response['title'], response['7a80f766077bc69dc36d870dc68ee41007fd28b8_street_number'],response['7a80f766077bc69dc36d870dc68ee41007fd28b8_route'], response['7a80f766077bc69dc36d870dc68ee41007fd28b8_sublocality'], response['7a80f766077bc69dc36d870dc68ee41007fd28b8_admin_area_level_1'], response['7a80f766077bc69dc36d870dc68ee41007fd28b8_admin_area_level_2'], response['cc_email'], organization, costumer))


if __name__ == "__main__":
    inst = Pipedrive()
    #response = inst.getDeals()
    #for i in response:
    #    inst.createDeal(i)
    #    print(i)

    #inst.getOrganization(7)
    inst.getCostumer(4180)