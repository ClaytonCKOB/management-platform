from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import CreateForm

# import sys
# sys.path.append("C:/Users/ti/Desktop/web_manager/modules")
#from packing.src.classes.relatorio import criarRelatorio

from modules.pipedrive.pipedrive import Pipedrive 
from modules.auvo.auvo import Auvo_api 
from modules.sysop.sysop import Sysop
from modules.packing.src.classes.relatorio import Relatorio

inst = Pipedrive()
inst.createDeals(inst.getDeals())

auvo = Auvo_api()
auvo.createCostumers(auvo.getCostumers())

sysop = Sysop()

packing_inst = Relatorio()

def index(response):
    return render(response, "main/base.html", {})

def client(response):
    return render(response, "main/clients.html", {'deals':inst.deals})

def auvoPage(response, id):
    similar = []
    for deal in inst.deals:
            if deal.id == id:
                similar = auvo.existsInAuvo(deal)

    if response.method == "POST":
        for deal in inst.deals:
            if deal.id == id:
                auvo.insertCostumer(deal)
                return redirect("/client/sysop/"+str(id))
    print(similar)
    return render(response, "main/auvo.html", {'deals':inst.deals, 'id':id, 'similar':similar})

def sysopPage(response, id):

    if response.method == "POST":
         for deal in inst.deals:
            if deal.id == id:
                order = sysop.createDeal(deal)
                inst.updateDeal(deal.id, order, deal.title)
                return redirect("/")

    return render(response, "main/sysop.html", {'deals':inst.deals, 'id':id})

def tracking(response):
    return render(response, "main/tracking.html", {})

def packing(response):
    if response.method == "POST":
        print(response.method)
        packing_inst.criarRelatorio("260", "Embalagem")

    return render(response, "main/packing.html")