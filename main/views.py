from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import CreateForm

import sys
sys.path.append("C:/Users/ti/Desktop/web_manager/modules")
#from packing.src.classes.relatorio import criarRelatorio

from pipedrive.pipedrive import Pipedrive 
from auvo.auvo import Auvo_api 

inst = Pipedrive()
inst.createCostumers(inst.getCostumers())

auvo = Auvo_api()


# Create your views here.

def index(response):
    return render(response, "main/base.html", {})

def client(response):
    return render(response, "main/clients.html", {'costumers':inst.costumers})

def auvoPage(response, id):
    form = CreateForm(response.POST)
    if response.method == "POST":

        for costumer in inst.costumers:
            if costumer.id == id:
                print("is valid!")
                auvo.insertCostumer(costumer)

    return render(response, "main/auvo.html", {'costumers':inst.costumers, 'id':id})

def tracking(response):
    return render(response, "main/tracking.html", {})

def packing(response):
    form = CreateForm(response.POST)
    if response.method == "POST":

        if form.is_valid():
            pass
            #criarRelatorio("9009", "Embalagem")
        else:
            form = CreateForm()
    return render(response, "main/packing.html", {'form':form})