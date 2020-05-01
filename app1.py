import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from geopy import geocoders
from geopy.distance import distance
from cities import cities_BL_coordinates, countries_BL_coordinates
import dash_html_components as html
import plotly.graph_objects as go
import plotly as plt
import locating_functions as lf
from dash.dependencies import Input, Output, State
import math, json
from description import aboutProject, projectNews
import pycountry
import random

desc = aboutProject
news = projectNews

# URLs for datasets
timestamp_dataset = 'https://raw.githubusercontent.com/dtandev/coronavirus/master/data/CoronavirusPL%20-%20Timeseries.csv'
general_dataset = 'https://raw.githubusercontent.com/dtandev/coronavirus/master/data/CoronavirusPL%20-%20General.csv'
hospitals_dataset = 'https://raw.githubusercontent.com/dtandev/coronavirus/master/data/CoronavirusPL%20-%20Isolation_wards.csv'

# create Data Framses based on csv files
generalDf = pd.read_csv(general_dataset)
generalDf["Timestamp"] = pd.to_datetime(generalDf["Timestamp"], format='%d-%m-%Y').dt.date
hospitalsDf = pd.read_csv(hospitals_dataset)
coronaDf = pd.read_csv(timestamp_dataset)
coronaDf["Timestamp"] = pd.to_datetime(coronaDf["Timestamp"], format='%d-%m-%Y')

coronaDfcaseI = coronaDf[coronaDf['Infection/Death/Recovery']=='I']
coronaDfcaseR = coronaDf[coronaDf['Infection/Death/Recovery']=='R']
coronaDfcaseD = coronaDf[coronaDf['Infection/Death/Recovery']=='D']

hospitalsDf['Szpital'] = hospitalsDf['Szpital'].apply(lambda x: x[:x.find(', ')]) # delete part of hospital name after ', '

# geolocator 
geolocator = geocoders.Nominatim(user_agent = 'dtansci@gmail.com')

# Dicts

cities_BL = cities_BL_coordinates
countries_BL = countries_BL_coordinates

# Maps

# Hospitals Map
hospitalsMap  = px.scatter_mapbox(hospitalsDf, lat = 'B', lon = 'L', mapbox_style = 'carto-positron' ,title = "Mapa szpitali zakaźnych w Polsce")
hospitalsMap.update_layout(height=550, paper_bgcolor = '#2b3e50', margin=dict(l=0, r=0, t=35, b=0), font = dict(color='white'), showlegend=False,)
address_bar = dbc.Input(id = "addressInputId", placeholder = "Podaj nazwę ulicy, miejscowość oraz kod pocztowy miejsca pobytu", value = 'Warszawa')



# Current state
currentCases = generalDf.tail(1)
currentCases['Active'] = currentCases['Confirmed']-currentCases['Deaths']-currentCases['Recovered']-1
currentCases = currentCases[['Timestamp', 'Confirmed', 'Active', 'Deaths', 'Recovered', 'In_the_hospital', 'In_quarantine', 'Under_medical_supervision', 'Number_of_tests_carried_out' ]]
currentCases.columns = ['Data', 'Potwierdzenia', 'Aktywne', 'Zgony', 'Wyleczeni', 'Hospitalizacje', 'Kwarantanna', 'Nadzór', 'Wykonane testy']

# Stats
# Data Frame preparation

generalDf.columns = ['Data', 'Potwierdzenia', 'Zgony', 'Wyleczeni', 'Hospitalizacje', 'Kwarantanna', 'Nadzór', 'Liczba testów']
coronaDf2 = coronaDf.groupby(['Timestamp', 'Province',]).count().reset_index().sort_values(by=['Timestamp'], ascending=True)

uniqProvinces = list(coronaDf['Province'].unique())
statement1 = coronaDf['Province'].isin(uniqProvinces)
sunburstDf = coronaDf[statement1].groupby(['Province', 'City', 'Infection/Death/Recovery']).count().reset_index()

def rename(x):
    if x == 'I':
        return 'Potwierdzony'
    elif x == 'R':
        return 'Wyleczony'
    elif x == 'D':
        return 'Zgon'

sunburstDf['Infection/Death/Recovery']= sunburstDf['Infection/Death/Recovery'].apply(lambda x: rename(x))


coronaDfGeneral = coronaDf.copy()
# konwersja to datetime i porządki
coronaDfGeneral["Timestamp"] = pd.to_datetime(coronaDfGeneral["Timestamp"], format='%d-%m-%Y')
coronaDfGeneral = coronaDfGeneral[(coronaDfGeneral["Timestamp"] > "2020-01-01") & (coronaDfGeneral["Timestamp"] < "2020-05-01")] # ta linijka czyści tylko dane z kilku błędnych pozycji - potem do wywalenia

# sortowanie i rozbicie na 3 kolumny
coronaDfGeneral = coronaDfGeneral.set_index(["Province", "Timestamp"]).sort_index()
coronaDfGeneral = pd.get_dummies(coronaDfGeneral["Infection/Death/Recovery"])

