class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

import sys

sys.stdout = Unbuffered(sys.stdout)
sys.stdin = Unbuffered(sys.stdin)

import requests,json,sys
from threading import Thread
import urllib
import time
from pooky import generate_cookies
# main class
class Superman(object):

    # constructor
    def __init__(self, data, port):

        # create a new web session (keep cookies and other data)
        self.r = requests.Session()

        slot = self.importData(data)

        # slot info
        self.variantId = None
        self.sizeId = None
        self.queueId = None
        self.profile = slot
        self.size = self.profile['size']
        self.keyword = self.profile['keyword']
        self.category = self.profile['category']
        self.color = self.profile['color']
        self.port = port
        self.proxies={}
        # only support for one proxy
        if len(self.profile['proxies'])>2:
            self.parsedProxy = self.profile['proxies'].split(':')
            if len(self.parsedProxy)==2:
                self.proxies = {
                'http':'http://'+self.parsedProxy[0]+':'+self.parsedProxy[1],
                'https':'https://'+self.parsedProxy[0]+':'+self.parsedProxy[1]
                }
            elif len(self.parsedProxy)==4:
                self.proxies = {
                'http':'http://'+self.parsedProxy[2]+':'+self.parsedProxy[3]+'@'+self.parsedProxy[0]+':'+self.parsedProxy[1],
                'https':'https://'+self.parsedProxy[2]+':'+self.parsedProxy[3]+'@'+self.parsedProxy[0]+':'+self.parsedProxy[1]
                }
            else:
                print 'error<<proxy'
                sys.exit()
            self.r.proxies.update(self.proxies)

    def importData(self, data):

        # split line by ,
        # make sure to check for "s for data-sensitive commas
        quoteOpen = False
        slot = []
        x = -1 # index starts at 0
        lastComma = 0
        for i in data:
            x += 1
            if i == "\"":
                quoteOpen = not quoteOpen

            if quoteOpen == True:
                continue
            else:
                if i == ",":
                    cut = data[lastComma:x]
                    if cut == '' or cut == None:
                        slot.append(cut)
                        continue
                    if cut[0] == "\"" and cut[len(cut)-1] == "\"":
                        cut = cut[1:len(cut)-1]
                    slot.append(cut)
                    lastComma = x+1
        
        # last cut wont be caught
        cut = data[lastComma:len(data)]
        slot.append(cut)
        
        if len(slot) != 19:
            print 'error<<baddata'
            sys.exit()

        # some_email@mailinator.com,firstname,lastname,fullname,4709 Brabant way,Elk Grove CA,95757,Elk Grove,CA,2078483726,1234567891234567,12,2010,102,large,Bag,Bag,Black,
        # csv style data
        slotProfile = {
            'email':		slot[0],
            'firstname':	slot[1],
            'lastname':		slot[2],
            'fullname':		slot[3],
            'address1':		slot[4],
            'address2':		slot[5],
            'zip':			slot[6],
            'city':			slot[7],
            'state':		slot[8],
            'phone':		slot[9],
            'card':			slot[10],
            'expMM':		slot[11],
            'expYYYY':		slot[12],
            'cvv':			slot[13],
            'size':			slot[14],
            'keyword':		slot[15],
            'category':		slot[16],
            'color':		slot[17],
            'proxies':		slot[18]
        }

        # add key-value data to self.slotDict
        return slotProfile

    def getCaptcha(self):
        r = self.r.get(url='http://127.0.0.1:' + str(self.port) + '/captcha')
        body = r.content
        print body
        if body == 'N/A':
            raise Exception('Captcha failed')
        else:
            return body

    # find item with keyword
    def searchMobileFeed(self):
        print 'progress<<25'
        try:

            # use mobile_stock.json to look for available items
            url = 'https://www.supremenewyork.com/mobile_stock.json'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9,la;q=0.8,fr;q=0.7',
                'Host': 'www.supremenewyork.com',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
                'Connection': 'Keep-Alive'
            }
            request = self.r.get(url=url,headers=headers)
            requestJ = json.loads(request.content)

            # check if category exists
            # print requestJ['products_and_categories'].keys()
            if self.category not in requestJ['products_and_categories']:
                print 'error'
                sys.exit()

            category = requestJ['products_and_categories'][self.category]

            # iterate items in category
            for item in category:
                item['name'] = item['name'].encode('utf-8')

                # if a variant is found, store it and return
                if self.keyword.lower() in item['name'].lower():
                    self.variantId = item['id']
                    # print 'Found {} with item id {}'.format(item['name'], self.variantId)

                    return True
            
            return False

        except Exception, e:
            print 'error<<networkError'
            # print e
            # print self.profile['email'] + ' : Error getting mobile feed of products'

    def getItem(self):
        print 'progress<<50'
        flag = ''
        while 'styles' not in flag:
            time.sleep(1)
            try:
                url = 'https://www.supremenewyork.com/shop/{}.json'.format(self.variantId)
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9,la;q=0.8,fr;q=0.7',
                    'Cache-Control': 'max-age=0',
                    'Connection': 'keep-alive',
                    'Host': 'www.supremenewyork.com',
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
                }
                request = self.r.get(url=url,headers=headers,proxies=self.proxies)
                flag = request.content
                requestJ = json.loads(request.content)

                sizes =[]
                colors= []
                colorIndex = ''
                selectedSize=''
                if len(requestJ['styles'])>1:
                    for items in requestJ['styles']:
                        colors.append(items['name'])
                        if self.color.lower() in items['name'].lower():
                            colorIndex=len(colors)-1
                else:
                    colorIndex=0
                if len(requestJ['styles'][colorIndex]['sizes'])>1:
                    for items in requestJ['styles'][colorIndex]['sizes']:
                        currentSize = items['name'].encode('utf-8')
                        sizes.append(currentSize)
                        if self.size.lower() in currentSize.lower() and self.size.lower() not in 'large': #and self.size.lower() not in 'large':
                            self.sizeId = items['id']
                            selectedSize = currentSize
                        elif 'Large' == currentSize and ('large' == self.size.lower() or 'l' == self.size.lower()):
                            self.sizeId = items['id']
                            selectedSize = currentSize
                else:
                    # print self.profile['email'] + ' : Detected one size item...'
                    self.sizeId = requestJ['styles'][colorIndex]['sizes'][0]['id']
                # print self.profile['email'] + ' : Found size {}with size ID {}'.format(selectedSize,self.sizeId)
            except Exception, e:
                print 'error<<networkError'
                sys.exit()
                # print e
                # print self.profile['email'] + ' : Error getting product info'

    def checkout(self):
        print 'progress<<75'
        flag = ''
        try:
            if len(str(int(self.keyword)))==5:
                # print self.profile['email']+' : Detected variant input!'
                self.sizeId = self.keyword
        except:
            pass

        while 'status' not in flag:
            try:
                self.profile['zip']= self.profile['zip'].split(',')[1]
                url = 'https://www.supremenewyork.com/checkout.json?store_credit_id=&from_mobile=1&cookie-sub=%257B'+'%'+'2522'+'{}%'.format(self.sizeId)+'2522%253A1%257D&same_as_billing_address=1&order%5Bbilling_name%5D={}+{}&order%5Bemail%5D={}&order%5Btel%5D={}-{}-{}&order%5Bbilling_address%5D={}&order%5Bbilling_address_2%5D={}&order%5Bbilling_zip%5D={}&order%5Bbilling_city%5D={}&order%5Bbilling_state%5D={}&order%5Bbilling_country%5D=USA&credit_card%5Bcnb%5D={}+{}+{}+{}&credit_card%5Bmonth%5D={}&credit_card%5Byear%5D={}&credit_card%5Brsusr%5D={}&order%5Bterms%5D=0&order%5Bterms%5D=1&is_from_ios_native=1&g-recaptcha-response={}'.format(self.profile['firstname'],self.profile['lastname'],urllib.quote_plus(self.profile['email']),self.profile['phone'][0:3],self.profile['phone'][3:6],self.profile['phone'][6:10],urllib.quote_plus(self.profile['address1']),urllib.quote_plus(self.profile['address2']),self.profile['zip'],urllib.quote_plus(self.profile['city']),self.profile['state'],self.profile['card'][0:4],self.profile['card'][4:8],self.profile['card'][8:12],self.profile['card'][12:16],self.profile['expMM'],self.profile['expYYYY'],self.profile['cvv'],self.getCaptcha())
                cookieData = 'cart=1+item--{}%2C21346; pure_cart=%7B%22'.format(self.sizeId)+str(self.sizeId)+'%'+'22%3A1%7D'
                headers = {
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9,la;q=0.8,fr;q=0.7',
                    'Host': 'www.supremenewyork.com',
                    'Referer': 'https://www.supremenewyork.com/mobile',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': 'https://www.supremenewyork.com',
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Mobile/14A403',
                    'Connection': 'Keep-Alive',
                    'Cookie': cookieData,
                }
                request = self.r.post(url=url,headers=headers,cookies=generate_cookies())
                flag = request.content
                requestJ = json.loads(request.content)
            except Exception, e:
                print 'error<<Internal failure'
                print e
                sys.exit()
                # print e
                # print self.profile['email'] + ' : Error checking out'
        if requestJ['status'] == 'queued':
            self.queueId = requestJ['slug']
            print 'progress<<90'
        elif requestJ['status']=='dup':
            # print self.profile['email'] + ' : Duplicate order!'
            print 'error<<duplicate'
            sys.exit()
        elif requestJ['status']=='outOfStock':
            # print self.profile['email'] + ' : Out of stock!'
            print 'error<<OOS'
            sys.exit()
        elif requestJ['status']=='failed':
            print 'error<<failedToQueue'
            sys.exit()
        else:
            print 'error<<unknown'
            sys.exit()
    def queue(self):
        print 'progress<<90'
        url = 'https://www.supremenewyork.com/checkout/{}/status.json'.format(self.queueId)
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,la;q=0.8,fr;q=0.7',
            'Host': 'www.supremenewyork.com',
            'Referer': 'https://www.supremenewyork.com/mobile',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.supremenewyork.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Mobile/14A403',
            'Connection': 'Keep-Alive',
        }
        flag = 'queued'
        while 'queued' in flag:
            try:
                request = self.r.get(url=url,headers=headers)
                requestJ = json.loads(request.content)
                flag = request.content
                # print self.profile['email'] + ' : Ordering...'
            except:
                print 'error'
                # print self.profile['email'] + ' : Error queueing'
        if requestJ['status']=='failed':
            print 'error'
            if requestJ['mpa'][0]['Failure Reason'] == None:
                # print self.profile['email'] + ' : Failed to order product | Failure Reason: Most likely payment error'
                print 'error<<likelypayment'
                sys.exit()
            elif requestJ['mpa'][0]['Sold Out']==True:
                # print self.profile['email'] + ' : Failed to order product | Failure Reason: Most likely payment error'
                print 'error<<outofstock'
                sys.exit()
        elif requestJ['status']=='paid':
            print 'progress<<100'
            print 'success<<Your order number is: {}'.format(requestJ['id'])
            # print self.profile['email'] + ' : SUCCESS! Order number {}'.format(requestJ['id'])


if __name__ == '__main__':

    # try:
    #     licenseS = sys.argv[2]
    #     licenseR = requests.post('http://127.0.0.1:8080/keys/check', data = { 'secret': licenseS })
    #     print licenseS
    #     print dir(licenseR)
    #     print licenseR.content
    #     if licenseR.status_code != 200:
    #         print 'error<<badlicense'
    #         sys.exit()
    # except Exception, e:
    #     print 'error<<licenseoffline'
    #     sys.exit()

    importData = ' '.join(sys.argv[2:])
    print 'launch<<' + importData + ''
    i = Superman(importData, sys.argv[1])
    
    i.getCaptcha()

    keyword = i.profile['keyword']
    if not isinstance(keyword, int) or len( str(keyword) ) != 5:
        i.searchMobileFeed()
        i.getItem()
    
    i.checkout()
    
    while True:
        time.sleep(1)
        i.queue()
