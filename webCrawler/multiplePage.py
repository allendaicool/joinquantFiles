#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

class Render(QWebPage):  
  def __init__(self, urls, cb):
    self.app = QApplication(sys.argv)  
    QWebPage.__init__(self)  
    self.loadFinished.connect(self._loadFinished)  
    self.urls = urls  
    self.cb = cb
    #self.crawl()  
    #self.app.exec_()  
      
  def restore_urls(self, urls):
    self.urls = urls

  def start_loading(self):
    print 'start scraping'
    self.crawl() 
    self.app.exec_()
    print 'DDDDDD'  
    # tmp = self.line_data
    # self.line_data = []
    return 'ok'

  def crawl(self):  
    if self.urls:  
      url = self.urls.pop(0)  
      print 'Downloading', url  
      self.mainFrame().load(QUrl(url))  
    else:  
      self.app.quit()  
        
  def _loadFinished(self, result):  
    frame = self.mainFrame()  
    url = str(frame.url().toString())  
    html = frame.toHtml()  
    self.cb(url, html)
    self.crawl()  


def scrape(url, html):
    pass # add scraping code here

count = 0 
urls = ['http://finance.sina.com.cn/realstock/company/sz300354/nc.shtml', 'http://finance.sina.com.cn/realstock/company/sz300120/nc.shtml', 'http://finance.sina.com.cn/realstock/company/sz300321/nc.shtml', 'http://finance.sina.com.cn/realstock/company/sz300483/nc.shtml', 'http://finance.sina.com.cn/realstock/company/sz300489/nc.shtml']

r = Render([x for x in urls], cb=scrape)
while count < 3:
  r.start_loading()
  r.restore_urls( [x for x in urls])
#     self.urls urls
  count +=1




# import sys
# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
# from PyQt4.QtWebKit import *
# #from crawlAnalyze import *

# class Render(QWebPage):  
#   def __init__(self, urls, cb):
#     self.app = QApplication(sys.argv)  
#     QWebPage.__init__(self)  
#     self.loadFinished.connect(self._loadFinished)  
#     self.cb = cb
#     self.urls = urls
#     # self.line_data = []

#   def restore_urls(self, urls):
#     self.urls = urls

#   def start_loading(self):
#     print 'start scraping'
#     self.crawl() 
#     self.app.exec_()
#     print 'DDDDDD'  
#     # tmp = self.line_data
#     # self.line_data = []
#     return 'ok'

#   def crawl(self):
#     if self.urls:  
#       url = self.urls.pop(0)  
#       self.mainFrame().load(QUrl(url))
#       print 'BBBBBBB'
#     else:  
#       self.app.quit()  
#       print 'quit'
        
#   def _loadFinished(self, result):  
#     print 'CCCCCCC'
#     frame = self.mainFrame()  
#     url = str(frame.url().toString()) 
#     #print ('uril is ' , url)
#     print ('AAAAAA')
#     html = frame.toHtml()  
#     #num_array = 
#     self.cb(url, html)
#     #self.line_data.append(num_array)
#     self.crawl()  


# def scrape(url, html):
#   print 'ok'
#   # m
#   return


# def get_line_data_dict(stock_list, webkit_obj,urls):
#   money_flow_data = webkit_obj.start_loading()
#   print ('money_flow_data is ',money_flow_data)  
#   line_data = {}
#   for idx, stock in enumerate(stock_list):
#     line_data[stock] = money_flow_data[idx]

#   webkit_obj.restore_urls([x for x in urls])
#   return line_data


# count = 0
# #urls_backUp = ['http://finance.sina.com.cn/realstock/company/sz300354/nc.shtml', 'http://finance.sina.com.cn/realstock/company/sz300120/nc.shtml', 'http://finance.sina.com.cn/realstock/company/sz300321/nc.shtml', 'http://finance.sina.com.cn/realstock/company/sz300483/nc.shtml', 'http://finance.sina.com.cn/realstock/company/sz300489/nc.shtml']
# #urls = ['http://finance.sina.com.cn/realstock/company/sz300354/nc.shtml', 'http://finance.sina.com.cn/realstock/company/sz300120/nc.shtml', 'http://finance.sina.com.cn/realstock/company/sz300321/nc.shtml', 'http://finance.sina.com.cn/realstock/company/sz300483/nc.shtml', 'http://finance.sina.com.cn/realstock/company/sz300489/nc.shtml']
# urls_backUp = ['http://webscraping.com', 'http://webscraping.com/blog']  
# obj = Render(urls_backUp, cb=scrape)
# while count < 3:


#   # obj.start_loading()
#   # obj.restore_urls([x for x in urls])
#   # money_flow_data = 
#   obj.start_loading()
#   # print ('money_flow_data is ',money_flow_data)  
#   # line_data = {}
#   # for idx, stock in enumerate(stock_list):
#   #   line_data[stock] = money_flow_data[idx]

#   obj.restore_urls([x for x in urls_backUp])

#   stock_list = ['a','b','c' ,'d','e']
#   count += 1


