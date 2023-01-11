# Scraping Azerbaijani real estate website and sending whatsapp message with AWS Lambda function that automatically triggered by Amazon CloudWatch.

## Motivation

People who want to buy a house face enough difficulties. Have you ever you encountered a situation where think that "This house is a very affordable price, I will call" but after calling the the owner of the house says that the house has already been leave deposit?

In particular, a house offered at a reasonable price on the sites is quickly seen by other customers or brokers, and we are late for a house offered at a reasonable price. So what can we do about it?

![arthitecture](https://user-images.githubusercontent.com/31247506/211854843-399cad25-0866-4a3d-b886-9abd1c1e66d6.jpeg)

__So, how about if newly added houses matching our desired price are sent to us via whatsapp?__


## Objective

In this project, I perform web scrapping of "kub.az" real estate website. The reason that I have chosen this website is that, it brings house ads from all real estate websites of Azerbaijan. To put it briefly, I use AWS Lambda function which scrapes website in every 30 minutes and if a new house added, it creates a new csv file in S3 bucket and sends this file with a message to my whatsapp number during each run. The project workflow is given below.

![arthitecture](https://user-images.githubusercontent.com/31247506/211852593-67b1324c-f792-4bef-b22c-1c3074dc7d51.png)


To replicate this at home, you’ll need an AWS account, a grasp of python, an API key for twilio.

Here’s an outline of the steps I followed.

1. Web scraping using Python
2. Create Amazon S3 Bucket
3. Create IAM Policy & Role
4. Setup AWS Lambda Function that save csv file to S3 bucket and send a message via whatsapp
6. Automate AWS Lambda function using Amazon CloudWatch

### 1. Web scraping using Python

In this section we will take care of web scraping part. I will provide the python code to perform web scrapping of kub.az using bs4. First step to import required Python Libraries and define base_url. In this url, we will write down our desired conditions (price range, location and etc.).

```python
from bs4 import BeautifulSoup
import requests
from datetime import date
```
Then we create a function which will return the number of houses available on the webpage. A function page_content that collects HTML data as text and collects multiple pages of text data in form of 'pagedict' list. The function takes the key parameters such as base url and index per page.

```python
def page_content(base_url,page_idx):
    pagedict = []
    for item in range(page_idx):
        
        page = requests.get(base_url+(str(item + 1)))
        if page.status_code !=200:
                raise Exception(f"Unable to download {base_url+(item)}")
        page_content = page.text
        pagedict.append(page_content)
    return pagedict
```
We will then extract and compile information after downloading the data using requests and beautiful soup libraries. data_in_text collects the key tags and classes from the html document and creates a large property data dictionary.

```python
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
    
data_text = data_in_text(pagedict,page_doc)
```
We can collect all essential information in connection with the property using the above custom formula, and information will be stored in form of a dictionary.

![arthitecture](https://user-images.githubusercontent.com/31247506/211865710-d040b1b8-0bd2-41e9-90fb-c8b72356761f.png)


### 2. Create Amazon S3 Bucket

I create an Amazon S3 bucket in which I will store the final cvs file. In simple terms Amazon S3 is an object storage service that offers industry-leading scalability, data availability, security, and performance. There are lots of configuration options available for Amazon S3 bucket but for the sake of simplicity I am keeping all options as is. Scroll down the page and click "Create Bucket" button. 

After creating the bucket, be sure that you have given public access to the objects, because your lambda code will send this object in the whatsapp message, so user should have access.

![arthitecture](https://user-images.githubusercontent.com/31247506/211870024-13a5cec3-e828-470c-893c-d4357a8ca22f.png)

### 3. Create Amazon Identity and Access Management (IAM) Policy & Role

In this step we will create necessary Policies & Roles to put the data into Amazon S3 bucket and write into CloudWatch Logs. Later on we will assign this Role to the Lambda Function. Click on "Policies" which will open page listing all available policies, then type S3 in the search bar and type PutObject. Provide the proper name to the policy, I gave the name as AWSS3PutObject and then click "Create policy" button. If everything went well, the new AWSS3PutObject policy should be available in the list. 

On the left Panel there should be option to select "Roles" and create the role named AWSS3PutRole.Then type AWSS3PutObject in the search bar and select the same policy. This role will be assigned in the later stages.

### 4. Setup AWS Lambda Function

Next we will create and configure AWS Lambda, in which the web scraping Python code will executed. The Python code used for web scraping needs to install requests python library also our code requires twilio. Each platform has their own ways to install various dependent packages and drivers, In case of AWS Lambda there is something called Layers to deploy the packages. First we install / download required libraries in a local folder, then we zip the folder and upload the zip file to AWS Lambda layers.

On the left panel Click Functions and then Click Create function button, keep default selection Author from scratch as is and provide appropriate function name. Then click on Configuration tab and then click Edit button. Set Memory as 1024 and Timeout as 5 min and click Save button.

By Default Lambda function provides python script called as lambda_function.py and our code will replace default one. Once its done click on Deploy button, then  click the Test button.

![](https://user-images.githubusercontent.com/31247506/211873463-28a88476-f4ac-4780-8c28-ca9e8441bc05.png)


### 5. Automate AWS Lambda function using Amazon EventBridge CloudWatch

The most of the heavy lifting is already done, Lambda function is running as expected. Now its time to Automate the Lambda function run. This is fairly easy step and we are going to use [Amazon EventBridge] (https://aws.amazon.com/eventbridge/) service. On the left panel of Amazon Cloudwatch, click Rules and then click Create rule button. Set the appropriate rule name, in rate expression section set value as you want (30 mins. in my case). Then we will select our lambda function as a target. After this, trigger is assigned to Lambda function. The Lambda function should run after every 30 minutes and it create a new csv file in S3 bucket and send whatsapp message.

### 6. Conclusion

In this project, we have done following concepts

Creation of Amazon S3 bucket, IAM policies & Role.

Creation & configuration AWS Lambda functions.

Automation of AWS Lambda runs. 