# agregacja do dni i skumulowana wartość
coronaDfGeneral = coronaDfGeneral.groupby(level=[0, 1]).sum().groupby(level=[0]).cumsum()

# jeśli koniecznie muszą być wszystkie daty/województwa
new_index = pd.MultiIndex.from_product(coronaDfGeneral.index.levels)
coronaDfGeneral = coronaDfGeneral.reindex(index=new_index)
coronaDfGeneral = coronaDfGeneral.unstack(level=0).ffill().stack(level=1).sort_index(level=1)
coronaDfGeneral = coronaDfGeneral.reset_index()
coronaDfGeneral['Active'] = coronaDfGeneral['I'] - coronaDfGeneral['D'] - coronaDfGeneral['R']

coronaDfGeneral.columns = ['Timestamp', 'Province', 'Death', 'Confirmed', 'Recovered', 'Active']

logFigData = generalDf[['Potwierdzenia']]
logFigData['Nowe potwierdzenia'] = 0
logFigData.columns = ['Potwierdzenia ogółem', 'Nowe potwierdzenia']
for i in range(1, len(logFigData['Potwierdzenia ogółem'])):
    logFigData.iloc[i,1] = logFigData.iloc[i,0] - logFigData.iloc[i-1,0]

# Figure preparation

infectedFig = go.Figure() # Figure with data about Infected/Death/Recovered

preventionFig = go.Figure() # Figure with data about Hospitalized/Tested/Supervised/In_quarantine

logFigPlot = go.Figure()

infectedFig.add_trace(go.Scatter(x = generalDf['Data'], y = generalDf['Potwierdzenia'], mode = 'lines+markers',name = 'Potwierdzenia'))
infectedFig.add_trace(go.Scatter(x = generalDf['Data'], y = generalDf['Zgony'], mode = 'lines+markers', name = 'Zgony'))
infectedFig.add_trace(go.Scatter(x = generalDf['Data'], y = generalDf['Wyleczeni'], mode = 'lines+markers', name = 'Wyleczeni'))

preventionFig.add_trace(go.Scatter(x = generalDf['Data'], y = generalDf['Hospitalizacje'], mode = 'lines+markers', name = 'Hospitalizacje'))
preventionFig.add_trace(go.Scatter(x = generalDf['Data'], y = generalDf['Kwarantanna'], mode ='lines+markers', name = 'Kwarantanna'))
preventionFig.add_trace(go.Scatter(x = generalDf['Data'], y = generalDf['Nadzór'], mode ='lines+markers', name = 'Nadzór medyczny'))
preventionFig.add_trace(go.Scatter(x = generalDf['Data'], y = generalDf['Liczba testów'], mode ='lines+markers', name = 'Wykonane testy'))

sunburstDf = sunburstDf[['Province', 'City', 'Infection/Death/Recovery', 'Timestamp']]
sunburstDf.columns = ['Województwo', 'Miasto', 'Przypadek', 'Liczba przypadków']
wojSunburstFig = px.sunburst(sunburstDf, path=['Województwo', 'Miasto', 'Przypadek'], values='Liczba przypadków',  color ='Liczba przypadków',color_continuous_scale='Reds',maxdepth=2, labels={"id":"Id", "parent":"Rodzic", 'labels':'Etykieta'})

logFigPlot.add_trace(go.Scatter(x = logFigData['Potwierdzenia ogółem'], y = logFigData['Nowe potwierdzenia'], mode = 'lines+markers', name = 'Potwierdzenia'))

logFigPlot.update_traces(
    marker = {"line": {"width": 1, 'color':'grey'}},
    hovertemplate='<b>Liczba wszystkich przypadków %{x}<br><b>Liczba nowych przypadków: %{y}',
    )

wojSunburstFig.update_traces(
    marker = {"line": {"width": 1, 'color':'grey'}},
    hovertemplate='<b>%{label}<br><b>Liczba przypadków: %{value}',
    )



wojSunburstFig.update_layout(
    paper_bgcolor = '#2b3e50', 
    margin = dict(l = 0, r = 0, t = 35, b = 0),
    font = dict(color = 'white'),
    coloraxis_showscale = False
    )


infectedFig.update_layout(
    paper_bgcolor = '#2b3e50', 
    margin = dict(l = 0, r = 0, t = 35, b = 0),
    font = dict(color = 'white'),
    legend = dict(x = 0, y = 1, bgcolor = 'rgba(0,0,0,0)', font = {'color':'black'})
    )

preventionFig.update_layout(
    paper_bgcolor = '#2b3e50', 
    margin = dict(l = 0, r = 0, t = 35, b = 0),
    font = dict(color = 'white'),
    legend = dict(x = 0, y=1, bgcolor = 'rgba(0,0,0,0)', font = {'color':'black'})
    )

logFigPlot.update_layout(
    paper_bgcolor = '#2b3e50', 
    margin = dict(l = 0, r = 0, t = 35, b = 0),
    font = dict(color = 'white'),
    xaxis_title="Liczba wszystkich potwierdzeń",
    yaxis_title="Liczba nowych potwierdzeń",
    legend = dict(x = 0, y = 1, bgcolor = 'rgba(0,0,0,0)', font = {'color':'black'})
    )


