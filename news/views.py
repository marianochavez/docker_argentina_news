from django.shortcuts import redirect, render
import requests
from .models import City
from .forms import CityForm


def home(request):

    # ------------------------------------ WEATHER API -----------------------------------------------

    weather_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&lang=es&appid=a155afeb5257381947fea91631337691'
     
    if request.method == 'POST':
            form = CityForm(request.POST)
            if form.is_valid():
                form.save()
            return redirect('home')

    form = CityForm()

    # last 3 cities
    cities = City.objects.all().order_by('-id')[:3][::-1]
    # cities = City.objects.all()

    weather_data = []

    for city in cities:

        try:
            city_weather = requests.get(weather_url.format(city)).json()

            if city_weather['cod'] == "404":
                # La ciudad ingresada no exite, la elimino de la base y recargo pagina
                city_error = City.objects.get(name=city)
                print(f'No existe:{city_error}')
                city_error.delete()
                return redirect("home")

            weather = {
                'city' : city,
                'temperature' : city_weather['main']['temp'],
                'temperature_max': city_weather['main']['temp_max'],
                'temperature_min': city_weather['main']['temp_min'],
                'description' : city_weather['weather'][0]['description'],
                'icon' : city_weather['weather'][0]['icon'],
                'country': city_weather['sys']['country'],
                'feels_like': city_weather['main']['feels_like'],
                'humidity': city_weather['main']['humidity']
            }

            weather_data.append(weather)

        except Exception:
            pass

    # ------------------------------------ COVID API-----------------------------------------------

    covid_url = "https://covid-19-data.p.rapidapi.com/country"

    covid_querystring = {"name":"argentina"}

    covid_headers = {
    'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
    'x-rapidapi-key': "01bd746841mshdd8087279d8e13ep16808cjsnc6581bea947b"
    }

    covid_response = requests.request("GET", covid_url, headers=covid_headers, params=covid_querystring).json()

    covid_data = {
        'country': covid_response[0]['country'],
        'confirmed': covid_response[0]['confirmed'],
        'recovered': covid_response[0]['recovered'],
        'deaths': covid_response[0]['deaths']
    }

    # ------------------------------------ NEWS API -----------------------------------------------

    news_url = 'https://newsapi.org/v2/top-headlines?country=ar&apiKey=bfc611e9f0aa4ee7a389121fd7704076&pageSize=9&page=1'

    last_news = requests.get(news_url).json()

    news_data = []

    for news in last_news['articles']:
        
        report = {
            'source': news['source']['name'],
            'title' : news['title'],
            'description': news['description'],
            'url': news['url'],
            'urlToImage': news['urlToImage'],
            'published': news['publishedAt']
        }

        news_data.append(report)

    # ----------------

    context = {'weather_data' : weather_data, 'covid_data': covid_data, 'news_data': news_data, 'form' : form}

    return render(request, 'index.html', context)

def city_delete(request,city_id):
    
    city = City.objects.get(id=city_id)
    city.delete()

    return redirect("home")