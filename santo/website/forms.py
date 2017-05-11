from django import forms

class ClassForm (forms.Form):
    your_name = forms.CharField(label="Your Name", max_length=100, initial="Name")
    your_email = forms.EmailField(label="Your Email", max_length=100)
    your_question = forms.CharField(label="Your Question", max_length=1000)
    your_image = forms.FileField(label="Your Image")
