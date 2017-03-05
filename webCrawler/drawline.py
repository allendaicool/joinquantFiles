
import numpy as n
import pylab as p
import time
import matplotlib.pyplot as plt
import numpy as np


from matplotlib.font_manager import FontProperties
fontP = FontProperties()
fontP.set_size('xx-small')

class drawRealTimeMoneyFlow():
	def __init__(self, num_plot = 5):
		self.fig = plt.figure(1)
		if num_plot == 5:
			self.length = 2
			self.width = 3
		else:
			self.length = num_plot
			self.width  = 1
		self.ax_dict = {}
		self.line_dict = {}
		self.default_color = ['red','blue', 'green', 'yellow']
		pass

	def initilize_each_plot(self,stock_set):
		count = 1
		for stock in stock_set:
			ax = self.fig.add_subplot(self.length, self.width, count)
			ax.set_title(stock)
			self.ax_dict[stock] = ax
			self.line_dict[ax] = []
			initial_value = [0,0,0,0]
			for idx, money_flow_type_amount in enumerate(initial_value):
				line, = ax.plot(0, money_flow_type_amount,  color = self.default_color[idx])
				self.line_dict[ax].append(line)
			count += 1
			ax.legend(['s','m','x','xl'], loc='upper left',prop = fontP)
		plt.tight_layout()
		plt.pause(1)
		# plt.draw()

	def update_each_plot(self, line_data):
		print 'get here'
		for key, value in line_data.items():
			ax = self.ax_dict[key]
			line_pool = self.line_dict[ax]

			for idx, money_flow in enumerate(value):
				x_data = line_pool[idx].get_xdata()
				x_data = np.concatenate((x_data,[x_data[-1] + 1]))
				y_data = np.concatenate((line_pool[idx].get_ydata(),[money_flow]))

				line_pool[idx].set_data(x_data,y_data)
			ax.relim()
			ax.autoscale_view()
		# plt.draw()
		plt.tight_layout()
		plt.pause(1)

	def finalize_plot(self):
		plt.show()


# inst = drawRealTimeMoneyFlow()
# stock_set = set()
# stock_set.add('002057')
# stock_set.add('600120')
# stock_set.add('500120')
# stock_set.add('000906')
# stock_set.add('000000')
# line_data = {}
# # line_data['002057'] = [1,2,3,4]
# # line_data['600120'] = [4,3,2,1]
# # line_data['500120'] = [5,1,2,-5]
# # line_data['000906'] = [-1,9,2,-5]
# # line_data['000000'] = [-10,10,1,-1]
# inst.initilize_each_plot(stock_set)
# print 'get here------'


# line_data['002057'] = [1,2,3,4]
# line_data['600120'] = [4,3,2,1]
# line_data['500120'] = [5,1,2,-5]
# line_data['000906'] = [-1,9,2,-5]
# line_data['000000'] = [-10,10,1,-1]
# inst.update_each_plot(line_data)
# plt.show()


# 	def 
# x=0
# y=0 

# x_s = 0
# y_s = 3

# fig=plt.figure(1)

# a = 1
# ax= fig.add_subplot(3,1,a)


# ax_b = fig.add_subplot(3,1,2)

# ax_dict = {}
# ax_dict[ax] = 1
# ax_dict[ax_b] = 2
# print ax_dict[ax]

# # ax.set_xlim(0,100)
# # ax.set_ylim(0,100)

# # ax_b.set_xlim(0,10)
# # ax_b.set_ylim(0,10)


# line,=ax.plot(np.array([0]),np.array([1]),color='green', label='allll')
# line_b,= ax_b.plot(np.array([0]),np.array([1]), color='red')

# line_s, = ax.plot(np.array([0]),np.array([1]),  color = 'blue')

# line_bs, = ax_b.plot(np.array([0]),np.array([1]),color = 'blue')
# ax.legend(['a','red line'])
# ax.set_title('002057')
# ax_b.set_title('600132')
# plt.pause(1)
# plt.show()

# for i in range(10):
# 	print line.get_xdata()[0]
# 	x = np.concatenate((line.get_xdata(),[i]))
# 	y = np.concatenate((line.get_ydata(),[i]))
# 	x_s = np.concatenate((line_s.get_xdata(),[i]))
# 	y_s = np.concatenate((line_s.get_ydata(),[i*3]))

# 	line.set_data(x,y)
# 	line_b.set_data(x,y)
# 	line_s.set_data(x_s, y_s)
# 	line_bs.set_data(x_s, y_s)


# 	ax.relim()
# 	ax.autoscale_view()
# 	ax_b.relim()
# 	ax_b.autoscale_view()
# 	plt.tight_layout()
# 	plt.pause(1)

# plt.show()

