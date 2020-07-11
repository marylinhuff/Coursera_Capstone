#!/usr/bin/env python
# coding: utf-8

# # Comparing similar suburbs in the vicinity Philadelphia, PA

# ## Introduction
# 
# ### When I moved to the town I now live in, our selection criteria was good schools. Over time, I have grown to love the quaint shops and independent restuarants. Now that the kids are grown and we are downsizing, I'd like to find a similar neighborhood with these amenities and low property taxes since I no longer care about the quality of the schools.

# ## Data
# 
# ### To accomplish this I will need to gather data on neighborhoods around Philadelphia, property tax data, and venue information. The data will need to be joined by zipcode and/or municipality.

# In[1]:


import numpy as np # library to handle data in a vectorized manner

import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

#!conda install -c conda-forge geopy --yes # uncomment this line if you haven't completed the Foursquare API lab
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

#!conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
import folium # map rendering library

print('Libraries imported.')


# ### 1. Download Neighborhood and zipcode data for the Philadelphia metro area
# 
# #### This data can be found on this website: https://namecensus.com/igapo/zip_codes/metropolitan-areas/metro-alpha/Philadelphia%20(PA-NJ)1.html
# #### This data includes the zipcode and minicipality, telephone area code, county, state, and some extraneous information that I will not need.

# In[2]:


base_site = 'https://namecensus.com/igapo/zip_codes/metropolitan-areas/metro-zip/Philadelphia%20(PA-NJ)1.html'

r = requests.get(base_site)
r.status_code

DF_list = pd.read_html(r.text)

Philly_DF=DF_list[0]
Philly_DF.head()


# #### Retain only Delaware County and Montgomery Counties in PA

# In[3]:


PA_DF = Philly_DF[Philly_DF[3].str.contains('PA')]
DelCo_DF=PA_DF[PA_DF[2].str.contains('Delaware')]
MontCo_DF=PA_DF[PA_DF[2].str.contains('Montgomery')]
DelCoMontCo_DF=pd.concat([DelCo_DF, MontCo_DF], axis=0)
DelCoMontCo_DF.head()


# #### Drop Columns 1, 2, 3, 4, and 5 since they are not useful

# In[4]:


DelCoMontCo_DF.drop([1,2,3,4,5], axis=1,inplace=True)
DelCoMontCo_DF.head()


# #### Rename Columns

# In[5]:


DelCoMontCo_DF.columns = ['Zip_Muni']
DelCoMontCo_DF.head()


# #### Split 'Zip_Muni' into 'Zip' and 'MUNICIPALITY'

# In[6]:


DelCoMontCo_DF=pd.DataFrame(DelCoMontCo_DF.Zip_Muni.str.split(' ',1).tolist(), columns = ['Zip','MUNICIPALITY'])
DelCoMontCo_DF['MUNICIPALITY'] = DelCoMontCo_DF['MUNICIPALITY'].str.upper() 
DelCoMontCo_DF.head()


# ### 2. Download Property tax information for Delaware County, PA
# 
# #### This data can be found on this website: https://www.delcopa.gov/treasurer/propertytaxes.html as a PDF. I exported the PDF to Excel, trimmed out extranous information, and renamed teh columns.

# In[7]:


DelCoTax_DF=pd.read_excel('TaxRateDelCo.xlsx', index_col=0) 
DelCoTax_DF.head()


# ### 3. Download Property tax information for Montgomery County, PA
# 
# #### This data can be found on this website: https://www.montcopa.org/622/County-Municipality-Millage-Rates

# In[8]:


base_site = 'https://www.montcopa.org/622/County-Municipality-Millage-Rates'

r = requests.get(base_site)
r.status_code

DF_list = pd.read_html(r.text)

MontCoTax_DF=DF_list[0]
MontCoTax_DF.columns = MontCoTax_DF.iloc[0]
MontCoTax_DF.drop([0], axis=0,inplace=True)
MontCoTax_DF.head()


# #### I'm really only interested in the municipality and total millage.

# In[9]:


MontCoTax_DF=MontCoTax_DF[['Municipality','Total Millage']]
MontCoTax_DF.columns = ['MUNICIPALITY','TotalTaxRate']
MontCoTax_DF['MUNICIPALITY']=MontCoTax_DF['MUNICIPALITY'].str.upper()
MontCoTax_DF.head()


# ### 4. Link this information into a single DataFrame

# In[10]:


DelCoMontCoTax_DF=pd.concat([DelCoTax_DF, MontCoTax_DF], axis=0)
DelCoMontCo_DF=pd.merge(DelCoMontCo_DF, DelCoMontCoTax_DF, on='MUNICIPALITY')
DelCoMontCo_DF.head()


# #### Use geopy library to get the latitude and longitude values of Philadelphia.

# In[11]:


address = 'Philadelphia, PA'

geolocator = Nominatim(user_agent="philly_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Philadelphia are {}, {}.'.format(latitude, longitude))

