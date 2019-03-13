import math
import pandas as pd
from datetime import datetime
import numpy as np
import QuantLib as ql



class Option:
    def __init__(self, right, s, k, exp_date, div,price, rf, vol):        
        self.k = float(k)
        self.s = float(s)
        self.rf = float(rf)
        self.vol = float(vol)
        self.div = float(div)
        self.day_count = ql.Actual365Fixed()
        self.calendar = ql.UnitedStates()
        t = datetime.today().timetuple()
        #print(exp_date)
        l = []
        for i in t[:-3]:
            l.append(i)
        self.day = l[2]
        self.month = l[1]
        self.year = l[0]
        self.hour = l[3]
        self.min = l[4]
        self.sec = l[5]
        self.micro = 0
        self.calculation_date = ql.Date(self.day,self.month,self.year,self.hour,self.min,self.sec,self.micro)
        exp_date = exp_date.split('/')
        self.month1 = int(exp_date[0])
        self.day1 = int(exp_date[1])
        self.year1 = int('20'+exp_date[2])
        self.hour1, self.minute1, self.sec1, self.micro1 = 16,0,0,0        
        self.expiration_date = ql.Date(self.day1,self.month1,self.year1,self.hour1,self.minute1,self.sec1,self.micro1)        
        self.price = price
        self.right = right
        
        if self.right == 'C':
            self.option_type = ql.Option.Call
        else:
            self.option_type = ql.Option.Put
    def initialize_pricing_engine(self, calculation_datee, expiration_datee):
        self.calculation_date = calculation_datee
        self.expiration_date = expiration_datee
        #create instance and set up the exercise type and option type
        
        ql.Settings.instance().evaluationDate = self.calculation_date
        payoff = ql.PlainVanillaPayoff(self.option_type, self.k)
        
        am_exercise = ql.EuropeanExercise(self.expiration_date)
        self.american_option = ql.VanillaOption(payoff, am_exercise)
        
        #set up the discount curves and the quotes and format the div yields. and start BSM process
        spot_handle = ql.QuoteHandle(ql.SimpleQuote(self.s))
        disc_curve = ql.FlatForward(self.calculation_date, self.rf, self.day_count)
      
        flat_ts = ql.YieldTermStructureHandle(disc_curve) 
        div_disc_curve = ql.FlatForward(self.calculation_date, self.div, self.day_count)
       
        dividend_yield = ql.YieldTermStructureHandle(div_disc_curve)
        flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(self.calculation_date, self.calendar, self.vol,self.day_count))
        self.bsm_process = ql.BlackScholesMertonProcess(spot_handle, dividend_yield, flat_ts, flat_vol_ts)
    
        
    def get_price_binomial(self):
        #price option using Binomial Tree
        steps = 200      
        binomial_engine = ql.BinomialVanillaEngine(self.bsm_process, 'crr', steps)
        self.american_option.setPricingEngine(binomial_engine)
        
        return(self.american_option.NPV())
    
        
    def delta(self):
        delta = self.american_option.delta()
        return delta
        
    def gamma(self):
        gamma = self.american_option.gamma()
        return gamma
    
    def theta(self):
        
        #set calculation date to +1 hour then calculate the price
        self.calculation_date = ql.Date(self.day ,self.month,self.year,self.hour + 1,self.min,self.sec,self.micro)
        self.expiration_date = ql.Date(self.day1 ,self.month1,self.year1,self.hour1 + 1,self.minute1,self.sec1,self.micro1)
        self.initialize_pricing_engine(self.calculation_date, self.expiration_date)
        self.get_price_binomial()
        after_price = self.american_option.NPV()       
        #self calc date to -1 hour then calc the price
        self.calculation_date = ql.Date(self.day ,self.month,self.year,self.hour + -1,self.min,self.sec,self.micro)                
        self.expiration_date = ql.Date(self.day1,self.month1,self.year1,self.hour1,self.minute1,self.sec1,self.micro1)
        self.initialize_pricing_engine(self.calculation_date, self.expiration_date)
        self.get_price_binomial()
        orig_price = self.american_option.NPV()
        #calculate theta by taking the price diff * -1
        theta = (after_price - orig_price ) * (-1)
        self.calculation_date = ql.Date(self.day,self.month,self.year,self.hour,self.min,self.sec,self.micro)
        #print('Theta: 'theta)
        return theta * 24
        
    def get_all(self):
        self.initialize_pricing_engine(self.calculation_date, self.expiration_date)
        self.get_price_binomial()                   
        return self.american_option.NPV()
    
    
    #add vega/rho/ all other greeks
    # Add futures/PnL/Margin <-- Later
    
    #net greeks
        
    
    
