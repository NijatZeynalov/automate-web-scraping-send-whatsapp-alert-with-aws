from bs4 import BeautifulSoup
import requests
from datetime import datetime
import boto3
from twilio.rest import Client
import csv
import json
from io import StringIO

base_url = 'https://kub.az/search?adsDateCat=All&entityType=0&buildingType=-1&purpose=0&ownerType=-1&city=1&words=&documentType=0&loanType=-1&oneRoom=false&twoRoom=false&threeRoom=false&fourRoom=false&fiveMoreRoom=false&remakeType=-1&minFloor=1&maxFloor=31&minBuildingFloors=1&maxBuildingFloors=31&minPrice=30000&maxPrice=66000&minArea=&maxArea=&minParcelArea=&maxParcelArea=&groupSimilar=true&search=&page='
page_idx = 9

def page_content(base_url,page_idx):
    pagedict = []
    for item in range(page_idx):
        
        page = requests.get(base_url+(str(item + 1)))
        if page.status_code !=200:
                raise Exception(f"Unable to download {base_url+(item)}")
        page_content = page.text
        pagedict.append(page_content)
    return pagedict

def data_in_text(pagedict):
    
    page_links1 = []

    description=[0]*len(pagedict)
    details=[0]*len(pagedict)
    address=[0]*len(pagedict)
    date=[0]*len(pagedict)
    price=[0]*len(pagedict)
    certificate=[0]*len(pagedict)
    url=[0]*len(pagedict)

    for i in range(len(pagedict)):
        
        description[i]=BeautifulSoup(pagedict[i]).find_all('p', class_="description")
        details[i]=BeautifulSoup(pagedict[i]).find_all('h1',class_="text-nowrap")
        address[i]=BeautifulSoup(pagedict[i]).find_all('p',class_="item-address")
        date[i]=BeautifulSoup(pagedict[i]).find_all('span',class_="item-date")
        price[i]=BeautifulSoup(pagedict[i]).find_all('h3',class_="item-price")
        certificate[i]=BeautifulSoup(pagedict[i]).find_all('div',class_="item-certificate")
        url[i]=BeautifulSoup(pagedict[i]).find_all('a',class_="more-details")
        
    for i in range(len(pagedict)):
        for j in range(0,20):
            try:
                page_links1.append({'url':'kub.az'+url[i][j].get('href'),'certificate':certificate[i][j].text.strip(),'price':price[i][j].text.strip(),'date':date[i][j].text.strip(),
                                    'details':''.join(details[i][j].text.split('\n')), 
                                    'description':description[i][j].text.strip(), 'address':address[i][j].text.strip()})
            except IndexError:
                pass
            continue
    return(page_links1)

def send_message_whatsapp(csv_file_name, house_count):

    twilio_sid = 'your_id'
    auth_token = 'your_token'
    client = Client(twilio_sid, auth_token)

    message = client.messages \
        .create(
             body='Salam, son yarım saat ərzində daxil etdiyiniz paramaterlərə uyğun {} yeni ev əlavə edilmişdir. \nYeni əlavə edilən evlərə baxmaq üçün linkə daxil olun: https://kubaz-automate-web-scraping.s3.amazonaws.com/{}'.format(house_count, csv_file_name),
             from_='whatsapp:+14155238886',
             to='whatsapp:your_number'
         )

    print(message.sid)

def remove_already_seen_houses(s3_bucket_name):
    
    previous_files = []
    s3 = boto3.resource('s3')
    bucket=s3.Bucket(s3_bucket_name)
    for key in bucket.objects.all():
        if key.key.startswith('hou'):
               previous_files.append(key.key)
    
    latest_file = previous_files[-1]
    print(latest_file)
    s3_resource = boto3.resource('s3')
    s3_object = s3_resource.Object(s3_bucket_name, latest_file)
    
    data = s3_object.get()['Body'].read().decode('utf-8').splitlines()
    
    lines = csv.reader(data)
    headers = next(lines)
    for line in lines:
        return line[0]
    
def upload_csv_s3(data_dictionary,s3_bucket_name,csv_file_name):
    data_dict = data_dictionary
    data_dict_keys = data_dictionary[0].keys()

    file_buff = StringIO()
    
    # writing csv data to file buffer
    writer = csv.DictWriter(file_buff, fieldnames=data_dict_keys)
    writer.writeheader()
    for data in data_dict:
        writer.writerow(data)
        
    # creating s3 client connection
    client = boto3.client('s3')
    
    # placing file to S3, file_buff.getvalue() is the CSV body for the file
    client.put_object(Body=file_buff.getvalue(), Bucket=s3_bucket_name, Key=csv_file_name)
    print('Done uploading to S3')
    
def lambda_handler(event, context):
    s3_bucket_name = 'your_bucket_name'
    pagedict = page_content(base_url,page_idx)
    print('Fetching the pages')
    print('Found {} houses'.format(len(pagedict)))
    print('Parsing houses')
    data_text = data_in_text(pagedict)    
    last_house_url = remove_already_seen_houses(s3_bucket_name)
    for i in data_text:
        if last_house_url==i['url']:
            data_text = data_text[:data_text.index(i)]
            
    if len(data_text)>0:
        dt_string = datetime.now().strftime("%Y-%m-%d_%H%M")
        csv_file_name =  'houses_'+dt_string +'.csv'
        upload_csv_s3(data_text,s3_bucket_name,csv_file_name)
        send_message = send_message_whatsapp(csv_file_name, len(data_text))
    
        response = {
            "body": data_text
        }
    
        return response
    else:
        pass
