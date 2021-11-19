from django import forms
from django.views.generic.edit import FormView

# class ReadFileForm(forms.Form):
#     file_field = forms.FileField()
    
#     #widget=forms.ClearableFileInput(attrs={'multiple': True})
#     your_name = forms.CharField(label='Your name', max_length=100)

max_file_uploads = 10

def make_ReadFileForm(n):
    fields = {}
    for i in range(n):
        fields[f"file_{str(i)}"] = forms.FileField(required=False)

    #from the docs I was reading:
    #type just wants to know the name of our new class (ContactForm), what classes, if any, it should inherit from (when doing this, use django.forms.BaseForm instead of django.forms.Form; the reasons are a bit obscure and technical, but any time you’re not declaring the fields directly on the class in the normal fashion you should use BaseForm) and a dictionary of attributes
    return type('ReadFileForm', (forms.BaseForm,), { 'base_fields': fields })

#this means we can dynamically adjust the number of forms created by changing the variable!
#
ReadFileForm = make_ReadFileForm(max_file_uploads)
