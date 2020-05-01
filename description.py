import pandas as pd
import dash_html_components as html

aboutProject = [html.P('Celem projektu "Wirus na mapie" jest monitorowanie rozprzestrzeniania się epidemii COVID-19 w Polsce, bazując na oficjalnych komunikatach rządowych i doniesieniach mediów ogólnopolskich i lokalnych.', style = {'textAlign':'justify'}),
    html.P("""Projekt składa się z dwóch części: pierwsza polega na gromadzeniu danych dotyczących kolejnych zdarzeń powiązanych 
    z epidemią. Każde zdarzenie - potwierdzenie infekcji, śmierć czy wyzdrowienie - posiada swoją sconygnaturę czasową oraz 
    jest geotagowane z największą możliwą dokładnością. Oprócz tego, o ile jest to możliwe, gromadzimy dane o osobach, których zdarzenie dotyczy.
    Dane są aktualizowane w dobowych odstępach (zwykle na drugi dzień po ostatnim komunikacie) i jest do nich 
    swobodny dostęp za pośrednictwem serwisu GitHub (link poniżej). Do tej pory aktualizacje obejmowały cały kraj, ale nie wykluczamy, że w przyszłości 
    szczegółowe aktualizacje będą obejmowały tylko kilka województw. Wynika to z dużego wzrostu liczby zdarzeń, przez co coraz trudniej jest nam utrzymać bazę
    na poziomie zakładanej dokładności i aktualności.""",  style = {'textAlign':'justify'}), 
    html.P("Czasami nie sposób jest dotrzeć do szczegółowych informacji. W takich sytuacjach ograniczamy się jedynie do podania stolicy województwa, w którym miało miejsce dane zdarzenie."),
    html.P("""Druga część związana jest z prezentacją danych. Do tego celu stworzyliśmy własny potral mapowy, który pozwala nam na swobodne
    dodawanie nowych funkcjonalności oraz prezentowania dowolnie wybranych zależności na mapach i wykresach. Wykaz narzędzi, które zostały
    do tego celu wykorzystane znajduje się w zakładce 'Autorzy'.""",  style = {'textAlign':'justify'}),
    html.P('Dane oraz metadane znajdują się pod adresem: https://github.com/dtandev/coronavirus',  style = {'textAlign':'left'})]

projectNews = pd.read_csv('https://raw.githubusercontent.com/dtandev/coronavirus/master/newsCsv.csv') 