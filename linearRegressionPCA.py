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


def initialize(context):
    set_params()      # 1设置策参数
    set_variables()   # 2设置中间变量
    set_backtest()    # 3设置回测条件
    
def set_params():
    g.tc = 1         # 设置调仓天数
    g.lag= 4          # 用过去多少期的财报回归
    g.non_suspend_days = 20
    g.num_stocks= 20  # 默认值选表现最好的20个股票
    # 自己选取的一些因子
    g.factors=['pe_ratio', 'turnover_ratio', 'market_cap', 'invesment_profit_to_profit','pb_ratio','eps',
                'inc_return','operation_profit_to_total_revenue','pcf_ratio','paidin_capital',
               'net_profit_margin','gross_profit_margin','operating_expense_to_total_revenue',
               'adjusted_profit_to_profit','operating_profit_to_profit','roe','roa','net_profit_to_total_revenue',
               'ocf_to_revenue','ocf_to_operating_profit','inc_total_revenue_year_on_year','inc_total_revenue_annual',
               'inc_revenue_year_on_year','inc_revenue_annual','inc_operation_profit_year_on_year',
               'inc_operation_profit_annual','inc_net_profit_year_on_year','inc_net_profit_annual',
               'total_owner_equities','total_sheet_owner_equities',
               'goods_sale_and_service_to_revenue'
               ]
    g.weight = (float)(1)/5
               
def set_variables():
    g.t = 0                # 记录回测运行的天数
    g.if_trade = False     # 当天是否交易
    a=get_all_trade_days() 
    g.ATD=['']*len(a)      # 记录这个脚本已经运行的天数
   
    for i in range(0,len(a)):
        g.ATD[i]=a[i].isoformat()
        # print a[i]
        # print type(a[i])
        # print g.ATD[i]

#3
#设置回测条件
def set_backtest():
    set_option('use_real_price',True) # 用真实价格交易
    log.set_level('order','error')    # 设置报错等级
    set_benchmark('000300.XSHG')
    
def set_slip_fee(context):
    # 将滑点设置为0
    set_slippage(PriceRelatedSlippage(0.002))
    # 根据不同的时间段设置手续费
    dt=context.current_dt
    log.info(type(context.current_dt))
    
    if dt>datetime.datetime(2013,1, 1):
        set_commission(PerTrade(buy_cost=0.0003, sell_cost=0.0013, min_cost=5)) 
        
    elif dt>datetime.datetime(2011,1, 1):
        set_commission(PerTrade(buy_cost=0.001, sell_cost=0.002, min_cost=5))
            
    elif dt>datetime.datetime(2009,1, 1):
        set_commission(PerTrade(buy_cost=0.002, sell_cost=0.003, min_cost=5))
                
    else:
        set_commission(PerTrade(buy_cost=0.003, sell_cost=0.004, min_cost=5))


def before_trading_start(context):

    if g.t%g.tc==0:
        #每g.tc天，交易一次
        g.if_trade=True 
        # 设置手续费与手续费
        set_slip_fee(context) 
        candidates_stocks =  list(get_all_securities(['stock']).index)
        process_stocks_obj = process_stocks(candidates_stocks)
        # 设置可行股票池：获得当前开盘的沪深300股票池并剔除当前或者计算样本期间停牌的股票
        context.feasible_stocks = process_stocks_obj.get_proper_stocks(context)
        write_file('stockCandidates', str(context.feasible_stocks), append=False)
        
    g.t+=1
    
    
    

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
        while datestr not in  g.ATD:
            datestr= datetime.datetime.strptime(datestr,'%Y-%m-%d') + datetime.timedelta(days = -1)
            datestr = datestr.date().isoformat()
        dateStr_index = g.ATD.index(datestr)
        shiftDay = g.ATD[dateStr_index+ daysShift]
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
        
        
    def get_historical_dataframe(self, feasible_Stocks, context,lags = 10):
        today_str = str(context.current_dt)[0:10]
        dateStr = self.get_trade_day_shift(today_str,-30)
        
        train_cols = g.factors
        
        utility_cols= g.factors+['return', 'volume_ratio', 'net_pct_main']
        
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
        


