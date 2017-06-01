from django import forms

# class ClassForm (forms.Form):
#     your_name = forms.CharField(label="Your Name", max_length=100, initial="Name")
#     your_email = forms.EmailField(label="Your Email", max_length=100)
#     your_question = forms.CharField(label="Your Question", max_length=1000)
#     your_image = forms.FileField(label="Your Image")

class UserForm (forms.Form):
    user_name = forms.CharField(max_length=20)
    user_password = forms.CharField(max_length=20)

class ProducaoData (forms.Form):
    Tipo = forms.CharField(max_length=50)
    Produto = forms.CharField(max_length=50)
    Quantidade = forms.IntegerField()
    Data = forms.DateField(required=False)
