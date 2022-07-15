import pandas as pd
from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import datetime
from datetime import date, datetime
import time
import requests
import json
import sys


sys.path.append("C:/Users/ti/Desktop/web_manager/modules")
import constants as const
from costumer import Costumer, CostumerPipe, Deal, Organization



class Auvo_api():
    def __init__(self):
        self.costumers = []

        self.headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer '+ self.getAccessToken()
        }

    def getAccessToken(self) -> str:
        """
        Method will make a request to get the access Token
        """ 

        headers = {'Content-Type': 'application/json'}
        request = requests.get(f'https://api.auvo.com.br/v2/login/?apiKey={const.APP_KEY}&apiToken={const.TOKEN}', headers=headers)
        request = request.json()
        request = json.loads(json.dumps(dict(request['result']), indent=5))
        self.accessToken = request['accessToken']

        return self.accessToken

 
    def getUsers(self) -> dict:
        """
        Method will request the list of collaborators
        """
        users = {}

        request = requests.get(f'https://api.auvo.com.br/v2/users/?paramFilter={""}&page={1}&pageSize={10}&order={"asc"}&selectfields={""}', headers=self.headers)
        
        request = request.json()
        request = json.loads(json.dumps(dict(request['result']), indent=5))
        request = request['entityList']
        
        for user in request:
            if "Técnico de Instalação" in user['jobPosition']:
                users[user['name']] = user['userID']
        
        return users
    
    def getTeams(self) -> dict:
        """
        Method will request the list of teams
        """

        teams = {}

        request = requests.get(f'https://api.auvo.com.br/v2/teams/?paramFilter={""}&page={1}&pageSize={10}&order={"asc"}&selectfields={""}', headers=self.headers)
        
        request = request.json()
        request = json.loads(json.dumps(dict(request['result']), indent=5))
        request = request['entityList']
        
        for team in request:
            teams[team['description']] = team['teamUsers']
        
        return teams

    def getTasksId(self, date, collaborator):
        """
        Will request the list of tasks of the day and will return the ids of the ones that are 
        related to the km.

        :Args
            date: String -> represent the day that will be use in the request
            collaborator: String
        
        :Usage
            getTaskId('20/05/2022', 'clayton)

        """
        ids = []
        year = date[-4:]
        day = date[:2]
        date = year + '-' + date[3:len(date)-5] + '-' + day     # Converting the format of the date
        users = self.getUsers()
        id = users[collaborator]

        # Parameters
        paramFilter = {
            'startDate': date,
            'endDate': date,
            'idUserTo': id
        }

        paramFilter = json.loads(json.dumps(paramFilter))

        # Request
        request = requests.get(f'https://api.auvo.com.br/v2/tasks/?paramFilter={paramFilter}&page={1}&pageSize={10}&order={"asc"}', headers=self.headers)
        
        if request.status_code < 400 :
            # Converting the response to json
            request = request.json()
            request = json.loads(json.dumps(dict(request['result']), indent=5))
            request = request['entityList']

            # Searching for the ids where the word 'veiculo' is included
            for task in request:
                if 'VEÍCULO-' in task['customerDescription'] or 'VEÍCULO' in task['customerDescription']:
                    ids.append(task['taskID'])

        return ids
        
    def getTaskInfo(self, day, collaborator):
        """
        Will make a request to get the answers of the collaborators from the questionnaire
        
        :Args
            day: String -> represent the day that will be use in the request
            collaborator: String 
        
        :Usage
            getTaskInfo('20/05/2022', 'Clayton)

        """
        ids = self.getTasksId(day, collaborator)
        mileage = []

        for id in ids:
            request = requests.get(f'https://api.auvo.com.br/v2/tasks/{id}', headers=self.headers)
            request = request.json()
            request = json.loads(json.dumps(dict(request['result']), indent=5))

            if request['questionnaires'] != []:
                request = request['questionnaires'][0]['answers'][1]['reply']

                mileage.append(request)

        return mileage

    def getCostumers(self):
        """
            Will request the list of costumers  
        """

        request = requests.get(f'https://api.auvo.com.br/v2/customers/?paramFilter={""}&page={1}&pageSize={400}&order={"desc"}&selectfields={""}', headers=self.headers)
        request = request.json()
        request = json.loads(json.dumps(dict(request['result']), indent=5))
        request = request['entityList']
                
        return request

    def createCostumers(self, costumers_req:list):
        """
            Will create objects of the class Costumer
        
        :Args 
            costumers_req - list 
        """
        
        for costumer in costumers_req:
            address = costumer['address'].split(",")
            street = address[0]
            district = address[1] if len(address) >= 2 else ""
            state = address[2].split("-") if len(address) >= 3 else ["", ""]
            state = state if len(state) >= 2 else ["", ""]
            city = state[0]
            state = state[1]
            phoneNumber = costumer['phoneNumber'][0] if len(costumer['phoneNumber']) >= 1 else ""

            self.costumers.append(CostumerPipe(costumer['id'],costumer['description'], costumer['cpfCnpj'], costumer['creationDate'], phoneNumber, street, district, city, state, costumer['email']))


    def insertCostumer(self, costumer:Deal):
        """
            Will insert in the auvo's plataform
        
        :Args 
            costumer: Costumer
        """
        today = date.today()
        now = datetime.now()

        address = costumer.street + " - " + costumer.street_number + ", " + costumer.district + " - " + costumer.city + " - " + costumer.state if costumer.street is not None and costumer.state is not None else ""


        values = {
            "externalId": costumer.id,
            "name": costumer.title,
            "cpfCnpj": costumer.organization.cnpj,
            "phoneNumber": [
              costumer.costumer.phone
            ],
            "email": [costumer.email],
            "manager": "Ti",
            "managerJobPosition": "Developer",
            "note": "",
            "address": address,
            "latitude": 0,
            "longitude": 0,
            "maximumVisitTime": 1,
            "unitMaximumTime": 1,
            "groupsId": [],
            "managerTeamsId": [],
            "managersId": [],
            "segmentId": 0,
            "active": True,
            "adressComplement": "",
            "creationDate": f"{today.year}-{today.month}-{today.day}T{now.hour}:{now.minute}:{now.second}",
            "contacts": [],
            "dateLastUpdate": f"{today.year}-{today.month}-{today.day}T{now.hour}:{now.minute}:{now.second}",
            "attachments": []
        }

        

        response = requests.post('https://api.auvo.com.br/v2/customers/', json=json.loads(json.dumps(values)), headers=self.headers)
        return response


    def existsInAuvo(self, costumer:Costumer):
        """
            Will compare the given costumer with all the costumers 
        """
        result = []
        
        for i in range(len(self.costumers)):
            response = self.costumers[i].compareCostumers(costumer)
            if response >= 65:
                result.append([self.costumers[i], response])


                
        if result != []:
            changed = True
            while changed:
                changed = False
                for i in range(len(result)):
                    if i != len(result) - 1:
                        if result[i][1] < result[i+1][1]:
                            result[i+1][1], result[i][1] = result[i][1], result[i+1][1]
                            changed = True

        return result




