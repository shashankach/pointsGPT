from django import forms

class FlightSearchForm(forms.Form):
    search_query = forms.CharField(
        label='Enter Prompt Below',
        widget=forms.Textarea(attrs={
            'rows': 10, 
            'cols': 40, 
            'class': 'form-control'
        })
    )


