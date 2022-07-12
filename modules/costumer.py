# This file contains the class of a costumer

from dataclasses import dataclass
from unidecode import unidecode
from fuzzywuzzy import fuzz

@dataclass
class Costumer():
    id: int
    name: str
    email: str
    phone: str

@dataclass
class Organization():
    id: int
    name: str
    value: int
    address: str
    cnpj: str = None
    street_number: int = None
    street: str = None
    district: str = None
    city: str = None
    state: str = None
     
    

@dataclass
class Deal():
    id: int
    title: str
    street_number: int
    street: str
    district: str
    city: str
    state: str
    email: str
    organization: Organization = None
    costumer: Costumer = None

    def __post_init__(self):
        index = 0
        length = len(self.title)

        # Removing the code of the deal
        if '(' in self.title:
            for i in range(length):
                if self.title[i] == ')':
                    index = i
            self.title = self.title[index+1:length] if length != index + 1 else self.title



@dataclass
class CostumerPipe():
    name: str
    cpf_cnpj: str
    creationDate: str
    phoneNumber: str
    street: str
    district: str
    city: str
    state: str
    email: list
    

    def __str__(self):
        return f'{self.name} - {self.cpf_cnpj} - {self.street} - {self.district} - {self.city} - {self.state}'

    def compareCostumers(self, costumer2:Deal):
        """
            Will compare two costumers and will return the percent of similarity
        
        :Args
            costumer2 -> Costumer 

        """
        per_cpf = -1
        per_name = -1
        per_address = -1

        if costumer2.organization is not None and costumer2.organization.cnpj is not None and self.cpf_cnpj is not None:
            # Compare cpf_cnpj
            per_cpf = self.compareCpfCnpj(costumer2.organization.cnpj) if self.cpf_cnpj != '' and costumer2.organization.cnpj != '' else -1

        # Compare name
        per_name = self.compareText(self.name, costumer2.title) if self.name != '' and costumer2.title != '' else -1

        # Compare address
        per_address = self.compareAddress(costumer2.street, costumer2.city, costumer2.district, costumer2.state)
        
        values = [per_cpf, per_name, per_address]
        total = 0
        den = 0
        for i in values:
            if i != -1:
                total += i
                den += 1

        response = total/den if den != 0 else -1


        return response

    def compareCpfCnpj(self, cpf2):
        """
            Will compare the values, if equal return 1, else return 0
        """
        self.cpf_cnpj = self.cpf_cnpj.replace(" ", "").replace(".", "").replace("/", "")
        cpf2 = cpf2.replace(" ", "").replace(".", "").replace("/", "")

        if self.cpf_cnpj == cpf2 and cpf2 != '':
            return 1
        else:
            return 0
    

    def compareText(self, text1, text2):
        """
            Will compare the names of the costumers. When they are not exactly equal, the method will return the percente of similary
        """
        text1 = unidecode(text1.upper().replace("-", ""). replace("  ", " ")).split(" ")
        text2 = unidecode(text2.upper().replace("-", ""). replace("  ", " ")).split(" ")

        return fuzz.ratio(text1, text2)

        
    def compareAddress(self, street2, city2, district2, state2):
        """
            Will compare the street, city and state
        """

        per_street = self.compareText(self.street, street2)
        per_city =   self.compareText(self.city, city2)
        per_district =   self.compareText(self.district, district2)
        per_state =  self.compareText(self.state, state2)

        return (per_street + per_city + per_district + per_state)/4




#inst = CostumerPipe("Negócio Ana Paula Kloeckner", "", "", "", "", "", "", "", "", False, False, 3)
#print(inst.compareText("Av. Paulo Faccini, 939 - Macedo, Guarulhos - SP, 07111-000", "Avenida Paulo Faccini - Macedo - São Paulo - Guarulhos"))