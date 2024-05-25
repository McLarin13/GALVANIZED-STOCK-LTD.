from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytz
from datetime import datetime, time as dt_time
from tabulate import tabulate


#time code

philippine_timezone = pytz.timezone('Asia/Manila')
philippine_time = datetime.now(philippine_timezone)
formatted_date = philippine_time.strftime("%Y-%m-%d")
formatted_time = philippine_time.strftime( "%H:%M")

print(f"Philippine Time \n{formatted_date}  {formatted_time} ")



#Scraping
html_text = requests.get("https://finance.yahoo.com/most-active").text
soup = BeautifulSoup(html_text, features = 'html.parser')



#Difference Change Sort

differnece_change = soup.find_all("span", class_=lambda c: c in ["C($positiveColor)", "C($negativeColor)"])
change_diff= [difference.text for difference in differnece_change]
final_change_float = [float(dif.replace("+","")) for dif in change_diff  if "%" not in dif]
new_final_percent_float = final_change_float[6:]


pdchange = pd.DataFrame(new_final_percent_float)


#print(len(new_final_percent_float)



#Percent

differnece_percent = soup.find_all("span", class_=lambda c: c in ["C($positiveColor)", "C($negativeColor)"])
percentage_diff= [differenceperc.text for differenceperc in differnece_percent]
final_percent_float = [float(dif.replace("+","").replace("%","").replace("(","").replace(")",""))
                      for dif in percentage_diff  if "%" in dif]

new_final_percent_float = final_percent_float[6:]


pdpercent = pd.DataFrame(new_final_percent_float)



# Initialize a list to store the values

values = []

fin_streamers = soup.find_all('fin-streamer')
for streamer in fin_streamers:
    values.append(streamer['value'])

#print(len(values))

Market_Price= values[18::5]
pdMP = pd.DataFrame(Market_Price)

Market_Volume= values[21::5]
pdMV = pd.DataFrame(Market_Volume)

# Print the list of values


#Variable
all_co = []



#Row Extraction

#slider_co = soup.find_all("a", class_="Fz(s) Ell Fw(600) C($linkColor)")
table_co = soup.find_all("td", class_="Va(m) Ta(start) Px(10px) Fz(s)")


for tables in table_co:
  all_co.append(tables.text)


##print(len(all_co)) # should show 31


#Pandas and Tablinh

#Value Change
pdcompany = pd.DataFrame(all_co)
combined_data1 = pd.concat([pdcompany,pdchange],axis = 1)
combined_data1.columns = ["Company Name","Value Change"]

#Percent Change
combine_data2 = pd.concat([pdcompany,pdpercent], axis = 1)
combine_data2.columns = ["Args","Percent Change"]

#Market Price
combine_data3 = pd.concat([pdcompany,pdMP],axis = 1)
combine_data3.columns = ["Args","Price(Interday)"]

#Market Volume
combine_data4 = pd.concat([pdcompany,pdMV], axis = 1)
combine_data4.columns = ["Args","Buying Volume"]



#Two variables
all_merge_close_2 = pd.merge(combined_data1,combine_data2,left_on="Company Name", right_on="Args").drop("Args", axis = 1)

all_merge_close_1 = pd.concat([all_merge_close_2,combine_data3], axis =1)

ALL_MERGE_CLOSE_DEFAULT = pd.concat([all_merge_close_1,combine_data4], axis =1).drop("Args", axis =1)
ALL_MERGE_CLOSE_DEFAULT.index = pd.RangeIndex(start=1, stop=len(new_final_percent_float)+1, step=1)

#print(ALL_MERGE_CLOSE_DEFAULT.)

print(tabulate(ALL_MERGE_CLOSE_DEFAULT, headers='keys', tablefmt='pretty'))

