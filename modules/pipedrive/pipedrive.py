# This file will contain the class that represents the pipedrive
import sys
import requests
sys.path.append("C:/Users/ti/Desktop/web_manager/modules")
import constants as const

class Pipedrivre:
    def __init__(self):
        pass

    def getCostumers(self):
        request = requests.get(f'https://reflexapersianas.pipedrive.com/api/v1/persons?api_token='+const.PIPE_TOKEN)
        request = request.json()
        request = request['data']


inst = Pipedrivre()
inst.getCostumers()