heatmapFig = go.Figure(go.Heatmap(
        z = coronaDf2['Infection/Death/Recovery'],
        x = coronaDf2['Timestamp'],
        y = coronaDf2['Province'],
        xgap = 3, # this
        ygap = 3, # and this is used to make the grid-like apperance,
        colorscale = "Reds",
        hovertemplate='Data: %{x}<br>Województwo: %{y}<br>Potwierdzenia: %{z}<extra></extra>'
    ))

heatmapFig.update_layout(
    paper_bgcolor = '#2b3e50', 
    margin = dict(l = 0, r = 0, t = 35, b = 0),
    font = dict(color = 'white'),
    )

def destinationsMapPlot(df):
    coronaDf = df.reset_index()

    destinationsDf = coronaDf[coronaDf['Infection/Death/Recovery']=='I']
    destinationsDf = destinationsDf[['Where_infected', 'City']].fillna('POL')
    destinationsDf = destinationsDf[destinationsDf['Where_infected']!='POL']

    destinationsDf['B'] = destinationsDf["City"].apply(lambda x: cities_BL[x][0]+random.random()/10)
    destinationsDf['L'] = destinationsDf["City"].apply(lambda x: cities_BL[x][1]+random.random()/10)

    destinationsDf['Destination'] = destinationsDf['Where_infected'].apply(lambda x: pycountry.countries.get(alpha_3=x).name)

    countries = list(destinationsDf[~destinationsDf['Destination'].isin(countries_BL)]['Destination'].dropna().unique())
    try:
        for country in countries:
            countries_BL[country] = geolocator.geocode(country)[1]
    except TypeError:
        print('Type Error')

    destinationsDf['Destination_B'] = destinationsDf['Destination'].apply(lambda x: countries_BL[x][0]+random.random()/10)
    destinationsDf['Destination_L'] = destinationsDf['Destination'].apply(lambda x: countries_BL[x][1]+random.random()/10)

    # Opacity value depends of frequency of destination
    destinationsDf['freq'] = destinationsDf['Destination'].apply(lambda x: (list(destinationsDf['Destination']).count(x)/len(list(destinationsDf['Destination']))+0.2)/1.2)
    print(destinationsDf['freq'].min())
    destinationsMap = go.Figure()

    for i in list(destinationsDf.index):
        destinationsMap.add_trace(
            go.Scattergeo(
                lon = [destinationsDf.loc[i]['L'], destinationsDf.loc[i]['Destination_L']],
                lat = [destinationsDf.loc[i]['B'], destinationsDf.loc[i]['Destination_B']],
                mode = 'lines',
                line = dict(width = 1,color = 'red'),
                opacity = destinationsDf.loc[i]['freq'],
            )
        )

    destinationsMap.add_trace(go.Scattergeo(
        lon = destinationsDf['L'],
        lat = destinationsDf['B'],
        hoverinfo = 'text',
        text = destinationsDf['City'],
        mode = 'markers',
        marker = dict(
            size = 3,
            color = 'rgb(0, 0, 255)',
            line = dict(
                width = 3,
                color = 'rgba(68, 68, 68, 0)'
            )
        )))

    destinationsMap.add_trace(go.Scattergeo(
        lon = destinationsDf['Destination_L'],
        lat = destinationsDf['Destination_B'],
        hoverinfo = 'text',
        text = destinationsDf['Destination'],
        mode = 'markers',
        marker = dict(
            size = 3,
            color = 'rgb(255, 0, 0)',
            line = dict(
                width = 3,
                color = 'rgba(68, 68, 68, 0)'
            )
        )))

    destinationsMap.update_layout(
        title_text = 'Kierunki ostatnich podróży pacjentów z potwierdzonym zakażeniem',
        showlegend = False,
        hovermode='closest',
        paper_bgcolor = '#2b3e50', 
        margin = dict(l = 0, r = 0, t = 35, b = 0),
        font = dict(color = 'white'),
        height=600,
        geo = dict(
            fitbounds="locations",
            projection_type = 'natural earth',
            showland = True,
            landcolor = 'rgb(243, 243, 243)',
            resolution=110,
            rivercolor = 'rgb(0, 0, 255)',
            countrycolor = 'rgb(204, 204, 204)',
            showocean=True, 
            oceancolor="LightBlue",
            lonaxis_showgrid=True, 
            lataxis_showgrid=True,
            showcountries=True,
            bgcolor = '#2b3e50'
        )
    )

    destinationsMap.update_traces(
        customdata = destinationsDf[["City", 'Destination']].values, 
        hovertemplate='%{customdata[1]}-%{customdata[0]}',
        name = ''
        )
    return destinationsMap

## ## ## ## ##
df = coronaDf
df['Province'] = df['Province'].apply(lambda x: x.lower())

unique_cities = list(df[~df['City'].isin(list(cities_BL.keys()))]['City'].dropna().unique())
try:
    for city in unique_cities:
        print(city)
        cities_BL[city] = geolocator.geocode(city)[1]
except TypeError:
    print('Type Error')

