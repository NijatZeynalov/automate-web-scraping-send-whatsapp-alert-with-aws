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
