import json
import requests
import telegram
import time
import mysql.connector
from bs4 import BeautifulSoup
mydb = mysql.connector.connect(
  host="database-1.cyxb0drmxfft.us-east-1.rds.amazonaws.com",
  user="admin",
  password="admin123",

  database="CalDB"
)
mycursor = mydb.cursor()


bot = telegram.Bot('5306262514:AAGbfW4wV_ItrA2z08WL3FO_o2vL2T8FmrQ')

def load_data():
    print('Loading..')
    URL = "https://www.eenadu.net/"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    #results = soup.find(id="wrapper")
    #print(results.prettify())
    fig_elements = soup.find_all("figure", class_="item")
    #print(fig_elements)
    for fig_element in fig_elements:
        #print(fig_element, end="\n"*2)
        img_element = fig_element.find("img")
        a_element = fig_element.find("a")
        if img_element.has_attr('src'):
            #print(img_element['src'])
            #print(img_element['alt'])
            #print(a_element['href'] + '\n')
            URL = str(a_element['href'])
            #print(URL)
            txt = ''
            a4 = '' 
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, "html.parser")
            try:
                results = soup.find(id="wrapper")
                #print(results.prettify())
                span_elements = results.find_all("span", style="font-size:26px")
                for span_element in span_elements:
                    #print(span_element, end="\n"*2)
                    txt = txt + span_element.text + '\n'
                
                if len(txt) != 0:
                    a4 = txt[0:750]
                else:
                    a4 = ''                   
            except:
                print('No data')              
            try:
                sql ="insert  into CalDB.eenadu_imgs( ee_img_url,attribute2,attribute3,attribute4,creation_date,CREATED_BY) values ('" + str(img_element['src']) + "','" +str(img_element['alt']) + "','" +str(a_element['href']) + "','" +str(a4) +"',NOW(),-1 )"
                #print(sql)
                mycursor.execute(sql)
                mydb.commit()
            except mysql.connector.Error as err:
                #print("Something went wrong: {}".format(err))
                print("Something went wrong:")

def grab_data():
  sql = "SELECT ee_img_url,attribute2,attribute3,attribute4 from CalDB.eenadu_imgs where attribute1 is null"
  print(sql)
  mycursor.execute(sql)
  myresult = mycursor.fetchall()
  #print(myresult)
  for x in myresult:
    try:
        img  = str(x[0])  
        print(img)
        caption = '<b>' + str(x[1]) + '</b>\n\n' + '<pre>' + str(x[3]) + '</pre>' + '<a href="' + str(x[2])+ '"> More..</a>'
        #print(str(caption))       
        '''url = img
        response = requests.get(url)
        if response.status_code == 200:
            with open("sample.jpg", 'wb') as f:
                f.write(response.content)'''
        bot.send_photo(chat_id='-1001647973593', photo= str(img),caption = str(caption),parse_mode = 'HTML')
        try:
            sql = "UPDATE CalDB.eenadu_imgs SET attribute1 = 'Y' WHERE  ee_img_url = '" + str(img) + "'"
            print(sql)
            mycursor.execute(sql)
            mydb.commit()
            print(mycursor.rowcount, "record inserted."); 
        except Exception as e:
                print("Error in updating DB" + str(e))       
    except Exception as e:
        print("Error in sending.." + str(e))           
        

def lambda_handler(event, context):
    try:
        load_data()
        grab_data()   
        err = 'No error'
    except Exception as e:
        err = str(e)  
    
    return err