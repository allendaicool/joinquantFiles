
# -*- coding: utf-8 -*-

from scrapy import Render
from datetime import datetime  
from crawlAnalyze import beautifulSoupParse
from dateutil import tz
from drawline import *
import time

from PySide import QtCore, QtGui, QtWebKit
import sys


def loadPage(url):
      page = QtWebKit.QWebPage()
      loop = QtCore.QEventLoop() # Create event loop
      page.mainFrame().loadFinished.connect(loop.quit) # Connect loadFinished to loop quit
      page.mainFrame().load(url)
      loop.exec_() # Run event loop, it will end on loadFinished
      return page.mainFrame().toHtml()



default_url_prefix = 'http://finance.sina.com.cn/realstock/company/'
default_url_suffix  = '/nc.shtml'

def scrape(html):
	obj = beautifulSoupParse()
	money_flow_array = obj.find_money_flow_info(html)
	return money_flow_array


def get_complete_url(stockList):
	urls = []
	for stock in stockList:
		urls.append(default_url_prefix + stock + default_url_suffix)
	return urls


def get_line_data_dict(stock_list,money_flow_data):
	line_data = {}
	for idx, stock in enumerate(stock_list):
		line_data[stock] = money_flow_data[idx]
	return line_data



if __name__ == "__main__":

	app = QtGui.QApplication(sys.argv)

	stock_list = ['sz300354', 'sz300120','sz300321','sz300483','sz300489']
	urls = get_complete_url(stock_list)
	print urls
	# webkit_obj = Render([x for x in urls], cb=scrape)
	

	from_zone = tz.gettz('UTC')
	to_zone = tz.gettz('Asia/Shanghai')
	shanghaiTime = datetime.utcnow().replace(tzinfo=from_zone)
	shanghaiTime = shanghaiTime.astimezone(to_zone)
	open_time_morning = datetime(shanghaiTime.year, shanghaiTime.month, shanghaiTime.day,9, 32).replace(tzinfo=to_zone)
	close_time_morning = datetime(shanghaiTime.year, shanghaiTime.month, shanghaiTime.day,11, 30).replace(tzinfo=to_zone)
	open_time_afternoon = datetime(shanghaiTime.year, shanghaiTime.month, shanghaiTime.day,13, 00).replace(tzinfo=to_zone)
	close_time_afternoon = datetime(shanghaiTime.year, shanghaiTime.month, shanghaiTime.day,15, 00).replace(tzinfo=to_zone)
	
	count  = 0
	running = True

	plot_inst = drawRealTimeMoneyFlow()
	plot_inst.initilize_each_plot(stock_list)

	while running :
		utc_time = datetime.utcnow()
		utc_time = utc_time.replace(tzinfo=from_zone)
		local = utc_time.astimezone(to_zone)

		if (local > open_time_morning and local < close_time_morning) or (local > open_time_afternoon and local < close_time_afternoon):
			money_flow_array_list = []
			for url in urls:
				html = loadPage(url)
				money_flow_array = scrape(html)

				money_flow_array_list.append(money_flow_array)

			line_data  = get_line_data_dict(stock_list,money_flow_array_list)
			plot_inst.update_each_plot(line_data)
		if local> close_time_afternoon:
			running = False

		time.sleep(30)

	plt.show()
	app.exit()

