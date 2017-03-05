################ cell 1
import math
import datetime
import numpy as np
import pandas as pd
from jqdata import *
# 导入多元线性规划需要的工具包
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

from sklearn.svm import SVC
from sklearn import metrics
import datetime as dt
from dateutil import relativedelta
from sklearn.linear_model import LinearRegression
from sklearn import cross_validation
import cPickle as pickle
from six import StringIO


################ cell 2
a=get_all_trade_days() 
ATD_list=['']*len(a)      # 记录这个脚本已经运行的天数
for i in range(0,len(a)):
    ATD_list[i]=a[i].isoformat()



################ cell 3
factors=['pe_ratio', 'turnover_ratio', 'market_cap', 'invesment_profit_to_profit','pb_ratio','eps',
                'inc_return','operation_profit_to_total_revenue','pcf_ratio','paidin_capital',
               'net_profit_margin','gross_profit_margin','operating_expense_to_total_revenue',
               'adjusted_profit_to_profit','operating_profit_to_profit','roe','roa','net_profit_to_total_revenue',
               'ocf_to_revenue','ocf_to_operating_profit','inc_total_revenue_year_on_year','inc_total_revenue_annual',
               'inc_revenue_year_on_year','inc_revenue_annual','inc_operation_profit_year_on_year',
               'inc_operation_profit_annual','inc_net_profit_year_on_year','inc_net_profit_annual',
               'total_owner_equities','total_sheet_owner_equities',
               'goods_sale_and_service_to_revenue'
               ]


################ cell 4
class train_historial_data():
    def __init__(self):
        pass        
    
    
    def determine_if_not_suspend(self,dayStr,stock):
        suspened_info_df = get_price(stock, end_date=dayStr, frequency='daily', fields='paused')
        return suspened_info_df['paused'].sum() == 0

            
    def get_historical_price(self,stock,datestr):
        df = get_price(stock, start_date=datestr, end_date=datestr, frequency='daily', fields=['close'])
         # 如果数据存在，那么返回当天收盘价
        if len(df)>0:
            return df['close'][0]
        # 如果数据不存在，返回NaN
        else:
            return float("nan")
    
    def get_trade_day_shift(self, datestr, daysShift):
        while datestr not in  ATD_list:
            datestr= datetime.datetime.strptime(datestr,'%Y-%m-%d') + datetime.timedelta(days = -1)
            datestr = datestr.date().isoformat()
        dateStr_index = ATD_list.index(datestr)
        shiftDay = ATD_list[dateStr_index+ daysShift]
        #shiftDay= datetime.datetime.strptime(datestr,'%Y-%m-%d')+datetime.timedelta(days = daysShift)
        return shiftDay
        
        
    def get_historical_volume(self,stock, dateStr):
        volume_df = get_price(stock, end_date=dateStr, frequency='daily', fields=['volume'], skip_paused=True, fq='pre', count=60)
        #print volume_df.head()
        Day60_avg = volume_df['volume'].mean()
        day5_avg = volume_df['volume'].iloc[:5].mean()
        ratio = day5_avg/Day60_avg
        return ratio
        
        
    def get_historical_money_flow(self,stock,dateStr):
        money_df = get_money_flow(stock,end_date=dateStr, fields=[ 'net_pct_main'], count=3)
        avg_money_flow = money_df['net_pct_main'].mean()
        return avg_money_flow
        
        
    def get_historical_dataframe(self, feasible_Stocks,factors,lags = 10):
        today_str = '2016-07-01'
        dateStr = self.get_trade_day_shift(today_str,-30)
        
        train_cols = factors
        
        utility_cols= factors+['return', 'volume_ratio', 'net_pct_main']
        
        code_list = [val+'_lag'+str(i) for val in feasible_Stocks for i in range(lags)]
    
        len_rows=len(code_list)
        
        len_cols=len(utility_cols)
    
        table = np.zeros((len_rows,len_cols)) #生成0矩阵
    
        table[:,:]=nan
    
        table_factors=pd.DataFrame(table,columns=utility_cols,index=code_list)
    
        
        for i in feasible_Stocks:
        # 获得前一个交易日的日期（因为当前交易日你是不知道当前收盘价的）
            D = self.get_trade_day_shift(dateStr,-1)
        # 一个循环，对每一个财务季度进行获取因子
            for j in range(0,lags):
                q = query(valuation,balance,cash_flow,income,indicator).filter(indicator.code.in_([i]))
                f_temp = get_fundamentals(q,D)
                row_name= i+'_lag' + str(j)
                
                if len(f_temp)>0 and self.determine_if_not_suspend(D,i):
                    
                    LD = self.get_trade_day_shift(f_temp['pubDate'][0],-1)
                    
                    f_temp=f_temp[train_cols]
                    f_temp.index=[row_name]
                    table_factors.ix[[row_name],train_cols] = f_temp
                #得到本期财报的披露日期向前推一个日期:
                    p1 = self.get_historical_price(i,D)
                    two_weeks_later = self.get_trade_day_shift(D,35) 
                    p2 = self.get_historical_price(i,two_weeks_later)
                # 获得两个日期隔了多少个交易日
                    r = math.log(p2/p1)/10
                    table_factors.ix[[row_name],['return']]= r
                    table_factors.ix[[row_name],['volume_ratio']]= self.get_historical_volume(i,D)
                    table_factors.ix[[row_name],['net_pct_main']]= self.get_historical_money_flow(i,D)

                else:
                    LD=D
                D=LD
        
        #table_factors =table_factors.dropna() # 将所有含有nan项的行(每行代表一只股票)删除
       
        table_factors = table_factors.dropna(how='all')
        table_factors = table_factors.fillna(table_factors.mean())
        
        stock_return_series = table_factors['return']
        write_file('pca_linRegDF.csv', table_factors.to_csv(), append=False)
        table_factors.drop('return', axis=1, inplace=True)


        #print table_factors.head()
        #print stock_return_series.head()
        
        return table_factors,stock_return_series

################ cell 5
rd = read_file('stockCandidates_2')
rd = eval(rd)


################ cell 6
train_historial_data_obj = train_historial_data()
train_historial_data_obj.get_historical_dataframe(rd,factors,10)
