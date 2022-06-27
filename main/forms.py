from django import forms

class CreateForm(forms.Form):
    order = forms.CharField(label="Pedido", max_length=10)
