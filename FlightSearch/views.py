from django.shortcuts import render, redirect

from .forms import FlightSearchForm
from .points_gpt import PointsGPT

# Create your views here.
def homepage(request):
    context = {
        'forms': {
            'FlightSearchForm': FlightSearchForm()
        }
    }
    if request.method == 'GET':
        error_code = request.GET.get('error')
        if error_code is not None and error_code == 'boeing737max8':
            context['alert'] = {
                'message': 'Invalid search query. Please try again.',
                'type': 'danger'
            }
    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            return redirect(f"/search/?q={form.cleaned_data.get('search_query', '')}")
    return render(request, 'FlightSearch/homepage.html', context=context)

def searchpage(request):
    context = {
        'flights': []
    }
    query =  request.GET.get('q', '')
    print(query)
    search_args = PointsGPT.parse_args(query)
    print(search_args)
    if search_args is None:
        return redirect('/?error=boeing737max8')
    result = PointsGPT.search_seats_aero_api(search_params=search_args)

    context['flights'] =  [f.to_json() for f in result]
    if not context['flights']:
        context['alert'] = {
            'message': 'No flights found. Please try again.',
            'type': 'danger'
        }
    return render(request, 'FlightSearch/search_page.html', context=context)

