from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import CreateForm

import sys
sys.path.append("C:/Users/ti/Desktop/web_manager/modules")
#from packing.src.classes.relatorio import criarRelatorio

from pipedrive.pipedrive import Pipedrive 
from auvo.auvo import Auvo_api 
from sysop.sysop import Sysop

inst = Pipedrive()
inst.createDeals(inst.getDeals())

auvo = Auvo_api()

#sysop = Sysop()
# Create your views here.

def index(response):
    return render(response, "main/base.html", {})

def client(response):
    return render(response, "main/clients.html", {'deals':inst.deals})

def auvoPage(response, id):
    if response.method == "POST":
        for deal in inst.deals:
            if deal.id == id:
                print(auvo.insertCostumer(deal))
                print("redirect!!!!")
                return redirect("/client/sysop/"+str(id))

    return render(response, "main/auvo.html", {'deals':inst.deals, 'id':id})

def sysopPage(response, id):

    if response.method == "POST":
        for costumer in inst.costumers:
            if costumer.id == id:
                print("is valid!")
                #print(sysop.insertCostumer(costumer))
                return redirect("/")

    return render(response, "main/sysop.html", {'deals':inst.deals, 'id':id})

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