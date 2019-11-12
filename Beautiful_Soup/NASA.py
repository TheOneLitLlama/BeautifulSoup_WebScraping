import requests
from bs4 import  BeautifulSoup
import pandas as pd
import datetime
import re

def find_stuff (data):
    arr = []
    for entries in data:
        if entries != '':
            arr.append(entries)
    return arr
def get_data(data):
    arr = []
    for temp in data:
        if temp.__class__.__name__ == 'Tag':
            tempArr = []
            tempArr.append(temp.contents[0])
            arr.append(tempArr)
        else:
            arr.append(find_stuff(temp.string.split(' ')))
    return arr

r = requests.get('http://www.hcbravo.org/IntroDataSci/misc/waves_type2.html')
root = BeautifulSoup(r.content, "lxml")
df_nasa = pd.DataFrame({'start_date':['1997/04/01'],
'start_time':['14:00'],
'end_date':['04/01'],
'end_time':['14:15'],
'start_frequency':['8000'],
'end_frequency':['4000'],
'flare_location':['S25E16'],
'flare_region':['8026'],
'flare_classification':['M1.3'],
'cme_date':['04/01'],
'cme_time':['15:18'],
'cme_angle':['74'],
'cme_width':['79'],
'cme_speed':['312'],})
table = root.find("pre").contents
length = len(table)
i = 10
while (i<length-10):
    arr = []
    temp  = 0
    while temp < 11:
        if(table[i+temp].__class__.__name__ == 'Tag'):
            if(table[i+temp].contents[0]=='PHTX'):
                temp = temp + 1
                break
            else:
                arr.append(table[i+temp])
        else:
            arr.append(table[i+temp])
        temp = temp + 1
    data = get_data(arr)
    flattened = [val for sublist in data for val in sublist]
    flat = [i for i, item in enumerate(flattened) if re.search('.*\n\d+\/\d+\/\d+', item)]
    flattened = flattened[flat[0]:]
    start_date = flattened[0]
    start_time = flattened[1]
    end_date = flattened[2]
    end_time = flattened[3]
    start_freq = flattened[4]
    end_freq = flattened[5]
    loc = flattened[6]
    NOAA = flattened[7]
    flare_classification =  flattened[8]
    cme_date =  flattened[9]
    cme_time =  flattened[10]
    cme_angle = flattened[11]
    cme_width = flattened[12]
    cme_speed=  flattened[13]
    strIn = start_date.find('/')
    start_date = start_date[strIn-4:]
    df_nasa1 = pd.DataFrame({'start_date':[start_date],
    'start_time':[start_time],
    'end_date':[end_date],
    'end_time':[end_time],
    'start_frequency':[start_freq],
    'end_frequency':[end_freq],
    'flare_location':[loc],
    'flare_region':[NOAA],
    'flare_classification':[flare_classification],
    'cme_date':[cme_date],
    'cme_time':[cme_time],
    'cme_angle':[cme_angle],
    'cme_width':[cme_width],
    'cme_speed':[cme_speed]})
    df_nasa = df_nasa.append(df_nasa1,ignore_index=True)
    i = i + temp

df_nasa = df_nasa.replace('????','NaN')
df_nasa = df_nasa.replace('-----','NaN')
df_nasa = df_nasa.replace('----','NaN')
df_nasa = df_nasa.replace('--/--','NaN')
df_nasa = df_nasa.replace('--:--','NaN')
df_nasa = df_nasa.replace('24:00','00:00')
df_nasa = df_nasa.replace('FILA','NaN')
df_nasa['Halo'] ='False'
df_nasa['lower_bound'] = 'False'
df_nasa['fcNums'] = 0
df_nasa['fcDec'] = 0
for index, row in df_nasa.iterrows():
    if row['flare_classification'] != 'NaN':
        fClass = row['flare_classification'][1:]
        f = fClass.find('.')
        fNum = int(fClass[:f])
        fDec = fClass[f+1:]
        if fDec == '':
            fDec = 0
        else:
            fDec = int(fDec)
        df_nasa.loc[index,'fcNums'] = fNum
        df_nasa.loc[index,'fcDec'] = fDec
    start_date = datetime.datetime.strptime(row['start_date'],'%Y/%m/%d').date()
    start_time = datetime.datetime.strptime(row['start_time'],'%H:%M').time()
    end_date = datetime.datetime.strptime(row['end_date'],'%m/%d').date()
    end_time = datetime.datetime.strptime(row['end_time'],'%H:%M').time()
    if row['cme_date'] == 'NaN':
        cmedatetime = 'NaN'
    else:
        cme_date = datetime.datetime.strptime(row['cme_date'],'%m/%d').date()
        cme_time = datetime.datetime.strptime(row['cme_time'],'%H:%M').time()
        cme_date = cme_date.replace(year=start_date.year)
        cmedatetime = datetime.datetime.combine(cme_date,cme_time)
    end_date = end_date.replace(year=start_date.year)
    startdatetime = datetime.datetime.combine(start_date,start_time)
    enddatetime = datetime.datetime.combine(end_date,end_time)
    df_nasa.loc[index,'start_time'] = startdatetime
    df_nasa.loc[index,'end_time'] = enddatetime
    df_nasa.loc[index,'cme_time'] = cmedatetime
    if row['cme_angle'] == 'Halo':
        df_nasa.loc[index,'Halo'] = 'True'
        df_nasa.loc[index,'cme_angle'] = 'NA'
    if row['cme_width'].startswith('>'):
        df_nasa.loc[index,'lower_bound'] = 'True'
        df_nasa.loc[index,'cme_width'] = row['cme_width'].replace('>','')
df_nasa = df_nasa.drop('cme_date',1)
df_nasa = df_nasa.drop('start_date',1)
df_nasa = df_nasa.drop('end_date',1)
print(df_nasa)
