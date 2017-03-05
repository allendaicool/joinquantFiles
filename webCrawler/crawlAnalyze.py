from bs4 import BeautifulSoup
import urllib
import sys  

money_flow_index = 2 
raio_over_circulating_market_index = 3
turn_over_ratio_index = 4


class beautifulSoupParse():

	def __init__(self):
		self.soup = None
		

	def is_numeric(self, num):
		try:
			float(num)
			return True
		except ValueError:
			pass
		return False

	def generate_soup_obj(self,html):		
		text = html.encode('utf-8')
		#str(unicode(html, 'ISO-8859-1', errors='strict').encode('ISO-8859-1'))
		soup = BeautifulSoup(text,'html.parser')
		self.soup = soup


	def find_money_flow_info(self,html):
		self.generate_soup_obj(html)
		flow_table_obj =  self.soup.find_all("div", class_='flow_table', id="FLFlow")
		try:
			money_flow_row = flow_table_obj[0].find_all('tr')[money_flow_index]
		except:
			#print ('length is ', len(flow_table_obj),len(flow_table_obj[0].find_all('tr')))
			return []


		num_array = []
		for  money_flow_entry in money_flow_row.find_all('td'):
			print ('text is ', money_flow_entry.get_text())
			money_num = money_flow_entry.get_text().rstrip()
			if self.is_numeric(money_num):
				num_array.append(float(money_num))
			else:
				num_array.append(0)
		return num_array


	def find_money_over_circulating_market_info(self):
		if self.soup == None:
			self.generate_soup_obj()
		flow_table_obj =  self.soup.find_all("div", class_='flow_table', id="FLFlow")
		raio_over_circulating_market_row = flow_table_obj[0].find_all('tr')[raio_over_circulating_market_index]
		num_array = []
		for  raio_over_circulating_market_entry in raio_over_circulating_market_row.find_all('td'):
			text = raio_over_circulating_market_entry.get_text()
			ratio = self.fetch_percentage_portion(text)
			num_array.append(float(ratio)/100)
		return num_array


	def fetch_percentage_portion(self, percentage_in_text):
		return percentage_in_text[:-1]

	def find_turn_over_ratio_info(self):
		if self.soup == None:
			self.generate_soup_obj()
		flow_table_obj =  self.soup.find_all("div", class_='flow_table', id="FLFlow")
		turn_over_ratio_row = flow_table_obj[0].find_all('tr')[turn_over_ratio_index]
		num_array = []
		for  turn_over_ratio_entry in turn_over_ratio_row.find_all('td'):
			text = turn_over_ratio_entry.get_text()
			ratio = self.fetch_percentage_portion(text)
			num_array.append(float(ratio)/100)
		return num_array









