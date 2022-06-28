from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import CreateForm

import sys
sys.path.append("C:/Users/ti/Desktop/web_manager/modules")
#from packing.src.classes.relatorio import criarRelatorio

from pipedrive.pipedrive import Pipedrive 

inst = Pipedrive()
inst.createCostumers(inst.getCostumers())


# Create your views here.

def index(response):
    return render(response, "main/base.html", {})

def client(response):
    return render(response, "main/clients.html", {'costumers':inst.costumers})

def tracking(response):
    return render(response, "main/tracking.html", {})

def packing(response):
    if response.method == "POST":
        form = CreateForm(response.POST)
        
        if form.is_valid():
            pass
            #criarRelatorio("9009", "Embalagem")
        else:
            form = CreateForm()
    return render(response, "main/packing.html", {'form':form})