####################


customMap = px.scatter_mapbox(lat=[0],  lon=[0],  center = dict(lat=52, lon=19), zoom = 5, 
                    mapbox_style = 'carto-positron', height = 600)

customMap.update_layout(
    paper_bgcolor = '#2b3e50', 
    margin = dict(l = 0, r = 0, t = 35, b = 0),
    font = dict(color = 'white'),
    coloraxis_showscale = False
)

#Slider options dictionary

coronaDfDict = {}
i = 0
for data in coronaDf['Timestamp'].sort_values().dt.date.unique():
    coronaDfDict[i] = str(data)[5:] #remove year
    i=i+1

# App server

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.SUPERHERO])
server = app.server

# App layout

app.layout = html.Div([
        dbc.Row([
            dbc.Col([
                html.Img(src = "http://uwm.edu.pl/geosin/wordpress/wp-content/uploads/2016/12/logo_pozmianie-e1546509093312.png", style={'width':'50%', 'margin-top':'15px', 'margin-bottom': '15px'})
                ], width = 2),
            dbc.Col([
                html.H1(id = 'TitleId', children = 'Coronawirus na mapie (SARS-CoV-2)', style = {'margin-top':'20px'}), 
                html.H6(id = 'SubtitleId', children ='Na podstawie danych zebranych przez Koło Naukowe GeoSiN z Uniwersytetu Warmińsko-Mazurskiego w Olsztynie', style={'margin-top':'10px'})
                ], width = 8), 
            dbc.Col([
                html.Img(src = "http://www.uwm.edu.pl/geosin/wordpress/wp-content/uploads/2020/03/poland.png",style={'width':'50%','margin-top':'20px', 'margin-bottom':'10px'})
                ], width = 2),
        ], style = {'width':'101%' ,'backgroundColor':'#042c38','text-align':'center'}),
                                            

    dcc.Tabs(id="app-tabs", value= '1', colors =  {'border': '#d6d6d6', 'primary': '#1975F00', 'background': '#ffffff10'}, children=[
        dcc.Tab(label = 'O projekcie', value = '1', children= html.Div([
            dbc.Row([
                dbc.Col([html.H5('Projekt "Wirus na mapie"'),html.Div(children = desc)], width = 4),
                dbc.Col([html.H5('Aktualności'), html.Div(children = dbc.Table.from_dataframe(news, striped=True, bordered=False, hover=True, responsive=True, style={'textAlign':'left'})
            )], width = 5),
                dbc.Col([html.H5('Interaktywność treści'),html.P(' '), html.Img(src='http://www.uwm.edu.pl/geosin/wordpress/wp-content/uploads/2020/03/figPlot.gif', width='100%'), html.Img(src='http://www.uwm.edu.pl/geosin/wordpress/wp-content/uploads/2020/03/heatmap.gif', width='100%')], width = 3)
            ], style = {'margin':15, 'textAlign': 'left'})
        ], style = {'margin':15, 'textAlign': 'left'})),

        dcc.Tab(label = 'Wirus na mapach', value = '3', children = html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(label = 'Zasięg wirusa', tab_id = "zasiegwirusaTab"),
                        dbc.Tab(label = 'Przypadki wg miejscowości', tab_id = "wmiastachTab"),
                        dbc.Tab(label = 'Przypadki wg województw', tab_id = "wwojewodztwachTab"),
                        dbc.Tab(label = 'Kierunki podróży', tab_id = 'kierunkipodrozyTab')
                    ], id = 'mapTabs', active_tab='zasiegwirusaTab', style= {'width':'100%'}),
                    html.Div(id = 'mapRadioItem', children = [dbc.RadioItems(
                        id = 'mapRadioItems', inline = True,
                        options = [
                            {'label': 'Potwierdzenia', 'value':1},
                            {'label': 'Zgony', 'value':2},
                            {'label': 'Wyzdrowienia', 'value':3},
                        ],
                        value = 1
                    ), html.Div(id = 'sliderDivId', children = [dcc.Slider(id='sliderId',  min = 0, max = i-1, value = i-1, marks = coronaDfDict)], style = {'margin-right':'5px', 'fontcolor':'white', 'width':'100%' }),
                    ]),
                    #html.Div(id = 'sliderDivId', children = [dcc.Slider(id='sliderId',  min = 0, max = i-1, value = 1, marks = coronaDfDict)], style = {'margin-right':'5px', 'fontcolor':'white' }),
                    html.Div(id="mapTabsContent"),
                ], md = 12)
            ])
        ], style = {'margin':20, 'textAlign': 'left'})),

        dcc.Tab(label = 'Statystyki', value = '4' , children = html.Div([
            dbc.Row(
                dbc.Table.from_dataframe(currentCases, striped=True, bordered=True, hover=True, responsive=True, style={'textAlign':'center'})
            ),
            dbc.Row([
                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(label = 'Zachorowania wg dni', tab_id = "zachorowaniaTab"),
                        dbc.Tab(label = 'Zachorowania', tab_id = 'zachorowaniaLogTab'),
                        dbc.Tab(label = 'Prewencja', tab_id = "prewencjaTab"),
                        dbc.Tab(label = 'Województwa', tab_id = "wojewodztwaTab")
                    ], id = 'plotTabs', active_tab='zachorowaniaTab', style= {'width':'100%'}),
                    html.P(''),
                    html.Div(id='checkBoxDivId', children = dbc.Checklist( id='checkBoxId',
                        options=[ {'label': 'Lubię logarytmy', 'value': 1} ],
                        value=[],
                        inline = True
                    )),
                    html.Div(id="plotTabsContent"),
                ], md = 6),

                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(label = 'Potwierdzenia', tab_id = "heatmapInfectionTab"),
                        dbc.Tab(label = 'Aktywne', tab_id = "heatmapActiveTab"),
                        dbc.Tab(label = 'Zgony', tab_id = "heatmapDeathTab"),
                        dbc.Tab(label = 'Wyzdrowienia', tab_id = "heatmapRecoveredTab")
                    ], id = 'heatmapsTabs', active_tab='heatmapInfectionTab', style= {'width':'100%'}),
                    
                    html.P(''),
                    html.Div(id='radioBoxesId', children=[
                        dbc.RadioItems(
                            id = "example-radios-row", inline = True,
                            options = [
                            {"label": "Liczba nowych przypadków", "value": 1},
                            {"label": "Całkowita liczba przypadków ", "value": 2}
                            ],
                            value = 2
                        )]),
                    html.Div(id="heatmapsTabsContent"),
                ], md = 6
                ), 
            ], style = {'align':'center'}  )
        ], style = {'margin':20, 'textAlign': 'left'})),

        dcc.Tab(label = 'Szpitale zakaźne', value = '5', children = html.Div([
            dbc.Row([
                
            ]),
            dbc.Row([
                dbc.Col( [html.H5('Znajdź najbliższy szpital zakaźny (podaj adres): '), address_bar, dcc.Graph(id = 'hospitalsMapId', figure = hospitalsMap)], width = 7 ),
                dbc.Col([html.H5('Adresy najbliższych placówek'), html.Div( id='hospitalsTableId', children = dbc.Table.from_dataframe(df=hospitalsDf[['Szpital', 'Adres']].head(5), striped=True, bordered=True, hover=True))], width = 5 )
            ]),
            dbc.Row(
                dbc.Col()
            )
        ], style = {'margin':15, 'textAlign': 'left'})),
        
        dcc.Tab(label = 'Autorzy', value='6', children = html.Div([
            html.P(''),
            dbc.Row([
                dbc.Col([
                    html.H4('Scenariusz i reżyseria: ', style={'margin-bottom':'25px'}),
                    dbc.Row([
                        dbc.Col([
                            html.P('Aleksandra Gleba'),
                            html.P('Patrycja Borsuk'),
                            html.P('Mateusz Czyrzniak'),
                            html.P('Piotr Poskrobko'),
                            html.P('Michał Lasia'),
                        ]),
                        dbc.Col([
                            html.P('Łukasz Łobko'),
                            html.P('inż. Tomasz Kozakiewicz'),
                            html.P('mgr inż. Marta Augustynowicz'),
                            html.P('dr inż. Dariusz Tanajewski'),
                    html.Div(' '),
                        ])
                    ]),
                    html.Div('Serdeczne podziękowania dla Łukasza Sawaniewskiego z Olsztyn @ DataWorkshop Club,'),
                    html.Div('za pomoc w przejściu przez meandry multi-indeksowania oraz prezentacji danych'),
                    ], md = 5),
                    
                dbc.Col([
                    html.H4('W rolach głównych występują: '),
                    html.P(''),
                    html.P([html.Img(src='http://www.uwm.edu.pl/geosin/wordpress/wp-content/uploads/2020/03/python.png'), html.Img(src='http://www.uwm.edu.pl/geosin/wordpress/wp-content/uploads/2020/03/pandas.png')]),
                    html.P([html.Img(src='http://www.uwm.edu.pl/geosin/wordpress/wp-content/uploads/2020/03/plotly.png'), html.Img(src='http://www.uwm.edu.pl/geosin/wordpress/wp-content/uploads/2020/03/heroku1.png'),html.Img(src='http://www.uwm.edu.pl/geosin/wordpress/wp-content/uploads/2020/03/dash.png')]),
                    html.P([html.Img(src='http://www.uwm.edu.pl/geosin/wordpress/wp-content/uploads/2020/03/geopy.png'), html.Img(src='http://www.uwm.edu.pl/geosin/wordpress/wp-content/uploads/2020/03/GitHub-e1585351451771.png')]),
                    ], md = 7)
            ],style = {'width':'100%'}),
            html.P([' ']),
            html.P([' ']),
            html.P([' ']),
            html.H3('Koła Naukowe zaangażowane w prace nad aplikacją'),
            dbc.Row([
                dbc.Col([html.Img(src = "http://www.uwm.edu.pl/geosin/wordpress/wp-content/uploads/2020/04/logo_dahlta.png", style={'width':'25%', 'margin-top':'15px', 'margin-bottom': '15px'}),html.P('KNG Dahlta'), html.P('Akademia Górniczo-Hutnicza im. Stanisława Staszica w Krakowie'),html.H6('https://www.facebook.com/KNGDahlta', style={'margin-top':'5px'}),]),
                dbc.Col([html.Img(src = "http://uwm.edu.pl/geosin/wordpress/wp-content/uploads/2016/12/logo_pozmianie-e1546509093312.png", style={'width':'25%', 'margin-top':'15px', 'margin-bottom': '15px'}),html.P('MKN GeoSiN'),html.P('Uniwersytet Warmińsko-Mazurski w Olsztynie'),html.H6('www.geosin.pl', style={'margin-top':'5px'}),html.H6('https://www.facebook.com/mkn.geosin', style={'margin-top':'5px'}),]),
                dbc.Col([html.Img(src = "http://www.uwm.edu.pl/geosin/wordpress/wp-content/uploads/2020/04/wroclaw.png", style={'width':'25%', 'margin-top':'15px', 'margin-bottom': '15px'}),html.P('SKN Geodetów'),html.P('Uniwersytet Przyrodniczy we Wrocławiu'),html.H6('https://www.facebook.com/SKNGeodetow/', style={'margin-top':'5px'}),]),
            ]),
            
            html.H5('Komentarze, opinie, prośby oraz zaproszenia do złożenia CV prosimy wysyłać na adres: ', style={'margin-top':'35px'}),
            html.H5('mkn.geosin@uwm.edu.pl'),
            html.H5(' ', style={'margin-top':'135px'}),
            html.Div()],
            style = { 'textAlign': 'center'}))
    ],style= {'width':'100%', 'fontColor':'red'})
], style = {
    'width':'100%',
    'overflow':'hidden',
    'asta':'niewime'
})