#%%

df = pd.DataFrame()
    
#convert FIX message to series then append it
#vol numbers on puts OTM go up quite a bit. almost 10% more when otm by 30$
current_price = '2780' 
vol = .115
put_modifier = 0

df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'C',
                          'E2A',
                          '2740',
                          '100',
                          '901',
                          '13.324',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)

df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'C',
                          'E2A',
                          '2750',
                          '100',
                          '-807',
                          '6.942',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'C',
                          'E2A',
                          '2755',
                          '100',
                          '303',
                          '4.247',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'C',
                          'E2A',
                          '2760',
                          '100',
                          '-1235',
                          '2.476',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'C',
                          'E2A',
                          '2775',
                          '100',
                          '300',
                          '3.7',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)    
    
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'C',
                          'E2A',
                          '2780',
                          '100',
                          '200',
                          '.25',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'C',
                          'E2A',
                          '2785',
                          '100',
                          '400',
                          '.15',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'P',
                          'E2A',
                          '2710',
                          '100',
                          '200',
                          '.3',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
    
    
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'P',
                          'E2A',
                          '2715',
                          '100',
                          '22',
                          '.336',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol+ put_modifier),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'P',
                          'E2A',
                          '2720',
                          '100',
                          '300',
                          '.2',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol+ put_modifier),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'P',
                          'E2A',
                          '2735',
                          '100',
                          '-2',
                          '1.82',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol+ put_modifier),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'P',
                          'E2A',
                          '2740',
                          '100',
                          '300',
                          '4.62',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol+ put_modifier),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)  
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'P',
                          'E2A',
                          '2750',
                          '100',
                          '250',
                          '1.15',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol+ put_modifier),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'P',
                          'E2A',
                          '2760',
                          '100',
                          '50',
                          '6.75',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol+ put_modifier),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'P',
                          'E2A',
                          '2765',
                          '100',
                          '-203',
                          '3.94',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol+ put_modifier),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'P',
                          'E2A',
                          '2770',
                          '100',
                          '-962',
                          '2.51',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol+ put_modifier),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)    
