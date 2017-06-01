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
    tipo = forms.CharField(max_length=50)
    produto = forms.CharField(max_length=50, required=False)
    quantidade = forms.IntegerField(required=False)
    data_field = forms.DateField(required=False)
    button = forms.CharField(max_length=10)

    def clean(self):
        cleaned_data = super(ProducaoData, self).clean()
        tipo = cleaned_data.get("tipo")
        produto = cleaned_data.get("produto")
        quantidade = cleaned_data.get("quantidade")
        button = cleaned_data.get("button")
        data_field = forms.DateField("data_field")

        if button == "add":
            if not (tipo and produto and quantidade):
                raise forms.ValidationError(
                "Didn't input all fields for add."
                )
        elif button == "filter":
            if quantidade and (not produto):
                raise forms.ValidationError(
                "Didn't input valid fields for filter."
                )