# Callbacks


@app.callback([
    Output('hospitalsTableId', 'children'),
    Output('hospitalsMapId', 'figure')], 
    [Input('addressInputId', 'value')],
    )
def findNearestHospital(user_address):
    user_B, user_L = lf.locate_user_address(user_address)
    hospitalsDf['Odległość_[km]'] = hospitalsDf.apply(lambda x: math.ceil(distance((user_B,user_L), (x.B, x.L)).kilometers), axis =1)
    hospitalsDf['distance_normalized'] = 1/(hospitalsDf['Odległość_[km]']+10)
    hospitalsMap  = px.scatter_mapbox(
        hospitalsDf, 
        lat = 'B', lon = 'L', 
        color = 'Odległość_[km]', 
        size = 'distance_normalized', 
        mapbox_style = 'carto-positron', 
        zoom = 5, 
        text = 'Szpital',
        center = go.layout.mapbox.Center(lat=51.80, lon=20.00),
        )
    hospitalsMap.update_layout(
        height = 600, 
        paper_bgcolor = '#2b3e50', 
        margin = dict(l=0, r=0, t=35, b=0),
        font = dict(color='white'),
        )
    hospitalsMap.update_traces(
        customdata = hospitalsDf[["Szpital", 'Odległość_[km]']].values, 
        hovertemplate='Szpital:%{customdata[0]}<br>Dystans: %{customdata[1]:.1f} km'
        )
    return dbc.Table.from_dataframe(hospitalsDf[['Szpital', 'Adres', 'Odległość_[km]']].sort_values(by=['Odległość_[km]']).head(6), id='hospitalsTableId', striped=True, bordered=True, hover=True), hospitalsMap


