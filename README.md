# Analysis of Social Media Data about Singapore

Singapore is a multi-racial and multi-cultural society with 4 main languages. This repository documents the journey to derive insights from textual social media data, from *Twitter* and *Instagram*, about Singapore with the following potential areas of exploration:

1) Trending topics

2) Sentiment Analysis on trending topics as well as internal vs external data

3) Named-Entity Recognition

4) Proportion of languages used


As no datasets on social media data about Singapore are publicly available, data will be mined from the aforementioned social media platforms using AWS before being used for analysis. As such, this project will be segmented into 4 parts:

1) Data mining using AWS

2) Data cleaning & labelling using NLTK and spaCy

3) Building/Training of various AI Models

4) Extraction and visualization of results


The following graph showcases the overall approach for this project:
![](images/AWS%20flowchart.jpg)


# Data mining using AWS

To collect data from *Twitter* and *Instagram*, we first need to create an EC2 instance on AWS to run the mining scripts indefinitely.

As the scripts are generally lightweight, we do not need heavy computing power. We will hence be using the the basic Amazon Linux instance which will be enough to fulfil our requirements. Although the instance is in the free-tier, please note there are hidden charges after a certain usage duration as well as for data transfer/storage options. Check out the pricing at this link: https://aws.amazon.com/ec2/pricing/

![](images/ec2.png)

Next, head to AWS RDS to create a database where we will store the collected text data. PostgreSQL will be used in this guide. Note that there are also hidden charges and it is important to first check out their pricing plans before creation of any instances.

![](images/postgres.png)

It will take a while for AWS to provision your resources. Once it is up and running, go into your database instance to copy its endpoint- we would need this to post data to our database from our ec2 instance. If you run into authentication problems, head to IAM and create a role that allows your AWS RDS instance to interface with your AWS EC2 instance: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html

![](images/endpoint.png)

We are now ready to run our mining scripts on our ec2 instance(almost)! Access to all tweets must first be authenticated by a user account's key and token. Follow this guide provided by Twitter to generate your access keys and tokens, which would be needed for our Twitter mining scipt: https://developer.twitter.com/en/docs/basics/authentication/oauth-1-0a/obtaining-user-access-tokens.

The *Tweepy* wrapper that modularizes the twitter API will be used to further simplify our mining script, install it in the ec2 instance using pip:
```
pip install tweepy
``` 

For Instagram, we will be mining the captions of posts related to Singapore. Scrapping data via the HTML way will allow us to mine more data as well as avoid having to use the Instagram API. However, they are very good at detecting mining bots and may excercise rate-limiting based on the IP address of the ec2 instance.

The *Instaloader* wrapper is an awesome, well documented library that like Tweepy, modularizes mining functions, making it really simple for us to mine data from instagram. Do check them out: https://github.com/instaloader/instaloader

```
pip install instaloader
```

Lastly, download the *twitter_crawler.py* and *insta_crawler.py* file from this repository and transfer them to your ec2 instance(using transfer protocols such as scp or putty). Do not forget to change the credentials of the database endpoint and Twitter access tokens.

Use the in-built terminal multiplexer to concurrently run both scripts:
```
tmux new -s twitter #creates new instance
tmux attach -t twitter #attaches to the newly created instance
python twitter_crawler.py #starts the mining script
Ctrl+B D #detaches from the terminal instance without terminating the script

--Repeat for insta_crawler.py--
```

To ensure that both scripts are actually mining, we can either access the database through pgAdmin4(browser interface for postgreSQL) or log in via the command line(need to have postgresql installed):
```
sudo -su postgres
psql -h (your aws rds endpoint)
\dt
```

You should see both the *instagram_captions* and the *singapore_tweets* tables present. Use SQL to confirm that they are not empty:
```
SELECT COUNT(id) from singapore_tweets;
SELECT COUNT(id) from instagram_captions;
```

![](images/db.png)

Due to rate limiting, it may take some time to mine a sizable amount of text data. It took around 2 weeks to mine a million tweets.

# --Other parts in progress--
