from django.db import models

# Create your models here.

class Order(models.Model):
    order_number = models.IntegerField()
    client = models.CharField(max_length=30, blank=True)
    id_pipe = models.IntegerField(default=0, blank=True)

    def __str__(self) -> str:
        return str(self.order_number)

class Item(models.Model):
    pedido = models.ForeignKey(Order, on_delete=models.CASCADE)
    idItem = models.IntegerField()
    nome = models.CharField(max_length=30)
    volume = models.IntegerField()
    dimensao = models.CharField(max_length=30)
    item = models.CharField(max_length=5)
    largura = models.IntegerField(default=0)
    altura =  models.IntegerField(default=0)
    ambiente = models.CharField(max_length=30, default='')
    modelo =  models.CharField(max_length=30)
    colecao = models.CharField(max_length=30)
    cor    =  models.CharField(max_length=30)
    acion  =  models.CharField(max_length=30)
    quant  =  models.IntegerField()
    tubo   =  models.CharField(max_length=30)
    perfil =  models.CharField(max_length=30)
    altCom =  models.FloatField(default=0)
    tipo   =  models.CharField(max_length=30)
    pos    =  models.FloatField(default=0)
    peso    = models.FloatField(default=0)
