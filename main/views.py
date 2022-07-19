from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .models import Order, Item
from .forms import CreateForm
import pandas, os

# import sys
# sys.path.append("C:/Users/ti/Desktop/web_manager/modules")
#from packing.src.classes.relatorio import criarRelatorio

from modules.pipedrive.pipedrive import Pipedrive 
from modules.auvo.auvo import Auvo_api 
from modules.sysop.sysop import Sysop
from modules.packing.src.classes.relatorio import Relatorio
from modules.packing.src.modules.functions import selectPath

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
        print(response.POST)
        
        if response.POST.get('create'):
            number = response.POST.get('order')
            print(number)
            if not Order.objects.filter(order_number=number).exists():
                t = Order(order_number=number)
                t.save()
            else:
                t = Order.objects.get(order_number=number)

            df = packing_inst.criarRelatorio("260", "Embalagem")
            df['IdItem'] = df['IdItem'].replace([''],0)

            if t.item_set.all().exists():
                records = t.item_set.all()
                records.delete()
            
            for id in df.index:
                t.item_set.create(idItem = df['IdItem'][id],nome = df['Nome'][id],volume = df['Volume'][id],dimensao = df['Dimensao'][id],item = df['Item'][id],largura = df['Largura'][id] * 1000,altura = df['Altura'][id] * 1000,ambiente = df['Ambiente'][id],modelo = df['Modelo'][id],colecao = df['Colecao'][id],cor= df['Cor'],acion= df['Acionamento'],quant= 0,tubo= df['Tubo'][id],perfil = df['Perfil'][id],tipo= df['Tipo'], pos=df['Posicao'][id], peso=df['Peso'][id])
            
            if t.id_pipe != 0:
                inst.createActivity(t.id_pipe)
            
            return render(response, 'main/packing.html', {'order':t}) 
        
        if response.POST.get('download'):
            print("downloaded")
            # Define the full file path
            filepath =  selectPath("260")
            if os.path.exists(filepath):
                with open(filepath, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(filepath)
                    return response

    return render(response, "main/packing.html", {'order':False})


def packingView(response, id):
    t = Order.objects.get(order_number=id)
    return render(response, "main/packingView.html", {'order':t})