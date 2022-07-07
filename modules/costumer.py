# This file contains the class of a costumer

from dataclasses import dataclass
from unidecode import unidecode

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
    auvo: bool
    sysop: bool
    id: int
    

    def __str__(self):
        return f'{self.name} - {self.cpf_cnpj} - {self.street} - {self.district} - {self.city} - {self.state}'

    def compareCostumers(self, costumer2):
        """
            Will compare two costumers and will return the percent of similarity
        
        :Args
            costumer2 -> Costumer 

        """

        # Compare cpf_cnpj
        per_cpf = self.compareCpfCnpj(costumer2.cpf_cnpj)

        # Compare name
        per_name = self.compareText(self.name, costumer2.name)

        # Compare address
        per_address = self.compareAddress(costumer2.street, costumer2.city, costumer2.district, costumer2.state)
        


        return (per_cpf + per_name + per_address)/3

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

        big_name = text1 if len(text1) > len(text2) else text2
        small_name = text1 if len(text1) < len(text2) else text2

        contains_word = 0
        contains_letter = 0


        for word in small_name:
            if word in big_name:
                contains_word += 1

            else:
                # If the word is not in the big name verify if the letters are similary
                for w in big_name:
                    if len(w) != len(word):
                        small_word = word if len(word) < len(w) else w
                        big_word = word if len(word) > len(w) else w
                    else:
                        small_word = w
                        big_word = word

                    # The difference between the letter must smaller or equal to two
                    if len(big_word) - len(small_word) <= 2:
                        
                        for letter in small_word:
                            if letter in big_word:
                                contains_letter += 1

                        if len(small_word) != 0:
                            if contains_letter/len(small_word) >= 0.9:
                                contains_letter = 0
                                contains_word += 1


        return contains_word/len(small_name)
        

    def compareAddress(self, street2, city2, district2, state2):
        """
            Will compare the street, city and state
        """

        per_street = self.compareText(self.street, street2)
        per_city =   self.compareText(self.city, city2)
        per_district =   self.compareText(self.district, district2)
        per_state =  self.compareText(self.state, state2)

        return (per_street + per_city + per_district + per_state)/4



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
    cnpj: str
    street_number: int = None
    street: str = None
    district: str = None
    city: str = None
    state: str = None
    address: str = None
    

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
    costumer: CostumerPipe = None

    def __post_init__(self):
        index = 0
        length = len(self.title)

        # Removing the code of the deal
        if '(' in self.title:
            for i in range(length):
                if self.title[i] == ')':
                    index = i
            self.title = self.title[index+1:length] if length != index + 1 else self.title


