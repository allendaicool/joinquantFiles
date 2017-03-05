from bs4 import BeautifulSoup
import urllib
import sys  
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import * 


#inheretence
class Render(QWebPage):  
  def __init__(self):  
    self.app = QApplication(sys.argv)  
    QWebPage.__init__(self)  
    self.loadFinished.connect(self._loadFinished) 
    
      
  
  def _start_loading_url(self, url):
    self.mainFrame().load(QUrl(url))  
    self.app.exec_()   

  def _loadFinished(self, result):  
    self.frame = self.mainFrame()  
    #self.app.quit()  
  def __end_all_loading(self):
    self.app.quit() 
  
  

# for row in text[0].find_all('tr'):
# 	for col in row.find_all('td'):
# 		print col.get_text()
# 	print 'find----------'


#print soup.prettify().encode('utf-8')






# import requests
# from bs4 import BeautifulSoup

# session = requests.Session()
# headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome"\
#                         , "Accept":"text/html,application/xhtml+xml, "\
#                         "application/xml;q=0.9, image/webp, */*; q=0.8"}

# url = 'http://finance.sina.com.cn/realstock/company/sz002057/nc.shtml'
# req = session.get(url, headers=headers)
# print req.encoding
# bsobj = BeautifulSoup(req.text)
# print bsobj