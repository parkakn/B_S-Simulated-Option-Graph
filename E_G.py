# %%
# Import all packages used in this program 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from pandas_datareader import data
from yahoo_fin import options
import datetime
from datetime import timedelta
import math
from scipy import stats
from matplotlib.animation import FuncAnimation
import itertools

# %%


class EuropeanCall():

    def d1(self, asset_price, strike_price, risk_free_rate, volatility, dt):
        return (np.log((asset_price/strike_price)) + (risk_free_rate + math.pow(volatility,2)/2)*dt)/(volatility*np.sqrt(dt))

    def d2(self, d1, volatility, dt):
        return d1 - (volatility*math.sqrt(dt))

    def price(self, asset_price, d1, strike_price, d2, risk_free_rate, dt):
        # Calculate NormalCDF for d1 & d2
        n1 = stats.norm.cdf(d1)
        n2 = stats.norm.cdf(d2)
        # Calculate call option price
        return asset_price*n1 - strike_price*(math.exp(-(risk_free_rate*dt)))*n2

    def delta(self, d1):
        return stats.norm.cdf(d1)

    def exercise_prob(self):
        return 1 - stats.norm.cdf(((self.strike_price - self.asset_price) - (self.drift*self.asset_price*self.dt))/((self.volatility*self.asset_price)*(self.dt**.5)))


    def __init__(self, asset_price, strike_price, volatility, expiration_date, risk_free_rate, drift):
        self.asset_price = asset_price
        self.strike_price = strike_price
        self.volatility = volatility
        self.expiration_date = expiration_date
        self.risk_free_rate = risk_free_rate
        self.drift = drift
        # Calculate delta t
        dt = np.busday_count(datetime.date.today(), expiration_date) / 252
        # Calculate d1
        d1 = self.d1(asset_price, strike_price, risk_free_rate, volatility, dt)
        # Calculate d2
        d2 = self.d2(d1, volatility, dt)
        self.dt = dt
        self.price = self.price(asset_price, d1, strike_price, d2, risk_free_rate, dt)
        self.delta = self.delta(d1)

# %%
# Graph
#  
class LiveOptionsGraph:
    def __init__(self, european_option, axs):
        self.index = 0
        self.asset_price = european_option.asset_price
        self.strike_price = european_option.strike_price
        self.volatility = european_option.volatility
        self.expiration_date = european_option.expiration_date
        self.risk_free_rate = european_option.risk_free_rate
        self.drift = european_option.drift
        self.index_set = []
        self.option_prices = []
        self.asset_prices = [european_option.asset_price]
        self.deltas = []
        self.axs = axs
        self.axs[0].set_xlim(0, self.index+1)
        self.axs[1].set_xlim(0, self.index+1)
        self.axs[2].set_xlim(0,self.index+1)
        self.axs[2].axhline(self.strike_price, label='Call Strike Price', c='gray')
        
        self.axs[0].legend(loc='upper right')
        self.axs[1].legend(loc='upper right')
        self.axs[2].legend(loc='upper right')
    # Can be modified by appending new realtime data rather than randomly generated data
    def __call__(self, z):
        # Portfolio tick
        # ASSUMING DRIFT/TIMESTEPS/VOLATILITY ARE CONSTANT WE CAN GENERATE A DRAW FROM THE NORMAL DISTRIBUTION TO SIMULATE A assetS CHANGE IN PRICE OVER TIME
        # We want to graph delta and the underlying asset_price as well
        # MODEL IS INHERINTLY WRONG TO ASSUME EVERYTHING IS CONSTANT BUT CAN DRAW ON LIVE UPDATES OVER TIME TO MAKE IT WORK
        t = np.busday_count(datetime.date.today(), self.expiration_date) / 252  # Calculate dt so we can draw from a normal distribution to model the asset price
        eo = EuropeanCall(self.asset_prices[self.index] + np.random.normal(0, t**(1/2)), self.strike_price, self.volatility, self.expiration_date, self.risk_free_rate,self.drift)
        self.option_prices.append(eo.price)
        self.deltas.append(eo.delta)
        
        self.index_set.append(self.index)

        self.line1, = axs[0].plot(self.index_set, self.option_prices,label='Black-Scholes Option Price', c='b')
        self.line2, = axs[1].plot(self.index_set,self.deltas, label='Delta', c='gray')
        print(self.index_set, self.option_prices,self.asset_prices)

        if self.strike_price <= self.asset_prices[self.index]:
            self.line3,=self.axs[2].plot(self.index_set, self.asset_prices, label='Asset Price', c='g')
        else:
            self.line3,=self.axs[2].plot(self.index_set, self.asset_prices, label='Asset Price', c='r')
        self.index = self.index + 1
        self.asset_prices.append(eo.asset_price)
        self.axs[0].set_xlim(0,self.index+1)
        self.axs[1].set_xlim(0,self.index+1)
        self.axs[2].set_xlim(0,self.index+1)
        self.expiration_date = self.expiration_date - timedelta(days=1)  # Helps display time decay
        return self.line1,self.line2,self.line3
    
        
#%%
european_option = EuropeanCall(64.5, 64.6, 0.4, datetime.date(2023, 2, 17), 0.1, 0.2)

plt.style.use('dark_background')
fig, axs = plt.subplots(3)
a = LiveOptionsGraph(european_option,axs)
ani = FuncAnimation(plt.gcf(), a, frames=100, interval=100, blit=True)
plt.tight_layout()
plt.show()
