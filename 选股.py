# 初始化函数，设定要操作的股票、基准等等
import math
import datetime
import numpy as np
import pandas as pd
import datetime as dt


def initialize(context):
    g.non_suspend_days = 20
    set_benchmark('000300.XSHG')

# 每个单位时间(如果按天回测,则每天调用一次,如果按分钟,则每分钟调用一次)调用一次
def handle_data(context, data):
    pass 

def before_trading_start(context):
    candidates_stocks =  list(get_all_securities(['stock']).index)
    process_stocks_obj = process_stocks(candidates_stocks)
    context.feasible_stocks = process_stocks_obj.get_proper_stocks(context)
    write_file('stockCandidates_2', str(context.feasible_stocks), append=False)
    exit()


class process_stocks():
    def __init__(self, stockList):
        self.stockList = stockList
        pass
    
    def get_proper_stocks(self, context, deltaday = 60):
        
        def remove_unwanted_stocks():
            current_data = get_current_data()
            return [stock for stock in self.stockList 
                if not current_data[stock].is_st and (current_data[stock].name  is None or
                ( '*' not in current_data[stock].name 
                and '退' not in current_data[stock].name)) 
                and  not current_data[stock].paused]

        def fun_delNewShare(filtered_stocks):
            deltaDate = context.current_dt.date() - dt.timedelta(deltaday)
            tmpList = []
            for stock in filtered_stocks:
                if get_security_info(stock).start_date < deltaDate:
                    tmpList.append(stock)
            return tmpList
            
        def find_non_suspend_stocks(days,filtered_stocks):
            suspened_info_df = get_price(list(filtered_stocks), start_date=context.current_dt, end_date=context.current_dt, frequency='daily', fields='paused')['paused'].T
            # 过滤停牌股票 返回dataframe
            unsuspened_index = suspened_info_df.iloc[:,0]<1
            # 得到当日未停牌股票的代码list:
            unsuspened_stocks = suspened_info_df[unsuspened_index].index
            # 进一步，筛选出前days天未曾停牌的股票list:
            feasible_stocks=[]
            
            current_data=get_current_data()
            
            for stock in unsuspened_stocks:
                if sum(attribute_history(stock, days, unit='1d',fields=('paused'),skip_paused=False))[0]==0:
                    feasible_stocks.append(stock)
            return feasible_stocks
            
        unwanted_stocks = remove_unwanted_stocks()
        non_new_stocks = fun_delNewShare(unwanted_stocks)
        non_suspend_stocks = find_non_suspend_stocks(g.non_suspend_days,non_new_stocks)
        return non_suspend_stocks
    




