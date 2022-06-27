# This file will contains all the methods related with the sysop
import pyodbc
import os
import sys

sys.path.append("C:/Users/ti/Desktop/web_manager/modules")
from costumer import Costumer


class Sysop():
    def __init__(self):
        self.costumers = []

        db_path = os.environ["DB_PATH"]
        self.conn = pyodbc.connect(r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
                                   f"DBQ={db_path};")
        self.cursor = self.conn.cursor()
    
    def getCostumers(self):
        """
            Will request to the database the list of costumers
        """

        costumers = self.cursor.execute("SELECT cliente, CNPJ, dt_visita, Fone, endereco, num, Bairro, Cidade, UF, mail FROM t_cliente WHERE IDCad > 3000").fetchall()
        return costumers
    
    def createCostumers(self, request:list):
        """
            Will create the costumers from the request
        
        :Args
            request: list
        """
        for costumer in request:
            for x in range(len(costumer)):
                costumer[x] = costumer[x] if costumer[x] is not None else ""
            self.costumers.append(Costumer(costumer[0], costumer[1], costumer[2], costumer[3], str(costumer[4]) + " " + str(costumer[5]), str(costumer[6]), str(costumer[7]), str(costumer[8]), [costumer[9]]))


    def existsInSysop(self, costumer:Costumer):
        """
            Will compare the given costumer with all the costumers 
        """
        result = []
        
        for i in range(len(self.costumers)):
            response = self.costumers[i].compareCostumers(costumer)
            if response >= 0.9:
                result.append(self.costumer[i])
                
        if result != []:
            print("FOUND!")
            print(costumer)
            for i in result:
                print(i)
        else:
            print("NOT FOUND!")

        return result

if __name__ == "__main__":
    inst = Sysop()
    request = inst.getCostumers()
    inst.createCostumers(request)
    costumer = inst.costumers[25]
    inst.existsInSysop(costumer)