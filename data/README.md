# CSSE COVID-19 in Poland Dataset

## Daily reports (CoronavirusPL - Timeseries.csv)

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

### Update frequency
* We tried update our dataset twice a day. But somedays dataset caould be updated once, around 23:00 UTC+1.

### Data sources
Dataset based on official statements presented by the Ministry of Health, Provincial Departments and media. 

### Update frequency
* Once/Twice a day.

---
## Who makes a dataset
* Data was collected by GeoSiN Scientific Club Members from University of Warmia and Mazury in Olsztyn, Poland 
* Find us on the Facebook (www.facebook.com/mkn.geosin) or www (www.geosin.pl)
