# CSSE COVID-19 in Poland Dataset

## Daily events dataset (CoronavirusPL - Timeseries.csv)

This folder contains dataset with timestamped informations about infections, death and recoveries in Poland since 04-03-2020. 
Dataset based on official statements presented by the Ministry of Health and Provincial Departments. 
All timestamps are in UTC+1.

### Timestamp convention
DD-MM-YYYY in UTC.

								
### Field description
* Timestamp: Date of communique which contains information about infection, death or recovery of the patient [DD-MM-YYYY]
* Province: 1 of 16 polish provinces name 
* City: City where the patient comes from or where he/she was diagnosed
* Postal code: postal code for cities which have the same name as another one
* Infection/Death/Recovery: the patient status on the day of communique [I(nfected)/D(eath)/R(ecovered)]
* Sex: patient's gender if available 
* Where_infected: the countries which she/he visited in the near past and where he could be infected. The column contains country iso code. 
* Who_infected: who could be the source of the infection [Friends/Family/Another patient/Travel co-passenger)
* Age: How old is the patient? [F(emale)/M(ale)]

## Isolation wards dataset (CoronavirusPL - Isolation_wards.csv)

Dataset contains information about Isolation Wards, which were created in Poland.


### Field description
* Szpital: Hospital name
* Adres: Address of hospital 
* B: Latitude [DD.DDDD]
* L: Longitude [DD.DDDD]

## General information dataset (CoronavirusPL - General.csv)

Dataset contains general information about COVID-19 pandemy in Poland.

### Field description
* Timestamp: Date [DD-MM-YYYY]
* Confirmed: Number of confirmed Covid-19 cases in Poland
* Deaths: Number of novel coronavirus (COVID-19) deaths in Poland
* Recovered: Number of patients who have recovered from COVID-19 in Poland
* In_the_hospital: Number of patients requiring hospitalization in Poland
* In_quarantine: Number of people in quarantine in Poland
* Under_medical_supervision: Number of people under Public Health Monitoring in Poland
* Number_of_tests_carried_out: Number of COVID-19 test carried out in Poland


### Update frequency
* We update our dataset once a day (the next day morning after official information). We need more time to search for details in local media. 

### Data sources
Dataset based on official statements presented by the Ministry of Health, Provincial Departments and local media. 

### Update frequency
* Once a day.

---
## Who makes a dataset
* Data was collected by GeoSiN Scientific Club Members from the University of Warmia and Mazury in Olsztyn, Poland 
* Find us on the Facebook (www.facebook.com/mkn.geosin) or www (www.geosin.pl)

## Reference
D. Tanajewski, A. Gleba, P. Borsuk, M. Augustynowicz, T. Kozakiewicz: "Coronavirus infections data for Poland in 2020 (COVID-19 / 2019-nCoV)", 2020, GitHub, GitHub/dtandev/coronavirus, https://github.com/dtandev/coronavirus, the commit number