@app.callback(
    Output("plotTabsContent", "children"), [Input("plotTabs", "active_tab"), Input('checkBoxId', 'value')]
)
def figPlot_tab_content(active_tab, value):
    if active_tab == 'zachorowaniaTab':
        if len(value)!=0:
            infectedFig.update_layout(yaxis_type="log")
        else:
            infectedFig.update_layout(yaxis_type="linear")

        return dcc.Graph(id = 'infectedFigId', figure = infectedFig)

    elif active_tab == 'prewencjaTab':
        if len(value)!=0:
            preventionFig.update_layout(yaxis_type="log")
        else:
            preventionFig.update_layout(yaxis_type="linear")
            
        return dcc.Graph(id = 'preventionFigId', figure = preventionFig)

    elif active_tab == 'zachorowaniaLogTab':
        if len(value)!=0:
            logFigPlot.update_layout(yaxis_type="log")
        else:
            logFigPlot.update_layout(yaxis_type="linear")
        
        return dcc.Graph(id = 'preventionFigId', figure = logFigPlot)
            
    elif active_tab == 'wojewodztwaTab':
        return [dcc.Graph(id = 'preventionFigId', figure = wojSunburstFig), html.Div('*Z uwagi na ograniczonia w dostępie do danych, powyższy diagram należy traktować jako ciekawostkę.')]

