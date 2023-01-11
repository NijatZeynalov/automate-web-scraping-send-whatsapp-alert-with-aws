# Scraping Azerbaijani real estate website and sending whatsapp message with AWS Lambda function that automatically triggered by Amazon CloudWatch.

## Motivation

People who want to buy a house face enough difficulties. Have you ever you encountered a situation where think that "This house is a very affordable price, I will call" but after calling the the owner of the house says that the house has already been leave deposit?

In particular, a house offered at a reasonable price on the sites is quickly seen by other customers or brokers, and we are late for a house offered at a reasonable price. So what can we do about it?

## Objective

In this project, I perform web scrapping of "kub.az" real estate website. The reason that I have chosen this website is that, it brings house ads from all real estate websites of Azerbaijan. To put it briefly, I use AWS Lambda function which scrapes website in every 30 minutes and if a new house added, it creates a new csv file in S3 bucket and sends this file with a message to my whatsapp number during each run. The project workflow is given below.

![arthitecture](https://user-images.githubusercontent.com/31247506/211852593-67b1324c-f792-4bef-b22c-1c3074dc7d51.png)


To replicate this at home, you’ll need an AWS account, a grasp of python, an API key for twilio.

sekil + butun stepler

