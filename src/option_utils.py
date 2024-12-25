'''
Collection of functions to calculate pricing.
'''

import math

'''
    Calculate the Black-Scholes option price for a call or put

    Parameters:
    S (float): Current stock price
    K (float): Strike price
    T (float): Time to expiration (in years)
    r (float): Risk-free interest rate (annualized)
    sigma (float): Volatility of the stock (annualized)
    option_type (str): "call" for call option, "put" for put option

    Returns:
    float: Option price
'''
def compute_black_scholes(S, K, T, r, sigma, option_type="call"):
    if not K:
        return
    
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == "call":
        # Call option price
        return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    elif option_type == "put":
        # Put option price
        return K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")
    

'''
    Calculate annualized volaility given a stock dataframe. Assumes that
    'Close' column exists. Dataframe will be modified to add 'daily_return'
    field.

    Returns:
    float: annualized volatility in decimal form
'''
def calculate_vol(df):
    df['daily_return'] = df['Close'].pct_change()
    daily_vol = df['daily_return'].std()
    annualized_vol = daily_vol * math.sqrt(252)
    return annualized_vol

def norm_cdf(x):
    # Error function approximation for standard normal CDF
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))