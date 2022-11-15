import requests as re
from bs4 import BeautifulSoup as bs
import pandas as pd
from sys import argv, path
import json
import base64
import logging

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

    from datetime import date
    fii_data = {}
    fii_data[fii_initials] = {}
    fii_data[fii_initials]['date'] = date.today().strftime("%d/%m/%Y")
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

def csv_formater(p_dict):
    csv_output = ""
    str_list = []
    for key in p_dict:
        print(p_dict[key])
        for k,v in p_dict[key].items():
            str_list.append(str(v))
    csv_output = ",".join(str_list)
    return csv_output

def self_test():
    # DATE DY DY3 DY6 DY12 P/PV P 
    fii = 'BARI11'    
    response = fundsexplorer(fii)
    print(response)
    csv_output = True
    if csv_output:
        print(csv_formater(response))
    
    def self_test_list():
        fiis = ['BARI11','MFII11','HCTR11','BBPO11','BRCR11','HSML11','MXRF11','RBRF11','VISC11','XPML11','SPTW11']
        fiis = ['BARI11']
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

if __name__ == "__main__":
    self_test()

def handler(event, context):
    try:
        path.insert(0, 'dependencies')
        print(event)

        method = event['requestContext']['http']['method']
        print(f"method: {method}")
        raw_path = event['rawPath']
        print(f"raw_path: {raw_path}")
        
        initials = ""
        if method == "POST":
            body = event['body']
            body_encoded = event['isBase64Encoded']
            if body_encoded:
                body = base64.b64decode(body).decode()
            print(body)
            initials = body['initials']
        elif method == "GET":
            initials = raw_path.split("/")[2]

        print(f"FII: {initials}")
        response = fundsexplorer(initials)

        csv_output = True
        if csv_output:
            response = csv_formater(response)

            return response
        else:
            return {
                "statusCode": 200,
                "headers": {
                    "Contet-Type": "application/json"
                },
                "body": json.dumps({
                    'Initials' : initials,
                    'response' : response
                }) 
            }


    except Exception as e:
        print(e)

