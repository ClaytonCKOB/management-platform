from django.shortcuts import render, redirect
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse
from .models import Order, Item
import pandas, os
from math import ceil

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
        order_number = response.POST.get('order')

        # Case when a new report is created
        if response.POST.get('search'):

            # Verifing if the order already exists
            if not Order.objects.filter(order_number=order_number).exists():
                t = Order(order_number=order_number)
                t.save()
            else:
                t = Order.objects.get(order_number=order_number)


            df = packing_inst.criarRelatorio("260", "Embalagem")
            df['IdItem'] = df['IdItem'].replace([''],0)
            difVol = list(df['Volume'].unique())
            difDim = list(df['Dimensao'].unique())

            # Verifing if the order has itens
            if t.item_set.all().exists():
                records = t.item_set.all()
                records.delete()
            
            # Inserting the values in the database
            for id in df.index:
                t.item_set.create(idItem = df['IdItem'][id],nome = df['Nome'][id],volume = df['Volume'][id],dimensao = df['Dimensao'][id],item = df['Item'][id],largura = df['Largura'][id] * 1000,altura = df['Altura'][id] * 1000,ambiente = df['Ambiente'][id],modelo = df['Modelo'][id],colecao = df['Colecao'][id],cor= df['Cor'],acion= df['Acionamento'],quant= 0,tubo= df['Tubo'][id],perfil = df['Perfil'][id],tipo= df['Tipo'], pos=df['Posicao'][id], peso=df['Peso'][id])
            
            if t.id_pipe != 0:
                inst.createActivity(t.id_pipe)

            # Organizing the dimensions
            dims = []
            dimensoes = {}

            for vol in difVol:
                dims.append((df.loc[df['Volume'] == vol, 'Dimensao']).iloc[0])

            for i in difDim:
                dimensoes[i] = dims.count(i)

            chosenOnes = []
            for i in difVol:
                itens = list(t.item_set.filter(volume=i))
                chosenOnes.append(itens[ceil(len(itens)/2) - 1].id)



            # Organizing the weight
            pesos = {i: (round(float(df.loc[df['Volume'] == i, ['Peso']].sum()) * 100) / 100) for i in difVol}
            df.reset_index(inplace=True)
            indexDelRows = list(df[df['Tipo'] == 'Caixa'].index)
            df = df.drop(indexDelRows)

            pesoTotal = {}
            
            for i in range(len(pesos)+1):
                if i == 0:
                    pesoTotal['Total'] = round(sum(pesos.values())*100)/100
                else:
                    pesoTotal[i] = pesos[i]

            return render(response, 'main/packing.html', {'order':t, 'dims':dimensoes, 'pesos':pesoTotal, 'chosenOnes':chosenOnes}) 
        
        if response.POST.get('download'):
            filepath =  selectPath(order_number)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(filepath)
                    return response
                
        if response.POST.get('save_changes'):
            answer = dict(response.POST)
            changed_itens = {}
            val  = str(response.POST.get('save_changes'))
            num = int(val.split('|')[1])
            t = Order.objects.get(order_number=num)

            for id, value in answer.items():
                if value[0] != '' and id != "csrfmiddlewaretoken" and id != "save_changes":
                    if id[0] == 'v':
                        # Get the dimensions of the new box
                        query = t.item_set.filter(volume=value[0]).first()
                        
                        # Change the dimension of the item
                        itemToUpd = t.item_set.get(id=id[1:len(id)])
                        itemToUpd.dimensao = query.dimensao
                        
                        # Change the box of the item
                        itemToUpd.volume = value[0]
                        itemToUpd.save()

                    else:
                        changed_itens[id] = value

            # Treating the case when the dimension of a box is changed
            for id, value in changed_itens.items():
                itemToUpd = t.item_set.get(id=id[1:len(id)])
                query = t.item_set.filter(volume=itemToUpd.volume)
                for i in query:
                    print(i.volume)


    return render(response, "main/packing.html", {'order':False})


def packingView(response, id):
    t = Order.objects.get(order_number=id)
    number = id
    print(number)
    if not Order.objects.filter(order_number=number).exists():
        t = Order(order_number=number)
        t.save()
    else:
        t = Order.objects.get(order_number=number)

    df = packing_inst.criarRelatorio("260", "Embalagem")
    df['IdItem'] = df['IdItem'].replace([''],0)
    difVol = list(df['Volume'].unique())
    difDim = list(df['Dimensao'].unique())

    if t.item_set.all().exists():
        records = t.item_set.all()
        records.delete()
    
    for id in df.index:
        t.item_set.create(idItem = df['IdItem'][id],nome = df['Nome'][id],volume = df['Volume'][id],dimensao = df['Dimensao'][id],item = df['Item'][id],largura = df['Largura'][id] * 1000,altura = df['Altura'][id] * 1000,ambiente = df['Ambiente'][id],modelo = df['Modelo'][id],colecao = df['Colecao'][id],cor= df['Cor'],acion= df['Acionamento'],quant= 0,tubo= df['Tubo'][id],perfil = df['Perfil'][id],tipo= df['Tipo'], pos=df['Posicao'][id], peso=df['Peso'][id])
    
    if t.id_pipe != 0:
        inst.createActivity(t.id_pipe)

    # Organizing the dimensions
    dims = []
    dimensoes = {}

    for vol in difVol:
        dims.append((df.loc[df['Volume'] == vol, 'Dimensao']).iloc[0])

    for i in difDim:
        dimensoes[i] = dims.count(i)

    chosenOnes = []
    for i in difVol:
        itens = list(t.item_set.filter(volume=i))
        chosenOnes.append(itens[ceil(len(itens)/2) - 1].id)



    # Organizing the weight
    pesos = {i: (round(float(df.loc[df['Volume'] == i, ['Peso']].sum()) * 100) / 100) for i in difVol}
    df.reset_index(inplace=True)
    indexDelRows = list(df[df['Tipo'] == 'Caixa'].index)
    df = df.drop(indexDelRows)

    pesoTotal = {}
    
    for i in range(len(pesos)+1):
        if i == 0:
            pesoTotal['Total'] = round(sum(pesos.values())*100)/100
        else:
            pesoTotal[i] = pesos[i]

    return render(response, "main/packingView.html", {'order':t, 'dims':dimensoes, 'pesos':pesoTotal, 'chosenOnes':chosenOnes})