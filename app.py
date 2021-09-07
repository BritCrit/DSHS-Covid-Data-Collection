import pandas as pd 
import numpy as np
import requests 
from lxml import html

def import_dshs_data(link):
  df = pd.read_excel(link)
  report_label = df.iloc[0,0]
  report_label = report_label.replace('Current Report Period: ', '').split(' - ')
  df = pd.read_excel(link,skiprows=5)
  df = df.iloc[:,:16]
  #fix columns
  cols = df.columns.str.replace('\n', ' ')
  cols = ['district_name', 'district_lea_number',
       'total_district_enrollment_as_of_january_29,_20_cumulative',
       'campus_name', 'campus_id',
       'total_school_enrollment_as_of_january_29,_20_cumulative',
       'new_student_cases', 'new_staff_cases', 'on_campus', 'off_campus',
       'unknown', 'total_student_cases', 'total_staff_cases',
       'on_campus_cumulative', 'off_campus_cumulative', 'unknown_cumulative']
  df.columns = cols
  
  # drop campus without id and fix names
  df = df.dropna(subset=['campus_id']).reset_index(drop=True)
  df.campus_name = df.campus_name.replace('/n', ' ')
  
  df['week_start'], df['week_end'] = report_label[0], report_label[1]
  return df

def replace_zero_star_wnan(df):
    #fix null values
  int_col = ['new_student_cases', 'new_staff_cases', 'on_campus', 'off_campus',
        'unknown', 'total_student_cases', 'total_staff_cases',
        'on_campus_cumulative', 'off_campus_cumulative', 'unknown_cumulative']
  df[int_col] = df[int_col].replace(' ', np.nan)
  df = df.replace('*', np.nan)
  df = df.replace('', np.nan)
  df = df.fillna(0)
  return df

def collect_download_urls(url):
  r = requests.get(url)
  webpage = html.fromstring(r.content)
  link_list = webpage.xpath('//a/@href')

  for i in link_list:
    if '.xls' in i:
      download_list.append(i)
      print(f"Found excel chart: {i}")
   
  for i in download_list:
    if 'campus' in i.lower():
      campus_data.append(i)   
      print(f"Found campus data: {i}")
  print(campus_data)

url ='https://dshs.texas.gov/coronavirus/schools/texas-education-agency/'
download_list = []
campus_data = []


default_cols = ['week_start', 'week_end', 'district_name', 'district_lea_number',
       'total_district_enrollment_as_of_january_29,_20_cumulative',
       'campus_name', 'campus_id',
       'total_school_enrollment_as_of_january_29,_20_cumulative',
       'new_student_cases', 'new_staff_cases', 'on_campus', 'off_campus',
       'unknown', 'total_student_cases', 'total_staff_cases',
       'on_campus_cumulative', 'off_campus_cumulative', 'unknown_cumulative']

base_df = pd.DataFrame(data=None, columns=default_cols)

collect_download_urls(url)

import_df_list = []

for i in campus_data:
  df = import_dshs_data(i)
  import_df_list.append(df)

## Combine Dataframes into signle 
dshs_data = pd.concat(import_df_list, ignore_index=True)

## Adjust so week start and end are leading columns 
dshs_data = dshs_data[['week_start', 'week_end','district_name', 'district_lea_number',
       'total_district_enrollment_as_of_january_29,_20_cumulative',
       'campus_name', 'campus_id',
       'total_school_enrollment_as_of_january_29,_20_cumulative',
       'new_student_cases', 'new_staff_cases', 'on_campus', 'off_campus',
       'unknown', 'total_student_cases', 'total_staff_cases',
       'on_campus_cumulative', 'off_campus_cumulative', 'unknown_cumulative']]