df = df.append(pd.Series(['OPT', 
                          '03/11/19',
                          'P',
                          'E2A',
                          '2775',
                          '100',
                          '-500',
                          '2.47',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol+ put_modifier),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)    
    
df = df.append(pd.Series(['FUT', 
                          'NA',
                          'NA',
                          'ES',
                          'NA',
                          'NA',
                          '-124',
                          '2747.4',
                          '0',
                          'na',
                          'na',
                          'na',
                          '{}'.format(current_price),
                          'na']), ignore_index = True)   
    
'''
df = df.append(pd.Series(['FUT', 
                          'NA',
                          'NA',
                          'ES',
                          'NA',
                          'NA',
                          '-104',
                          '2747.4',
                          '0',
                          'na',
                          'na',
                          'na',
                          '{}'.format(current_price),
                          'na']), ignore_index = True)

df = df.append(pd.Series(['FUT', 
                          'NA',
                          'NA',
                          'ES',
                          'NA',
                          'NA',
                          '100',
                          '2770',
                          '0',
                          'na',
                          'na',
                          'na',
                          '{}'.format(current_price),
                          'na']), ignore_index = True)

df = df.append(pd.Series(['OPT', 
                          '02/22/19',
                          'C',
                          'EW3',
                          '2780',
                          '100',
                          '500',  #position
                          '15',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '02/22/19',
                          'C',
                          'EW3',
                          '2785',
                          '100',
                          '300',
                          '12',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)

df = df.append(pd.Series(['OPT', 
                          '02/22/19',
                          'P',
                          'EW3',
                          '2710',
                          '100',
                          '60',
                          '.15',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol+.05),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)
df = df.append(pd.Series(['OPT', 
                          '02/22/19',
                          'P',
                          'EW3',
                          '2750',
                          '100',
                          '-460',
                          '.2',
                          '0',
                          'now',
                          '1.00',
                          '{}'.format(vol+.01),
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)

df = df.append(pd.Series(['OPT', 
                          '02/22/19',
                          'P',
                          'EW3',
                          '2775',
                          '100',
                          '400', # amt
                          '5',
                          '0',
                          'now',
                          '.025',
                          '{}'.format(vol+.01), #.128 vs .115 got me the price i needed on puts
                          '{}'.format(current_price),
                          '.025']), ignore_index = True)'''

#%%
dictionary = {}
dictionary_futures = {}
def round1(x):
    return int(math.ceil(x/5)) * 5
current_mp = round1(float(current_price))
minus_mp = current_mp
current_mp_value = current_mp
#print('current price: ', current_mp)
interval = 5
index = []

dol_per_pnt = {'ES': 50, 'CL': 1000,'6j':100,'ZB':1000, 'ZN':1000,'GC':100,'NQ':20,
               'E1A': 50,'E2A':50,'E3A':50,'E4A':50, #ES MONDAY OPTIONS
               'E1C':50,'E2C':50, 'E3C':50, 'E4C':50, # ES WEDNESDAY OPTIONS
               'EW1':50,'EW2':50,'EW3':50,'EW4':50,  #ES FRIDAY OPTIONS
               'EW':50     #ES MONTHLY OPTIONS
               
               } 
 

for x in range(5):
    current_mp += interval
    index.append(current_mp)
    minus_mp -= interval
    index.append(minus_mp)
    
del minus_mp, interval
   # print(current_mp, minus_mp)
def create_df_risk(current_mp_value,index):
    
    index.append(current_mp_value)
    index.sort()
    columns_risk = ['Price','Delta', 'Gamma', 'Theta','pnl']
                
    df_risk = pd.DataFrame(index =index, columns = columns_risk)
    df_risk.fillna(float(0), inplace=True)
    df_risk = df_risk[~df_risk.index.duplicated(keep='first')]
    index.sort()
    return df_risk

def create_df_risk_futures(current_mp_value,index):
    
    index.append(current_mp_value)
    index.sort()
    columns_risk = ['delta','pnl']
                
    df_risk = pd.DataFrame(index =index, columns = columns_risk)
    df_risk.fillna(float(0), inplace=True)
    df_risk = df_risk[~df_risk.index.duplicated(keep='first')]
    
    return df_risk

count = 0
count2 = 0
Future_options = 0
for i, _ in df.iterrows():  
    Opt_or_FT = _[0]  
    #print(Opt_or_FT)
    if Opt_or_FT == 'FUT':
        s = float(_[12])
        amt = float(_[6])    
        price_paid = float(_[7])
        symbol = _[3]
        Opt_or_FT = _[0]    
    else:
        s = float(_[12])
        k = float(_[4])
        right = _[2]
        div = 0
        vol = float(_[11])
        rf = float(_[10])
        amt = float(_[6])                 
        exp_date = _[1]
        price_paid = float(_[7])
        symbol = _[3]
        Opt_or_FT = _[0]        
        
    #print(Opt_or_Fut)
    df_risk = create_df_risk(current_mp_value,index)
    futures_df = create_df_risk_futures(current_mp_value, index)
    if Opt_or_FT == 'FUT':
               
        #if symbol == dictionary value for a full point value 50 for ES, 10 for CL

        for i, row in futures_df.iterrows():
            
            #pct_gain_loss = float(i) - price_paid / price_paid            
            futures_df['delta'][i] =  amt
            futures_df['pnl'][i] = (float(i) * dol_per_pnt['{}'.format(symbol)] * amt) - (price_paid *dol_per_pnt['{}'.format(symbol)] * amt)                
            dictionary_futures['futures pnl' + str(count2)] = futures_df            
         
         
        count2+=1
   
    else:
        
        for i,_ in df_risk.iterrows(): 
            
                
            s = float(i)
            opt = Option(s=s, k=k, exp_date=exp_date, rf=rf, vol=vol, right=right, div = div, price = price_paid)            
            df_risk['Price'][i] = opt.get_all()
           
            # GREEKS FOR OPTIONS NEGATIVE AND POSITIVE.
            # REMOVE DOL_PER_PNT FROM CALC IF U WANT THE GREEKS * CONTRACTS
            # REMOVE INT(AMT) IF YOU WANT JUST RAW DELTA. BUT IT GETS ADDED FURTHER DOWN MIGHT NEED TO FIX THAT.
            if right =='C'and amt < 0:
                              
                df_risk['Delta'][i] = round(int(amt) * opt.delta(),2) #* dol_per_pnt['{}'.format(symbol)]
                df_risk['Gamma'][i] = round(int(amt) * opt.gamma(),2) #* dol_per_pnt['{}'.format(symbol)]
                df_risk['Theta'][i] = opt.theta() #* dol_per_pnt['{}'.format(symbol)]
                df_risk['pnl'][i] = round((df_risk['Price'][i]* int(amt)* dol_per_pnt['{}'.format(symbol)]) - (price_paid* int(amt)* dol_per_pnt['{}'.format(symbol)]),2)
               #df_risk['pnl'][i] = np.clip(df_risk['pnl'][i], None, -(price_paid * 50 * int(amt)))
                
                
            if right =='P'and amt < 0:
                df_risk['pnl'][i] = round((df_risk['Price'][i]* int(amt)* dol_per_pnt['{}'.format(symbol)]) - (price_paid* int(amt)* dol_per_pnt['{}'.format(symbol)]))
           
                df_risk['Delta'][i] = round(int(amt) * opt.delta(),2) #* dol_per_pnt['{}'.format(symbol)]
                df_risk['Gamma'][i] = round(int(amt) * opt.gamma(),2) #* dol_per_pnt['{}'.format(symbol)]
                df_risk['Theta'][i] = opt.theta() #* dol_per_pnt['{}'.format(symbol)]
                
            if right == 'C' and amt > 0:
                df_risk['pnl'][i] =  round((df_risk['Price'][i]* int(amt)* dol_per_pnt['{}'.format(symbol)]) - (price_paid* int(amt)* dol_per_pnt['{}'.format(symbol)]),2)
                df_risk['Delta'][i] = round(int(amt) * opt.delta(),2) #* dol_per_pnt['{}'.format(symbol)]
                df_risk['Gamma'][i] = round(int(amt) * opt.gamma(),2) #* dol_per_pnt['{}'.format(symbol)]
                df_risk['Theta'][i] = -opt.theta() #* dol_per_pnt['{}'.format(symbol)]
                
            if right == 'P' and amt > 0:
                df_risk['pnl'][i] = (df_risk['Price'][i]* int(amt)* dol_per_pnt['{}'.format(symbol)]) - (price_paid* int(amt)* dol_per_pnt['{}'.format(symbol)])
                df_risk['Delta'][i] = round(int(amt) * opt.delta(),2) #* dol_per_pnt['{}'.format(symbol)]
                df_risk['Gamma'][i] = round(int(amt) * opt.gamma(),2) #* dol_per_pnt['{}'.format(symbol)]
                df_risk['Theta'][i] = -opt.theta() #* dol_per_pnt['{}'.format(symbol)]
                
                #print(df_risk['pnl'][i])  
            dictionary['price_shock'+ str(count)+ '' + str(right) + '' + str(k)] = df_risk
            
        count +=1
        
    
net_shock = pd.DataFrame()
count = 0
count5 = 0

#net is created from futures in dictionary_futures
try:
    for _ in dictionary_futures:
        
        if count5 == 0:
            net = dictionary_futures[_]['pnl']
            net_fut_delta = dictionary_futures[_]['delta']
            #print(net)
        else:   
            net = net + dictionary_futures[_]['pnl']
            net_fut_delta = net_fut_delta + dictionary_futures[_]['delta']
            
        count5 += 1
       
except Exception as e:
    print('ERROR :', e)
    pass


count = 0
for _ in dictionary:    
    if count == 0:
        net_shock = dictionary[_]
    else:
        net_shock += dictionary[_]
    count+= 1
    
    #NET SHOCK IS RIGHT AS OF HERE FOR ALL OPTIONS--------------ABOVE
print(net_shock)
net_shock_options = net_shock.copy(deep = True)
try:
    net_shock.loc[:,'pnl'] = net_shock.loc[:,'pnl'] + net.loc[:]
    net_shock.loc[:,'Delta'] = net_shock.loc[:,'Delta'] + net_fut_delta.loc[:]
    
except Exception as e:
    print('ERROR :', e)
    pass

for i, row in net_shock.iterrows(): 
    for n in row:                
        row.replace(to_replace = n,value = round(n, 2), inplace=True) 
    
net_shock.sort_index(axis = 0,ascending = True, inplace=True)
del count,count5, count2, s,k,right,vol,rf,exp_date,div,price_paid,symbol

##      NET SHOCK IS ALL OF THE PRICES OF OPTIONS, DELTA, GAMMA, THETA ADDED TOGETHER PER STRIKE. DELTA AND PNL IS ADDED IN FROM FUTURES
##
#print(net_shock)
#%%
   
df_options = pd.DataFrame()
df_options_minusten = pd.DataFrame()
df_options_plusten = pd.DataFrame()


#Change this when you get final format
for i, _ in df.iterrows():          
    Opt_or_FT = _[0] 
    if Opt_or_FT == 'FUT':
        s = float(_[12])
        k = _[4]
        right = _[2]
        vol = _[11]
        rf = _[10]
        amt = float(_[6])
        exp_date = _[1]
        div = _[13]
        price_paid = float(_[7])
        symbol = _[3]
        Opt_or_FT = _[0]        
        #multipler = _[5]
        #commision = _[8]
        
        theo_price = s
        delta = int(amt) 
        theta = 0
        gamma = 0
        series = pd.Series([right,symbol, price_paid,theo_price, s, k, amt, exp_date, theta,delta,gamma, div, Opt_or_FT] )
        df_options = df_options.append(series, ignore_index=True)
        #print(series)
        
        s_plus = s+10
        series_plus = pd.Series([right,symbol, price_paid,theo_price, s_plus, k, amt, exp_date, theta,delta,gamma, div, Opt_or_FT] )
        df_options_plusten = df_options_plusten.append(series_plus, ignore_index=True)
        
        s_minus = s-10
        series_minus = pd.Series([right,symbol, price_paid,theo_price, s_minus, k, amt, exp_date, theta,delta,gamma, div, Opt_or_FT] )
        df_options_minusten = df_options_minusten.append(series_minus, ignore_index=True)
        del series, theta, delta,gamma, s,k,right,vol,rf,exp_date,div,price_paid,symbol, theo_price
    else:
        s = float(_[12])
        #print(_[4])
        k = float(_[4])
        right = _[2]
        vol = float(_[11])
        rf = float(_[10])
        amt = float(_[6])
        exp_date = _[1]
        div = float(_[13])
        price_paid = float(_[7])
        symbol = _[3]
        Opt_or_FT = _[0]        
        #multipler = float(_[5])
        #commision = float(_[8])

        opt = Option(s=s, k=k, exp_date=exp_date, rf=rf, vol=vol, right=right, div = div, price = price_paid)
        theo_price = opt.get_all()
        #greeks * amount of contracts to get greeks per positions
        theta = int(amt) * opt.theta()
       
        delta = int(amt) * opt.delta()
        gamma = int(amt) *opt.gamma()
        #print(amt)
        ##PUT THIS ACROSS THE REST OF THEM
        if amt < 0:
            
            series = pd.Series([right,symbol, price_paid,theo_price, s, k, amt, exp_date, theta,delta,gamma, div,Opt_or_FT] )
        else:   
            
            theta = -theta
           # print(theta)
            series = pd.Series([right,symbol, price_paid,theo_price, s, k, amt, exp_date, theta,delta,gamma, div,Opt_or_FT] )
        df_options = df_options.append(series, ignore_index=True)
        print(df_options)
        del series, theta, s,k,right,vol,rf,exp_date,div,price_paid,symbol
             
   #%%     

fut = df_options.loc[df_options[12] =='FUT']



if fut.empty == True:
    pricing = {'df_options':df_options}
    for i,_ in pricing.items():        
        if amt <0:
            df_options.loc[: ,12] = ( df_options.loc[:,2] - df_options.loc[:, 3]) / df_options.loc[:,2]
            df_options.loc[: ,13] = df_options.loc[:,3] * 50 * df_options.loc[:,6] - df_options.loc[:,2] * 50 * df_options.loc[:,6]
        else:              
            df_options.loc[: ,12] = (df_options.loc[:, 3] - df_options.loc[:,2]) / df_options.loc[:,2]
            df_options.loc[: ,13] = df_options.loc[:,3] * 50 * df_options.loc[:,6] - df_options.loc[:,2] * 50 * df_options.loc[:,6]        
        #Greeks for current portfolio 
    net_theta = pricing['df_options'].loc[:, 8].sum()
    print(net_theta)
    net_gamma = pricing['df_options'].loc[:, 10].sum()
    net_delta = pricing['df_options'].loc[:, 9].sum()
    net_pnl = pricing['df_options'].loc[:, 13].sum()
    net_normal = [net_pnl, net_delta, net_gamma, net_theta]
  
   

   
    pnl = {'normal': net_normal}
    print('Format: Net PnL, Delta, Gamma, Theta, PnL Difference from Current Portfolio')
    print('Current Price: ', pnl['normal'])
    #print('Up 10 handles: ', pnl['plus'])
    #print('Down 10 handles: ', pnl['minus'])
        

else:

    pricing = {'df_options':df_options}  #, 'df_options_plusten':df_options_plusten, 'df_options_minusten': df_options_minusten}
    fut = df_options.loc[df_options[12] =='FUT']      
    pricing['df_options'] = df_options.drop(fut.index)
   
    

    pricing['df_options'].loc[: ,12] = (pricing['df_options'].loc[:, 3] - pricing['df_options'].loc[:,2]) / pricing['df_options'].loc[:,2]
    pricing['df_options'].loc[: ,13] = pricing['df_options'].loc[:,3] * 50 * pricing['df_options'].loc[:,6] - pricing['df_options'].loc[:,2] * 50 * pricing['df_options'].loc[:,6]

    # $ PnL
    dol_per_pnt = {'ES': 50, 'CL': 10}
 
    
    for i, _ in fut.iterrows():
        try:
            var = str(fut[1][i])            
            fut.loc[i,13] = (fut.loc[i,4] - fut.loc[i,2]) * dol_per_pnt["{}".format(var)] * fut.loc[i,6]       
        except Exception as e:
            print('ERROR: ',e)

 
    es_margin = 6000 
    fut.loc[:,12] = fut.loc[:,13] / fut.loc[:,6] /es_margin
 
    futures = {'df_options':fut}
   
    
    for item in pricing:    
        var = item            
        pricing[item] = pricing[item].append(futures['{}'.format(var)], ignore_index = True)
        
   
    #print(pricing['df_options'])
    #Greeks for current portfolio 
    print('HEY',pricing['df_options'].loc[:, 8])
    net_theta = pricing['df_options'].loc[:, 8].sum()
    net_gamma = pricing['df_options'].loc[:, 10].sum()
    net_delta = pricing['df_options'].loc[:, 9].sum()
    net_pnl = pricing['df_options'].loc[:, 13].sum()
    net_normal = [net_pnl, net_delta, net_gamma, net_theta]
    #print('Current Price. Format: Net PnL, Delta, Gamma, Theta', net_normal)
    
    
    pnl = {'normal': net_normal}
    print('Format: Net PnL, Delta, Gamma, Theta')
    print('Current Price: ', pnl['normal'])
    #print('Up 10 handles: ', pnl['plus'])
    #print('Down 10 handles: ', pnl['minus'])        
    
       
       
columns = {0:'call_put',1:'ticker',2:'paid_p',3:'curr_p',4:'mkt_p',5:'strike',6:'amt',7:'expiry',8:'theta',9:'delta',10:'gamma',11:'div',12:'pct_gain',13:'dol_gain'}

for item in pricing:    
    pricing[item].rename(columns,inplace=True, axis = 1)
    
      
#%%
       


new_df = df.loc[:,[3,4,6,7]]


def create_df_risk_futures(current_mp_value,index):
    
    index.append(current_mp_value)
    columns_risk = ['above','below']
                
    df_risk = pd.DataFrame(index =index, columns = columns_risk)
    df_risk.fillna(float(0), inplace=True)
    df_risk = df_risk[~df_risk.index.duplicated(keep='first')]
    index.sort()
    return df_risk  

def create_df_risk_options(current_mp_value,index):
    
    index.append(current_mp_value)
    columns_risk = ['position','above','below']
                
    df_risk = pd.DataFrame(index =index, columns = columns_risk)
    df_risk.fillna(float(0), inplace=True)
    df_risk = df_risk[~df_risk.index.duplicated(keep='first')]
    index.sort()
    return df_risk  
#%%


print(index)
df_position = create_df_risk_futures(current_mp_value, index)
df_position.reset_index(inplace=True)
#%%


futures_positions = new_df.loc[new_df[3]=='ES']
#%%

futures_positions.loc[0,6] = 100
#%%
var2 = 0
for i, row in futures_positions.iterrows(): 
    var = int(futures_positions.loc[i,6])    
    index_comp = int(futures_positions.loc[i,7])
    var2 += var
    for x in range(len(df_position)):                   
        if df_position.loc[x,'index'] == index_comp:
            df_position.loc[:,['above','below']] = var2
            #print(df_position.loc[:,'above'])


#%%
total_futures = futures_positions.loc[:,6].astype(int).sum()


#%%
options_df = df.loc[:,[0,3,4,6,7]]
options_positions = options_df.loc[options_df[0]=='OPT']

#%% 
options_index = create_df_risk_options(current_mp_value, index)
options_index.reset_index(inplace=True)
#%%





#%%

for i, row in options_positions.iterrows(): 
    var = int(options_positions.loc[i,6])    
    index_comp = int(options_positions.loc[i,4])
    #var2 += var
    for x in range(len(df_position)):                   
        if options_index.loc[x,'index'] == index_comp:
            options_index.loc[x,['above','below']] = total_futures + np.sum()
























       