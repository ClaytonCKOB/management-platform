# This file will include functions that will be responsible to organize 
# the data of the website converting it to xlsx, pdf...
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pandas import DataFrame
import pandas as pd
import auvo.constants as const
from email.message import EmailMessage
import requests
import json
import smtplib


def xlsxReport(df:DataFrame):
    """
    Given a dataframe, will convert it to a xlsx file 
    
    :Args
        df: Dataframe -> data from the website 
    
    :Usage
        xlsxReport(df)
    """
    
    # Variables
    name = df['Nome'].iloc[0].lower()
    name = name[:30] if len(name) >= 31 else name
    df = df.drop(columns=['Nome', 'index'])
    writer = pd.ExcelWriter(f"{const.BASE_DIR}/reports/{name}.xlsx", engine='xlsxwriter')
    workbook  = writer.book
    

    # Saving the dataframe
    df.to_excel(writer, sheet_name=name, startrow=1, header=False, index=False)

    # Creating the worksheet
    worksheet = writer.sheets[name]

    # Creating formats
    bg_white = workbook.add_format({'bg_color': '#EEEEEE','font_name': 'Montserrat'}) 
    bg_gray  = workbook.add_format({'bg_color': '#FFFFFF','font_name': 'Montserrat'})

    bg_red   = workbook.add_format({'bg_color': 'red', 
                                    'font_color': 'white',
                                    'font_name': 'Montserrat'})

    bg_green = workbook.add_format({'bg_color': '#58BB43', 
                                    'font_color': 'white',
                                    'font_name': 'Montserrat'})

    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#51515D',
        'font_color': 'white',
        'font_name': 'Montserrat',
        'font_size': 10,
        'border': 1
    })


    # Getting the column's title
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        column_len = df[value].astype(str).str.len().max()
        column_len = max(column_len, len(value)) + 3
        worksheet.set_column(col_num, col_num, column_len)

    # Adding conditional formats
    worksheet.conditional_format('F1:F'+str(len(df)+1), {'type':     'cell',
                                        'criteria': '<=',
                                        'value':    -2,
                                        'format':   bg_red})

    worksheet.conditional_format('F2:F'+str(len(df)+1), {
                                        'type':     'cell',
                                        'criteria': '>',
                                        'value':    -2,
                                        'format':   bg_green})

     
    # Declaring that the odds rows will be gray
    for i in range(len(df)+1):  
        worksheet.set_row(i, 20, cell_format=(bg_white if i%2!=0 else bg_gray))

    writer.save()


def postNotion(df:DataFrame):
    """
    Will make the integration with the notion

    :Args
        df: Dataframe -> data from the website 
    
    """
    secret = const.SECRET
    pageId = const.DB_ID

    url = f'https://api.notion.com/v1/pages'

    headers = {
        'Authorization': f'Bearer {secret}',
        "Notion-Version": "2022-02-22",
        "Content-Type": "application/json"
    }

    for i in range(len(df)):
        name = df['Nome'][i]
        km_inicial = float(df['Km Inicial Carro'][i])
        km_final =   float(df['Km Final Carro'][i])
        km_sistema = float(df['Km Sistema'][i])
        km_total =   float(df['Km Total'][i])
        date =       df['Data'][i]
        comparativo =round(float(df['Comp. Auvo'][i])*100)/100

        data = {
        "parent":{
            "database_id": pageId
        },
        "properties": {
          "Nome": {
            "title": [
              {
                "text": {
                  "content": name
                }   
              }
            ]
          },
          "Km Inicial Carro": {
            "number": km_inicial
               
          },
          "Km Final Carro": {
            "number": km_final
              
          },
          "Km Sistema": {
            "number": km_sistema
          },
          "Km Total": {
            "number": km_total
          },
          "Data": {
            "rich_text": [
              {
                "text": {
                  "content": date
                }   
              }
            ]
          },
          "Comparativo": {
            "number": comparativo
          },
        }}
    
        requests.post(url, json=json.loads(json.dumps(data)), headers=headers)

def emailReport(df:DataFrame):
    """
    Will send an email if there are negative values 

    :Args
        df: Dataframe -> data from the website 
    
    :Usage
        emailReport(df)
    
    """

    # Variables
    sender = const.EMAIL
    password = const.E_PASS
    msg = MIMEMultipart('related')
    divergence_records = ""
    text_html = ""

    msg['Subject'] = "Relatório Semanal da Quilometragem"
    msg['From'] = sender
    msg['To'] = const.TO_EMAIL

    for i in range(len(df)):
        bg = 'red' if float(df['Comp. Auvo'][i]) <= -2 else '#58BB43'
        divergence_records += f""" <tr bgcolor={bg}><td>{df['Nome'][i]}</td><td>{df['Km Inicial Carro'][i]}</td><td>{df['Km Final Carro'][i]}</td><td>{df['Km Sistema'][i]}</td><td>{df['Km Total'][i]}</td><td>{df['Data'][i]}</td><td>{df['Comp. Auvo'][i]}</td><td>{df['Comp. Veículo'][i]}</td></tr> """

    # Getting the interval of the report
    interval = str(df['Data'][0]) + " - > " + str(df['Data'][len(df)-1])

    # HMTL code of the email
    with open(str(const.BASE_DIR) + r"\auvo\email.html") as f:
        html = f.readlines()
    
    # Organizing the text
    for i in range(len(html)):
        text_html += html[i].replace("\n", '')
    
    # Adding the reports to the html
    text_html = text_html.replace("{divergence_records}", divergence_records)

    # Adding the interval to the html
    text_html = text_html.replace("replace_interval_here", interval)


    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)

    msgText = MIMEText('Alternative plain text message.')
    msgAlternative.attach(msgText)

    msgText = MIMEText(text_html, 'html')
    msgAlternative.attach(msgText)

    # Adding the images of the html's body
    for i in range(1, 6):
        #Attach Image 
        fp = open(f'{const.BASE_DIR}\images\image-{i}.png', 'rb') #Read image 
        msgImage = MIMEImage(fp.read())
        fp.close()
        # Define the image's ID as referenced above
        msgImage.add_header('Content-ID', f'<image-{i}>')
        msg.attach(msgImage)

    # Send email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, const.TO_EMAIL, msg.as_string())