@app.callback(
    Output("mapTabsContent", "children"), 
    [Input("mapTabs", "active_tab"), 
    Input('mapRadioItems', 'value'), 
    Input('sliderId', 'value')]
)
def mapPlot_tab_content(active_tab, value, endDate):
    df = coronaDf.copy()
    df = df.set_index('Timestamp').loc[:str('2020-'+coronaDfDict[endDate])]
    #print(str('2020-'+coronaDfDict[endDate]))
    infectedCondition = df['Infection/Death/Recovery']=='I'
    deathCondition = df['Infection/Death/Recovery']=='D'
    recoveredCondition = df['Infection/Death/Recovery']=='R'

    if active_tab == 'zasiegwirusaTab':
        if value == 1:
            caseCondition = infectedCondition
            colorsScaleType = 'YlOrRd'
        elif value == 2:
            caseCondition = deathCondition
            colorsScaleType = 'Greys'
        elif value == 3:
            caseCondition = recoveredCondition
            colorsScaleType = 'YlGn'

        dfI = df[caseCondition].groupby('City').count()
        dfI = dfI.reset_index()[['City', 'Infection/Death/Recovery']]
        dfI['B'] = dfI['City'].apply(lambda x: cities_BL_coordinates[x][0])
        dfI['L'] = dfI['City'].apply(lambda x: cities_BL_coordinates[x][1])
        densityMap = px.density_mapbox(dfI, lat = 'B', lon='L', z= 'Infection/Death/Recovery', radius = 20, 
                    center = dict(lat=52, lon=19), zoom = 5, range_color=[0,1], color_continuous_scale=colorsScaleType,
                    mapbox_style = 'carto-positron', height = 600)

        densityMap.update_layout(
            paper_bgcolor = '#2b3e50', 
            margin = dict(l = 0, r = 0, t = 35, b = 0),
            font = dict(color = 'white'),
            coloraxis_showscale = False
        )

        densityMap.update_traces(
            customdata = dfI[["City", 'Infection/Death/Recovery']].values, 
            hovertemplate='%{customdata[0]}<br>Liczba zdarzeń:%{customdata[1]}'
        )
        if len(dfI['Infection/Death/Recovery']) == 0:
            return [dcc.Graph(id = 'infectedFigId', figure = customMap)]
        else:
            return [dcc.Graph(id = 'infectedFigId', figure = densityMap)]
    
    if active_tab == 'wmiastachTab':
        if value == 1:
            caseCondition = infectedCondition
            colorsScaleType = 'Aggrnyl'
            cols = ['Miasto', 'Potwierdzenia', 'B', 'L']
            maxSize = 40
        elif value == 2:
            caseCondition = deathCondition
            colorsScaleType = 'Greys'
            cols = ['Miasto', 'Zgony', 'B', 'L']
            maxSize = 20
        elif value == 3:
            caseCondition = recoveredCondition
            colorsScaleType = 'YlGn'
            cols = ['Miasto', 'Wyzdrowienia', 'B', 'L']
            maxSize = 30

        dfD = df[caseCondition].groupby('City').count()
        dfD = dfD.reset_index()[['City', 'Infection/Death/Recovery']]
        dfD['B'] = dfD['City'].apply(lambda x: cities_BL_coordinates[x][0])
        dfD['L'] = dfD['City'].apply(lambda x: cities_BL_coordinates[x][1])
        dfD.columns = cols
        scatterMap = go.Figure()
        scatterMap = px.scatter_mapbox(dfD, lat = 'B', lon='L', color = dfD[cols[1]],  size = dfD[cols[1]], range_color = [0, dfD[cols[1]].max()],
                    center = dict(lat=52, lon=19), zoom = 5, color_continuous_scale=colorsScaleType, size_max = maxSize,
                    mapbox_style = 'carto-positron', height = 600)

        scatterMap.update_layout(
            paper_bgcolor = '#2b3e50', 
            margin = dict(l = 0, r = 0, t = 35, b = 0),
            font = dict(color = 'white'),
            coloraxis_showscale = True
        )

        scatterMap.update_traces(
            customdata = dfD[["Miasto", cols[1]]].values, 
            hovertemplate='%{customdata[0]}<br>Liczba zdarzeń:%{customdata[1]}',
        )
        if len(dfD['Miasto']) == 0:
            return [dcc.Graph(id = 'infectedFigId', figure = customMap)]
        else:
            return [dcc.Graph(id = 'infectedFigId', figure = scatterMap)]    

    if active_tab == 'wwojewodztwachTab':
        if value == 1:
            caseCondition = infectedCondition
            colorsScaleType = 'Reds'
            cols = ['Województwo', 'Potwierdzenia']
        elif value == 2:
            caseCondition = deathCondition
            colorsScaleType = 'Greys'
            cols = ['Województwo', 'Zgony']
        elif value == 3:
            caseCondition = recoveredCondition
            colorsScaleType = 'Greens'
            cols = ['Województwo', 'Wyleczenia']

        dfR = df[caseCondition].groupby('Province').count()
        dfR = dfR.reset_index()[['Province', 'Infection/Death/Recovery']]
        dfR.columns = cols
        f= open('wojewodztwa-min.geojson')
        provinces = json.load(f)
        densityMap = px.choropleth_mapbox(dfR, geojson=provinces,  featureidkey='properties.nazwa', locations = 'Województwo', 
                    center = dict(lat=52, lon=19), zoom = 5,color = cols[1], color_continuous_scale=colorsScaleType,
                    mapbox_style = 'carto-positron', height = 600)

        densityMap.update_layout(
            paper_bgcolor = '#2b3e50', 
            margin = dict(l = 0, r = 0, t = 35, b = 0),
            font = dict(color = 'white'),
            coloraxis_showscale = True,
        )

        densityMap.update_traces(
            customdata = dfR[["Województwo", cols[1]]].values, 
            hovertemplate='%{customdata[0]}<br>Liczba zdarzeń:%{customdata[1]}',
            marker_line_color = 'white',
        )
        if len(dfR['Województwo']) == 0:
            return [dcc.Graph(id = 'infectedFigId', figure = customMap)]
        else:
            return [dcc.Graph(id = 'infectedFigId', figure = densityMap)]
    
    if active_tab == 'kierunkipodrozyTab':
        return [dcc.Graph(id = 'destinationsMapId', figure = destinationsMapPlot(df))]

            