class Auvo(Auvo_api):
    def __init__(self, driver_path=""):
        global driver
        self.driver_path = driver_path
        driver = webdriver.Chrome(self.driver_path)
        driver.minimize_window()

        self.site_open = False

        # Dict with the collaborators and their id
        self.collaborators = {}
    
    def __exit__(self):
        driver.quit()

    # Method to open the website of booking
    def openSite(self):
        driver.maximize_window()
        driver.get(const.SITE)
        self.site_open = True
        

    def loginAuvo(self):
        """
        Will insert the necessary information to execute the login.
        """
        
        # Finding the elements
        user_e = driver.find_element(By.CSS_SELECTOR, 'input[id="usuario"]')
        password_e = driver.find_element(By.CSS_SELECTOR, 'input[id="senha"]')
        btn_submit = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        # Clearing its content
        user_e.clear()
        password_e.clear()

        # Inserting the info
        user_e.send_keys(const.USER)
        password_e.send_keys(const.PASS)

        # Submit
        btn_submit.click()


    def goToRelatorios(self):
        """
        Will access the 'Relatorios' page
        """
        driver.implicitly_wait(10)
        btnRel = driver.find_element(By.ID, "controlaClique3")
        btnRel.click()

        opKmRodado = driver.find_element(By.CSS_SELECTOR, 'a[href="/kmRodado"]')
        opKmRodado.click()

    
    def getIntervalReport(self, begin, end, collaborator, is_collab) -> DataFrame:
        """
        Will collect the data in the defined interval

        :Args
            begin: String -> begin of the interval
            end: String -> end of the interval
            collaborator: String -> name of the collaborator

        :Usage
            getIntervalReport("16/05/2022", "18/05/2022", "clayton")
        """
        begin = begin.split("/")
        end = end.split("/")
        day = int(begin[0])
        month = int(begin[1])
        data = pd.DataFrame()

        # Getting the last day of the month
        next_month = datetime.date(int(begin[2]), int(begin[1]), 1).replace(day=28) + datetime.timedelta(days=4)
        last_day =  next_month - datetime.timedelta(days=next_month.day)
        last_day = last_day.strftime("%d")

        while (begin[1] == end[1] and day <= int(end[0])) or (begin[1] != end[1] and day != int(end[0]) + 1):
            self.selectDailyReport(str(day)+"/"+str(month)+"/"+end[2], collaborator, is_collab)
            time.sleep(8)
            data = pd.concat([data, self.getReportData(str(day)+"/"+str(month)+"/"+end[2], collaborator, is_collab)], axis=0)
            if day + 1 <= int(last_day):
                day += 1
            else:
                day = 1
                month += 1

        data = data.reset_index()

        return data

    def selectDailyReport(self, day, collaborator, is_collab):
        """
        Will generate the report of the collaborator in the specified day

        :Args
            day: String -> will specify the report's day
            collaborator: String -> name of the collaborator
            
        :Usage
            selectDailyReport('15/05/2022', 'clayton')

        """
        
        driver.implicitly_wait(10)

        # Select the begin of the interval
        begin_element = driver.find_element(By.ID, "dataInicio")
        begin_element.click()
        self.selectDayinTable(day)

        driver.implicitly_wait(10)
        # Select the end of the interval
        end_element = driver.find_element(By.ID, "dataFim")
        end_element.click()
        self.selectDayinTable(day)


        
        # Configuring the filter 
        filter_element = driver.find_element(By.ID, "select2-filtrarPor-container")
        filter_element.click()
        filter_input = driver.find_element(By.CLASS_NAME, "select2-search__field")

        if is_collab:
            # Select the collaborator
            filter_input.send_keys("Colaborador")
            filter_input.send_keys(Keys.ENTER)
            collab_element = driver.find_element(By.ID, "select2-listaColaboradores-container")
            collab_element.click()
            
        else:
            filter_input.send_keys("Equipe")
            filter_input.send_keys(Keys.ENTER)

            user_search_element = driver.find_element(By.ID, "select2-listaEquipes-container")
            user_search_element.click()

        user_search_element = driver.find_element(By.CLASS_NAME, "select2-search__field")
        user_search_element.click()
        user_search_element.send_keys(collaborator)
        user_search_element.send_keys(Keys.ENTER)

        # Click the submit button
        btn_get_report = driver.find_element(By.ID, "gerarConsulta")
        btn_get_report.click()


    def selectDayinTable(self, day):
        """
        Will select the day in the opened table

        :Args
            day: String -> the day that will be selected
        
        :Usage
            selectDayinTable('15/05/2022')

        """

        # Variables
        months = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        date = day.split('/')
        td_y = 1 if int(date[0]) < 15 else 3
        td_x = 1
        found = False

        # Select the month
        month_element = driver.find_element(By.CLASS_NAME, "datepicker-switch")
        month_in_num = months.index(month_element.text.split(' ')[0])

        while int(month_in_num) != int(date[1]):
            if int(month_in_num) < int(date[1]):
                next_element = driver.find_element(By.XPATH, "/html/body/div[5]/div[1]/table/thead/tr[2]/th[3]")
                next_element.click()
            else:
                prev_element = driver.find_element(By.CLASS_NAME, "prev")
                prev_element.click()
            
            month_element = driver.find_element(By.CLASS_NAME, "datepicker-switch")
            month_in_num = months.index(month_element.text.split(' ')[0])

        # Select the day
        while not found:
            end = driver.find_element(By.XPATH, f"/html/body/div[5]/div[1]/table/tbody/tr[{td_y}]/td[{td_x}]")
            
            if end.text == date[0]:
                end.click()
                found = True
            else:
                td_x += 1
                if td_x == 8:
                    td_x = 1
                    td_y += 1


    def getReportData(self, day, collaborator, is_collab) -> DataFrame:
        """
        Will get the atributes of the report

        :Args
            day: String -> will specify the report's day
            collaborator: String -> name of the collaborator
            
        :Usage
            getReportData('15/05/2022', 'clayton')
        """
        driver.implicitly_wait(20)

        if is_collab:
            # Finding the elements
            km_sistema = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr/td[3]')
            km_total = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr/td[5]')
            collab = collaborator
        else:
            # When it is a team the program needs to get the higher values
            first_km_total = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr/td[5]')
            second_km_total = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr[2]/td[5]')
            
            first_km_total = first_km_total.get_attribute("data-order")
            first_km_total = float(first_km_total[:len(first_km_total)-3] + "." + first_km_total[len(first_km_total)-3:])

            second_km_total = second_km_total.get_attribute("data-order")
            second_km_total = float(second_km_total[:len(second_km_total)-3] + "." + second_km_total[len(second_km_total)-3:])

            if first_km_total > second_km_total:
                km_sistema = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr/td[3]')
                km_total = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr/td[5]')

            else:
                km_sistema = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr[2]/td[3]')
                km_total = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr[2]/td[5]')

            collab = "Thiago Costa"


        # Treating each value
        km_sistema = km_sistema.get_attribute("data-order")
        km_sistema = float(km_sistema[:len(km_sistema)-3] + "." + km_sistema[len(km_sistema)-3:])       
        km_total = km_total.get_attribute("data-order")
        km_total = float(km_total[:len(km_total)-3] + "." + km_total[len(km_total)-3:])     

        # Get the data from the questionnaires 
        mileage = self.getTaskInfo(day, collab)
        beginCar = int(mileage[0]) if len(mileage) >= 1 and ('www' not in mileage[0].split('.') and 'apresentou' not in mileage[0].split(' ')) else 0
        endCar = int(mileage[1]) if len(mileage) >= 2 and ('www' not in mileage[1].split('.') and 'apresentou' not in mileage[1].split(' ')) else 0
        
        
        # Creating the dict with the info
        data = {
            "Nome": [collaborator.upper()],
            "Km Inicial Carro": [beginCar],
            "Km Final Carro": [endCar],
            "Km Sistema": [km_sistema],
            "Km Total": [km_total],
            "Data": [day], 
            "Comp. Auvo": [round((km_sistema - km_total)*100)/100],
            "Comp. Veículo": [round((km_total - (endCar - beginCar))*100)/100]
        }

        return pd.DataFrame(data)


if __name__ == "__main__":
    auvo = Auvo_api()

    df = auvo.getCostumers()

    #clayton = Costumer("Clayton", "ti@reflexapersianas.com.br", "51999999999")
    #org = Organization("Empresa", "sao lazaro", 9999, "62988868000107")
    deal = Deal(9999, "RDC Corretora de Seguros LTDA", 99, "Avenida Paulo Faccini", "Macedo", "Guarulhos", "São Paulo", "ti@reflexapersianas.com.br")
    auvo.createCostumers(df)
    auvo.existsInAuvo(deal)
    auvo.insertCostumer(deal)