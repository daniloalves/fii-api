import requests as re
from bs4 import BeautifulSoup as bs
import pandas as pd

def pd_table_parse(html_table):
    df = pd.read_html(str(html_table))[0]
    return df

def convert_to_float(float_str):
    fl = float(str(float_str).replace('%','').replace(',','.').replace('R$','').replace('mi','').replace("\n",""))
    return fl

def fundsexplorer(fii_initials):
    ws_url       = 'https://www.fundsexplorer.com.br'
    fii_path     = 'funds'
    # fii_initials = 'snag11'

    scraping_url = f"{ws_url}/{fii_path}/{fii_initials}"
    html_text    = re.get(scraping_url).text
    soup         = bs(html_text, 'html.parser')


    earnings = soup.find_all("div", {"class": "table-responsive"})[0]

    fundsexplorer_earnings_string = 'Proventos'

    if fundsexplorer_earnings_string not in str(earnings):
        raise Exception('Missing requirement string')

    df_earnings = pd_table_parse(earnings)

    dy_last_month = convert_to_float(df_earnings.iloc[1]['Último'])
    dy_three_months = convert_to_float(df_earnings.iloc[1]['3 meses'])
    dy_six_months = convert_to_float(df_earnings.iloc[1]['6 meses'])
    dy_twelve_months = convert_to_float(df_earnings.iloc[1]['12 meses'])

    fii_data = {}
    fii_data[fii_initials] = {}
    fii_data[fii_initials]['DY'] = dy_last_month
    fii_data[fii_initials]['DY3'] = dy_three_months
    fii_data[fii_initials]['DY6'] = dy_six_months
    fii_data[fii_initials]['DY12'] = dy_twelve_months

    fii_finan_tbl = soup.find("div", {"id": "main-indicators-carousel"}).findChildren("div", {"class": "carousel-cell"})

    for tags in fii_finan_tbl:
        tag = bs(str(tags), 'html.parser')
        title = str(tag.find("div", {"class": "carousel-cell"}).find("span", {"class": "indicator-title"})).replace('<span class="indicator-title">','').replace('</span>','').replace('</span>','').replace(' ','_')

        if title in ['Valor_Patrimonial','P/VP']:
            value = convert_to_float(str(tag.find("div", {"class": "carousel-cell"}).find("span", {"class": "indicator-value"})).replace('<span class="indicator-value">','').replace('</span>','').replace(' ',''))
            fii_data[fii_initials][title] = value
    
    return fii_data
    
# DY DY3 DY6 DY12 P/PV P 
# fiis = ['BARI11','MFII11','HCTR11','BBPO11','BRCR11','HSML11','MXRF11','RBRF11','VISC11','XPML11','SPTW11']
fiis = ['BARI11','MFII11']
fiis_data = []
for fii in fiis:
    print(fii)
    response = fundsexplorer(fii)
    # fiis_data.append(response)
    fii_data = response[fii]
    tmp_k = []
    tmp_v = []
    for k,v in fii_data.items():
        tmp_k.append(k)
        tmp_v.append(v)
    print(",".join(str(e) for e in tmp_k))
    print(",".join(str(e) for e in tmp_v))
    
    print('---')