@app.callback(
    Output("heatmapsTabsContent", "children"), [Input("heatmapsTabs", "active_tab"), Input('example-radios-row', 'value')]
)
def heatmap_tab_content(active_tab, value):
               
    if active_tab == 'heatmapInfectionTab':
        coronaDfgrouped = coronaDfcaseI.groupby(['Timestamp', 'Province',]).count().reset_index().sort_values(by=['Province'], ascending=False)
        if value == 1:
            heatMapData = coronaDfgrouped
        elif value == 2:
            heatMapData = coronaDfGeneral[['Timestamp', 'Province', 'Confirmed']].sort_values(by=['Province'], ascending=False)
            heatMapData.columns = ['Timestamp', 'Province', 'Infection/Death/Recovery']
    elif active_tab == 'heatmapDeathTab':
        coronaDfgrouped = coronaDfcaseD.groupby(['Timestamp', 'Province',]).count().reset_index().sort_values(by=['Province'], ascending=False)
        if value == 1:
            heatMapData = coronaDfgrouped
        elif value == 2:
            heatMapData = coronaDfGeneral[['Timestamp', 'Province', 'Death']].sort_values(by=['Province'], ascending=False)
            heatMapData.columns = ['Timestamp', 'Province', 'Infection/Death/Recovery']
    elif active_tab == 'heatmapRecoveredTab':
        coronaDfgrouped = coronaDfcaseR.groupby(['Timestamp', 'Province',]).count().reset_index().sort_values(by=['Province'], ascending=False)
        if value == 1:
            heatMapData = coronaDfgrouped
        elif value == 2:
            heatMapData = coronaDfGeneral[['Timestamp', 'Province', 'Recovered']].sort_values(by=['Province'], ascending=False)
            heatMapData.columns = ['Timestamp', 'Province', 'Infection/Death/Recovery']
    elif active_tab == 'heatmapActiveTab':
        coronaDfgrouped = coronaDfcaseI.groupby(['Timestamp', 'Province',]).count().reset_index().sort_values(by=['Province'], ascending=False)
        if value == 1:
            heatMapData = coronaDfgrouped
        elif value == 2:
            heatMapData = coronaDfGeneral[['Timestamp', 'Province', 'Active']].sort_values(by=['Province'], ascending=False)
            heatMapData.columns = ['Timestamp', 'Province', 'Infection/Death/Recovery']

        

    heatmapFig = go.Figure()

    heatmap1 = go.Heatmap(
        z = heatMapData['Infection/Death/Recovery'],
        x = heatMapData['Timestamp'],
        y = heatMapData['Province'],
        xgap = 3, # this
        ygap = 3, # and this is used to make the grid-like apperance,
        colorscale = "Reds",
        hovertemplate='Data: %{x}<br>Województwo: %{y}<br>Potwierdzenia: %{z}<extra></extra>'
    )

    heatmapFig.add_trace(heatmap1)

    heatmapFig.update_layout(
        paper_bgcolor = '#2b3e50', 
        margin = dict(l = 0, r = 0, t = 35, b = 0),
        font = dict(color = 'white'),
    )

    if active_tab == 'heatmapInfectionTab':
        heatmapFig.update_traces(colorscale='Reds', hovertemplate='Data: %{x}<br>Województwo: %{y}<br>Potwierdzenia: %{z}<extra></extra>')
    elif active_tab == 'heatmapDeathTab':
        heatmapFig.update_traces(colorscale='Greys', hovertemplate='Data: %{x}<br>Województwo: %{y}<br>Zgony: %{z}<extra></extra>')
    elif active_tab == 'heatmapRecoveredTab':
        heatmapFig.update_traces(colorscale='Greens', hovertemplate='Data: %{x}<br>Województwo: %{y}<br>Wyleczeni: %{z}<extra></extra>')
    
    return dcc.Graph(id = 'heatmapFigId', figure = heatmapFig)

# Google analitics code
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-162045786-1"></script>
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'UA-162045786-1');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </head>
</html>"""


# Run server 

if __name__ == '__main__':
    app.run_server(debug=True)
