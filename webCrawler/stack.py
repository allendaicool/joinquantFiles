# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui, QtWebKit
import sys

def loadPage(url):
      page = QtWebKit.QWebPage()
      loop = QtCore.QEventLoop() # Create event loop
      page.mainFrame().loadFinished.connect(loop.quit) # Connect loadFinished to loop quit
      page.mainFrame().load(url)
      loop.exec_() # Run event loop, it will end on loadFinished
      return page.mainFrame().toHtml()

app = QtGui.QApplication(sys.argv)

urls = ['http://finance.sina.com.cn/realstock/company/sz300354/nc.shtml']
count  = 0
while count < 3:
      for url in urls:
            print '-----------------------------------------------------'
            print 'Loading ' + url
            html = loadPage(url)
            text = html.encode('utf-8')
            print text
      #print html
      count += 1

app.exit()