class get_stock_factor():
    def __init__(self, stockList):
        self.stockList =stockList
        pass
    
    def get_today_complete_dataFrame(self,factors, today,context):
        basic_info_df = self.get_today_factor(factors, today)
        money_volume_df = self.get_yesterday_moneyFlow_volume_ratio(context)
        
        if np.array_equal(money_volume_df.index, basic_info_df.index):
            print 'they are equal'
        else:
            print 'they are not equal'
        
        combined_df = pd.concat([basic_info_df,money_volume_df], axis=1)
        combined_df = combined_df.dropna(how='all')
        combined_df = combined_df.fillna(combined_df.mean())
        return combined_df
    
    def get_today_factor(self, factors,d):
    # 用于查询基本面数据的查询语句
        q = query(valuation,balance,cash_flow,income,indicator).filter(valuation.code.in_(self.stockList))
    # 获得股票的基本面数据，
        df = get_fundamentals(q)
        code=array(df['code'])
        df = df[factors]
        
        df['cap_liability_ratio'] = df['total_owner_equities']/df['total_sheet_owner_equities'] 
        df.drop('total_owner_equities', axis=1, inplace=True)
        df.drop('total_sheet_owner_equities',  axis=1, inplace=True)
        df.index=code
        
        return df
    
    def get_yesterday_moneyFlow_volume_ratio(self, context):
        volume_df = history(60, unit='1d', field='volume', security_list=self.stockList, df=True, skip_paused=False, fq='pre')
        volume_df_avg_60Days= volume_df.mean(axis=0)
        volume_df_avg_5days = volume_df.iloc[-5:].mean(axis=0)
        volume_df_5daysOver60Days = volume_df_avg_5days/volume_df_avg_60Days
        
        delta = relativedelta.relativedelta(days=-1)
        dt = context.current_dt + delta
        money_df = get_money_flow(self.stockList,  end_date=dt, fields=[ 'sec_code', 'net_pct_main'], count=3)
        avg_money_flow = money_df.groupby(['sec_code']).mean()
        combined_df = pd.concat([volume_df_5daysOver60Days,avg_money_flow],axis=1)
        combined_df.columns = ['volume_ratio', 'net_pct_main']
        return combined_df
        
        
        
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
        
class PCA_regression():
    
    def __init__(self,train_X, train_Y, n_pca='mle', C_svr=1.0):
        self.n_pca = n_pca
        self.C_svr = C_svr
        self.train_X = train_X
        self.train_Y = train_Y
        self.mod_demR = PCA(n_components = self.n_pca, svd_solver='full')
        self.linear_reg = LinearRegression()

        pass
    
    def fit_transform_PCA(self):
        pass
        #self.train_X = scale(self.train_X)
        #self.train_X = self.mod_demR.fit_transform(self.train_X)
        
    
    def build_regression(self):
        pass
        #self.fit_transform_PCA()
        # Calculate MSE with only the intercept (no principal components in regression)
        
# 每个单位时间(如果按天回测,则每天调用一次,如果按分钟,则每分钟调用一次)调用一次
def handle_data(context, data):
    #train_historial_data_obj = train_historial_data()
    
    #table_factors,stock_return_series = train_historial_data_obj.get_historical_dataframe(context.feasible_stocks,context)
    #print 'data preprocessing done'

    
    get_stock_factor_obj = get_stock_factor(context.feasible_stocks)
    todayStr=str(context.current_dt)[0:10]
    combined_df = get_stock_factor_obj.get_today_complete_dataFrame(g.factors,todayStr,context)
    
    fileName = 'finalized_model.pkl'
    
    rd = read_file(fileName)
    dd1 = pickle.load(StringIO(rd))
    
    index_df = combined_df.index
    combined_df = preprocess_data(combined_df)
    
    print combined_df.shape
    bucket = dd1.predict(combined_df)
    print type(bucket)
    print len(bucket)
    print index_df
    return_series = pd.Series(bucket, index=index_df)
    print return_series
    return_series.sort(ascending=False,inplace=True)
    print return_series
    context.selected_stocks = list(return_series.index[:5])
    
    update_position(context,data)
   
    

def update_position(context, data):
    def sell_stock():
        for p in context.portfolio.positions:
            if p not in context.selected_stocks:
                o = order_target(p, 0)
                
            
    def buy_stock():
        target_value = g.weight * context.portfolio.portfolio_value
        for s in context.selected_stocks:
            o = order_target_value(s, target_value)
            
    sell_stock()
    buy_stock()
    


def preprocess_data(dataFrame):
    for column in dataFrame.columns:
        dataFrame[column] =  dataFrame[column] - dataFrame[column].mean()
        
    pca_model = PCA(n_components = 6 , svd_solver='full')
    return pca_model.fit_transform(dataFrame)
    
    
    #body=read_file("pca_linRegDF.csv")
    
    #data=pd.read_csv(StringIO(body))
    
        
        
        