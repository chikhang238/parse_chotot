import re
import pandas as pd
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from lxml import html
from os import listdir

MODEL_PATH = 'parse_model.csv'
CONFIG_PATH = 'config/'
COMMA = ','
PHONE = 'phone'


class parseHTML(object):
    """
    Retreive information from HTML which is stored in elasticsearch
    @param name is the name of the HTML database
    @param saved_name is the name of saved database
    @param es is the ElasticSearch object
    @param result is the dictionary of post information which are retreived
    """

    def __init__(self, saved_name, name):
        self.name = name
        self.saved_name = saved_name
        self.es = Elasticsearch()
        self.configs = dict()
        self.result = dict()

    def connect_to_es(self):
        return self.es.search(index=self.name, body={'size': 10000, "query": {"match_all": {}}})

    def read_config(self):
        model = pd.read_csv(MODEL_PATH)
        print(model)
        for i, regex in enumerate(model['url_regex']):
            self.configs[regex] = None

        for conf in listdir(CONFIG_PATH):
            print(CONFIG_PATH + conf)
            df = pd.read_csv(CONFIG_PATH + conf)
            temp = model[model['id'].str.contains(conf)]
            print(temp['url_regex'].iloc[0])
            self.configs[temp['url_regex'].iloc[0]] = df.fillna('')

        print('CONFIG :')
        print(self.configs)

    def check_url(self, url):
        for regex in self.configs:
            if bool(re.match(regex, url)):
                return self.configs[regex]

    def main(self):
        """
        Retreive necessary information for each document and save to elasticsearch
        """
        parse = self.connect_to_es()
        self.read_config()

        print('NUMBER OF POSTS:', parse['hits']['total'])
        posts = parse['hits']['hits']

        count = 1
        for post in posts:
            print('** POST NUMBER:', count)
            print('** POST ID:', post['_id'])
            doc = dict()
            print(post['_source']['url'])
            doc['url'] = post['_source']['url']
            
            df = self.check_url(doc['url'])

            page_source = post['_source']['document']
            profile_source = post['_source']['user_profile']
            tree = html.fromstring(page_source + profile_source)

            doc['data_details'] = dict()
            for index, row in df.iterrows():
                print(index)
                feature = row['features']
                
                attr = ''
                if feature != '':
                    attr_lst = tree.xpath(str(feature))
                    if len(attr_lst) != 0:
                        if row['pos_take'] != '':
                            attr = attr_lst[int(row['pos_take'])].text
                        else:
                            for element in attr_lst:
                                attr = attr + element

                doc['data_details'][row['ID']] = attr

            self.result[post['_id']] = doc
            self.save_to_es(post['_id'], doc)
            count += 1

        #        if bool(row['regex_take_bool']) == False: 
        #             doc['data_details'][row['ID']] = attr.text
        #         else:
        #             # if row['ID'] == PHONE:
        #             match = re.search(row['regex_take'], attr['href'])            
        #             # else:
        #             #     match = re.search(row['regex_take'], str(attr.text))
        #       doc['data_details'][row['ID']] = match.group(int(row['pos_take_regex']))
                

        print('PARSING DONE')
        print(self.result['da34bcf7e41a317a43adfe9e6dc7636a']['data_details'])

    def save_to_es(self, id, doc):
        h = id
        if not self.es.exists(index=self.saved_name, id=h, doc_type='_doc'):
            doc = doc
            self.es.index(index=self.saved_name, id=h, body=doc, doc_type='_doc')

parse = parseHTML('info', 'urls')
# # parse_info = parse.connect_to_es()
# # print(parse_info.keys())
# # print(parse_info['hits']['hits'][0]['_source']['url'])
# # print(len(parse_info['hits']['hits']))
# # print(parse_info['hits']['total'])
# # user1 = parse_info['hits']['hits'][1]['_source']
# # print(user1['url'])
# # #soup = BeautifulSoup(user1['document'], 'html.parser')
# # tree = html.fromstring(user1['document'] + user1['user_profile'])

# # print('****Title******')
# # # title = soup.findAll(attrs={'itemprop' : 'name'})
# # # for i in title:
# # #     print(i.text)
# # # match = re.search('.+', title[0].text)
# # # url = match.group()
# # # print(url)
# # title = tree.xpath("//h1[@class='styles__Title-sc-14jh840-1 lgidFF' and @itemprop='name']")
# # print(title)
# # for i in title:
# #     print(i.text)

# # print("***Price****")
# # # price = soup.findAll(attrs={'class': 'styles__Price-sc-14jh840-4 jBNDPj', 'itemprop' : 'price'})
# # # for i in price:
# # #     print(i.text)
# # # #print(price[0].text)
# # price = tree.xpath("//span[@class='styles__Price-sc-14jh840-4 jBNDPj' and @itemprop='price']")
# # for i in price:
# #     print(i.text)

# # print("****Description****")
# # # description = soup.findAll(attrs={'class': 'styles__DescriptionAd-sc-14jh840-7 iHuKsX', 'itemprop' : 'description'})
# # # for i in description:
# # #     print(i.text)
# # # #print(description[0].text)
# # des = tree.xpath("//p[@class='styles__DescriptionAd-sc-14jh840-7 iHuKsX' and @itemprop='description']")
# # for i in des:
# #     print(i.text)

# # print("****Name*****")
# # # user = soup.findAll(attrs={'class': 'styles__NameDiv-jjbnsh-3 bWjZeW'})
# # # for i in user:
# # #     print(i.text)
# # # #print(user[0].text)
# # name = tree.xpath("//span[@class='name']")
# # for i in name:
# #     print(i.text)

# # print('****Poster s address****')
# # addr = tree.xpath("//div[contains(text(), 'Địa chỉ:')]/span")
# # for i in addr:
# #     print(i.text)


# # print("*****Phone*****")
# phone = soup.findAll(attrs={'id': 'call_phone_btn'})
# for i in phone:
#     print(i['href'])
# # print(phone[0]['href'])
# # match = re.search('(\w+):(\d+)', phone[0]['href'])
# # url = match.group(2)
# # print(url)
# phone = tree.xpath("//span[@class='name']")
# for i in phone:
#     print(i.text)

# print("****Status*****")
# status = soup.findAll(attrs={'class': 'media-body media-middle'})
# for s in status:
#     print(str(s.text))
# # match = re.search('([\w\s]+):\s([\w\s]+)', str(status[4].text))
# # url = match.group(2)
# # print(url)
# # status = soup.findAll(attrs={'class': 'fz13'})
# print(status[0].text)
# print('*'*10)
# a = "class: styles__Title-sc-14jh840-1 lgidFF, itemprop : name"
# dic = dict(item.split(": ") for item in a.split(", "))
# print(dic['class'])
# print(',' in a)
parse.main()



