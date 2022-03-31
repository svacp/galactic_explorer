from django import forms


class StatisticsForm(forms.Form):
    name = forms.BooleanField(label='name', required=False)
    height = forms.BooleanField(label='height', required=False)
    mass = forms.BooleanField(label='mass', required=False)
    hair_color = forms.BooleanField(label='hair_color', required=False)
    skin_color = forms.BooleanField(label='skin_color', required=False)
    eye_color = forms.BooleanField(label='eye_color', required=False)
    birth_year = forms.BooleanField(label='birth_year', required=False)
    gender = forms.BooleanField(label='gender', required=False)
    homeworld = forms.BooleanField(label='homeworld', required=False)
    date = forms.BooleanField(label='date', required=False)
