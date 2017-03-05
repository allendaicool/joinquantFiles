import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

from sklearn.svm import SVC
from sklearn import metrics
import datetime as dt
from dateutil import relativedelta
from sklearn.linear_model import LinearRegression
from sklearn import cross_validation
from sklearn.metrics import mean_squared_error
import pickle


class PCA_regression():
    #n_components = self.n_pca, svd_solver='full'  n_pca=6, C_svr=1.0
    def __init__(self,train_X, train_Y,n_pca=6,C_svr=1.0):
        self.n_pca = n_pca
        self.C_svr = C_svr
        self.train_X = train_X
        self.train_Y = train_Y
        self.mod_demR = PCA(n_components = self.n_pca, svd_solver='full')
        self.linear_reg = LinearRegression()

        pass
    
    def fit_transform_PCA(self):
    	for column in self.train_X.columns:
    		self.train_X[column] = self.train_X[column] - self.train_X[column].mean()
		self.X_train, self.X_test , self.y_train, self.y_test = cross_validation.train_test_split(self.train_X, self.train_Y, test_size=0.05, random_state=1)
    	#self.X_train  = self.X_train.as_matrix().astype(float)
        #self.train_X = scale(self.train_X)
        self.X_train = self.mod_demR.fit_transform(self.X_train)
        self.X_test = self.mod_demR.fit_transform(self.X_test)
    

    def build_regression(self):
        self.fit_transform_PCA()
        self.linear_reg.fit(self.X_train[:,:], self.y_train)

        ################# save model into pkl file
        filename = '/Users/ydai/Desktop/JointQuant/csvFile/finalized_model.pkl'
        pickle.dump(self.linear_reg, open(filename, 'wb'),2)


        ##########################  doing cross validation 
        loaded_model = pickle.load(open(filename, 'rb'))
        result = loaded_model.predict(self.X_test)
        #return mean_squared_error(self.y_test , result)
        n = len(self.X_train)
        kf_10 = cross_validation.KFold(n, n_folds=10, shuffle=True, random_state=1)
        mse = []
        # Calculate MSE with only the intercept (no principal components in regression)
        score = -1*cross_validation.cross_val_score(self.linear_reg, np.ones((n,1)), self.y_train.ravel(), cv=kf_10, scoring='mean_squared_error').mean()
        mse.append(score)
        for i in np.arange(1,32):
        	score = -1*cross_validation.cross_val_score(self.linear_reg, self.X_train[:,:i], self.y_train.ravel(), cv=kf_10, scoring='mean_squared_error').mean()
        	mse.append(score)
        return mse


data = pd.read_csv('/Users/ydai/Desktop/JointQuant/csvFile/pca_linRegDF_10.csv', low_memory=False)

print data.index
print data.columns
data.index = data.ix[:,0]
data.drop(data.columns[0], axis = 1, inplace=True)

target_Y = data['return']
data.drop('return', axis = 1, inplace=True)


PCA_regression_obj = PCA_regression(data,target_Y)

mse = PCA_regression_obj.build_regression()


print mse
print mse.index(min(mse))




