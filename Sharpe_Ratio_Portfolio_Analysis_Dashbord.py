# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 16:44:33 2025

@author: ggpal
"""

#http://127.0.0.1:8054/

# -- Import Libraries
import plotly 
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from plotly.offline import plot
from plotly.subplots import make_subplots
import dash
from dash import html, dcc, dash_table
import seaborn as sns
import matplotlib.pyplot as plt
from dash.dependencies import Input, Output
import numpy as np
import requests
import time
from datetime import date
from stockdex import Ticker
import warnings
warnings.filterwarnings("ignore")


# === Mask dataframe based on dates
def process_dates(df, start=date(2025, 9, 8), end=date(2025, 10, 10)):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    mask = (df["timestamp"].dt.date >= inv_start) & (df["timestamp"].dt.date <= inv_end)
    return df[mask]

# === Find Volatility of Portfolios
def find_volatility(df_prices, df_weights):
    """"Create a function to find the portfolio varaince of any given portfolio"""
    # Pivot df
    price_df = df_prices.pivot(index="timestamp", columns="Symbol", values="pct_change")
    #cov matrix
    cov_mat = price_df.cov()*250
    
    # Set symbol as index for reindexing
    weights = df_weights.set_index("Symbol")
    weights = weights.reindex(price_df.columns).fillna(0)
    weights_array = weights["frac_inv"].values
    
    # variance
    v = np.dot(weights_array.T, np.dot(cov_mat, weights_array))
    # std
    return (np.sqrt(v) * 100).round(2)


# Calculate Support and Resistance Levels
def find_mean_support_resistance(df, window=20, std_factor=2):
    rolling_mean = df['close'].rolling(window=window).mean()
    rolling_std = df['close'].rolling(window=window).std()
    support = rolling_mean - (std_factor * rolling_std)
    resistance = rolling_mean + (std_factor * rolling_std)
    return rolling_mean, support, resistance

    



# -- Load in Portfolio Information
# -- Portfolio 1 will represent our portfolio made through graph theory
# -- Portfolio 2 will represent our portfolio made through sector performances(GICS)
portfolio_1 = pd.read_csv(r"C:\Users\ggpal\Downloads\graph_portfolio.xls")
p1_amt = portfolio_1[["Symbol", "n_shares"]]

# -- Create display df for presentation
portfolio_1_display = portfolio_1.copy()
portfolio_1_display.columns = ["Symbol", "Monthly Sharpe Ratio(9/2024-9/2025)", 
                               "Annualized Sharpe Ratio(9/2024-9/2025)", "Group",
                               "Close(9/8/2025)", "Instrument Type", "Portfolio Weight(%)",
                               "Shares Invested", "Amount Invested"
                               ]
portfolio_1_display = portfolio_1_display.drop(columns = ["Group", "Close(9/8/2025)", "Amount Invested"])

# Change Formatting for numeric cells
for col in portfolio_1_display.columns:
    if col == "Portfolio Weight(%)":
        portfolio_1_display[col] = portfolio_1_display[col]*100
    if portfolio_1_display[col].dtype == float:
        portfolio_1_display[col] = portfolio_1_display[col].round(2)
portfolio_1_display = portfolio_1_display.sort_values(by = "Portfolio Weight(%)", ascending = False)
 
# Same as above
portfolio_2 = pd.read_csv(r"C:\Users\ggpal\Downloads\sector_portolio.xls")
p2_amt = portfolio_2[["Symbol", "n_shares"]]


portfolio_2_display = portfolio_2.copy()
portfolio_2_display.columns = ["Symbol", "GICS", "Monthly Sharpe Ratio(9/2024-9/2025)", 
                               "Annualized Sharpe Ratio(9/2024-9/2025)",
                               "Close(9/8/2025)", "Portfolio Weight(%)",
                               "Shares Invested", "Amount Invested"
                               ]
portfolio_2_display = portfolio_2_display.drop(columns = ["Close(9/8/2025)", "Amount Invested"])
# Change Formatting for numeric cells
for col in portfolio_2_display.columns:
    if col == "Portfolio Weight(%)":
        portfolio_2_display[col] = portfolio_2_display[col]*100
    if portfolio_2_display[col].dtype == float:
        portfolio_2_display[col] = portfolio_2_display[col].round(2)
portfolio_2_display = portfolio_2_display.sort_values(by = "Portfolio Weight(%)", ascending = False)



# -- Scraping historical data from stockdex
p1_tickers = portfolio_1.Symbol.tolist()
p2_tickers = portfolio_2.Symbol.tolist()
# Get data for investment time
inv_start = date(2025, 9, 8)
inv_end = date(2025, 10, 10)

#p1_prices = pd.DataFrame()
#start = time.time()
#print("Loading...")

# Columns returned by .yahoo_api_price: timestamp, volume, close, open, high, low, currency, timezone, exchangeTimezoneName, exchangeName, instrumentType
#for ticker in p1_tickers: 
#    temp_tick = Ticker(ticker)
#    security_df = temp_tick.yahoo_api_price(range='1y', dataGranularity='1d')
#    security_df = security_df[["timestamp", "low", "high", "open", "close", "instrumentType"]]
#    
#    mask = (security_df["timestamp"].dt.date >= inv_start) & (security_df["timestamp"].dt.date <= inv_end)
#    filtered_df = security_df[mask]
    
    # Use .loc[] to avoid SettingWithCopyWarning
#    filtered_df.loc[:, "Symbol"] = ticker
    
                                
#    p1_prices = pd.concat([p1_prices, filtered_df])
p1_PRICES_ALL = pd.read_csv(r"C:\Users\ggpal\Downloads\all_prices_port1.xls")
p1_prices = process_dates(p1_PRICES_ALL)

                                        
p2_PRICES_ALL = pd.read_csv(r"C:\Users\ggpal\Downloads\all_prices_port2.xls")
p2_prices = process_dates(p2_PRICES_ALL)



# -- How much did each portfolio earn?
# -- port 1
portfolio_1_amt_earned = pd.merge(p1_amt,p1_prices[['Symbol', 'timestamp', 'close']],
                                  on = "Symbol", how = "right")
portfolio_1_amt_earned['amt'] = portfolio_1_amt_earned['n_shares']*portfolio_1_amt_earned['close']
# Find total earned
portfolio_1_amt_earned_total = portfolio_1_amt_earned.groupby('Symbol').apply(
    lambda x: (x['amt'].iloc[-1] - x['amt'].iloc[0])
).reset_index(name='amt_earned')

portfolio_1_amt_earned_total.sort_values(by = "amt_earned", ascending = False)

# -- Get starting values
starting_value_p1 = portfolio_1_amt_earned.groupby('Symbol').apply(
    lambda x: (x['amt'].iloc[0])
).reset_index(name='Total($)').round(2)

# -- Append Inmportant Info to p1_display
portfolio_1_display = portfolio_1_display.merge(starting_value_p1, on = 'Symbol', how='left')
starting_value_p1_total = starting_value_p1["Total($)"].sum().round(2)


# -- Print info
amt_earned_string_port1 = f"Portfolio 1 Earned ${portfolio_1_amt_earned_total['amt_earned'].sum().round(2)}"
investment_info_port1 = f"Portfolio 1 Grew From ${starting_value_p1_total:.2f} --> ${portfolio_1_amt_earned_total['amt_earned'].sum() + starting_value_p1_total:.2f}"


# -- port 2
portfolio_2_amt_earned = pd.merge(p2_amt,p2_prices[['Symbol', 'timestamp', 'close']],
                                  on = "Symbol", how = "right")
portfolio_2_amt_earned['amt'] = portfolio_2_amt_earned['n_shares']*portfolio_2_amt_earned['close']
# Find total earned
portfolio_2_amt_earned_total = portfolio_2_amt_earned.groupby('Symbol').apply(
    lambda x: (x['amt'].iloc[-1] - x['amt'].iloc[0])
).reset_index(name='amt_earned')

portfolio_2_amt_earned_total.sort_values(by = "amt_earned", ascending = False)

# -- Get starting values
starting_value_p2 = portfolio_2_amt_earned.groupby('Symbol').apply(
    lambda x: (x['amt'].iloc[0])
).reset_index(name='Total($)').round(2)

# -- Append Inmportant Info to p1_display
portfolio_2_display = portfolio_2_display.merge(starting_value_p2, on = 'Symbol', how='left')
starting_value_p2_total = starting_value_p2["Total($)"].sum().round(2)


# -- Print info
amt_earned_string_port2 = f"Portfolio 2 Earned ${portfolio_2_amt_earned_total['amt_earned'].sum().round(2)}"
investment_info_port2 = f"Portfolio 2 Grew From ${starting_value_p2_total:.2f} --> ${portfolio_2_amt_earned_total['amt_earned'].sum() + starting_value_p2_total:.2f}"



# ============== Find Portfolio Volatility
# --p1 first
p1_df_prices = p1_prices[["timestamp", 'Symbol', 'close']]
p1_df_prices["pct_change"] = p1_df_prices.groupby("Symbol")['close'].pct_change()

p1_df_weights = portfolio_1[["Symbol", "frac_inv"]]
#print(find_volatility(p1_df_prices, p1_df_weights))
vol_string_port1 = f"Portfolio 1 Volatility(STD) = {find_volatility(p1_df_prices, p1_df_weights)}%"


p2_df_prices = p2_prices[["timestamp", 'Symbol', 'close']]
p2_df_prices["pct_change"] = p2_df_prices.groupby("Symbol")['close'].pct_change()

p2_df_weights = portfolio_2[["Symbol", "frac_inv"]]
#print(find_volatility(p2_df_prices, p2_df_weights))
vol_string_port2 = f"Portfolio 2 Volatility(STD) = {find_volatility(p2_df_prices, p2_df_weights)}%"



# -- Display page portfolio 1 suplot
colors = [
    'gold', 'mediumturquoise', 'darkorange', 'lightgreen', 
    'lightblue', 'tomato', 'plum', 'khaki', 'limegreen', 'pink',
    'coral', 'orchid', 'skyblue', 'salmon', 'slateblue',
    'springgreen', 'peachpuff', 'powderblue', 'lavender', 'seagreen',
    'crimson', 'steelblue', 'moccasin', 'turquoise', 'indigo'
]

fig = make_subplots(
    rows=1, cols=2,
    specs=[[{"type": "domain"}, {"type": "xy"}]],  # pie needs domain
    subplot_titles=["Portfolio Distribution", "Profit(Percent Change%)"]
)

# Pie chart
fig.add_trace(
    go.Pie(
        labels=portfolio_1_display.Symbol,
        values=portfolio_1_display["Total($)"],
        textinfo='label+percent',
        hole=0.3,
        name="Initial Investments($)",
        marker=dict(
            colors=colors[:len(portfolio_1_display)],  # match # of stocks
            line=dict(color='#000000', width=2)        # black border
        )
    ),
    row=1, col=1
)


pct_changes_p1 = p1_prices.groupby('Symbol').apply(
    lambda x: (((x['close'].iloc[-1] - x['close'].iloc[0]) / x['close'].iloc[0])*100).round(2)
).reset_index(name='pct_change')

# Bar 
fig.add_trace(
    go.Bar(
        x=pct_changes_p1.Symbol,
        y=pct_changes_p1["pct_change"],
        text=pct_changes_p1["pct_change"],
        name="Percent Change(%)",
        marker=dict(
            color='mediumturquoise',
            line=dict(color='black', width=1.5)
        ),
    ),
    row=1, col=2
)


fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True, row=1, col=2)
fig.update_yaxes(title_text = "(%)Change",showline=True, linewidth=1, linecolor='black', mirror=True, gridcolor='lightgray', row=1, col=2)

fig.add_annotation(
    text=f"<b>{amt_earned_string_port1}<br>{investment_info_port1}<br>{vol_string_port1}</b>",
    xref="paper", yref="paper",
    x=0.5, y=-0.28,  # add more separation (previously -0.2)
    showarrow=False,
    font=dict(size=17, color="black"),
    align="center"
)

fig.update_layout(
    title_text="Stock Initial Prices and Growth(Graph Portfolio(1))",
    showlegend=False,
    width=1300,
    height=650,
    margin=dict(t=80, b=150, l=80, r=80)
)


# -- Display plot for second portfolio
fig_2 = make_subplots(
    rows=1, cols=2,
    specs=[[{"type": "domain"}, {"type": "xy"}]],  # pie needs domain
    subplot_titles=["Portfolio Distribution", "Profit(Percent Change%)"]
)

# Pie chart
fig_2.add_trace(
    go.Pie(
        labels=portfolio_2_display.Symbol,
        values=portfolio_2_display["Total($)"],
        textinfo='label+percent',
        hole=0.3,
        name="Initial Investments($)",
        marker=dict(
            colors=colors[:len(portfolio_2_display)],  # match # of stocks
            line=dict(color='#000000', width=2)        # black border
        )
    ),
    row=1, col=1
)


pct_changes_p2 = p2_prices.groupby('Symbol').apply(
    lambda x: (((x['close'].iloc[-1] - x['close'].iloc[0]) / x['close'].iloc[0])*100).round(2)
).reset_index(name='pct_change')

# Bar 
fig_2.add_trace(
    go.Bar(
        x=pct_changes_p2.Symbol,
        y=pct_changes_p2["pct_change"],
        text=pct_changes_p2["pct_change"],
        name="Percent Change(%)",
        marker=dict(
            color='aquamarine',
            line=dict(color='black', width=1.5)
        ),
    ),
    row=1, col=2
)


fig_2.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True, row=1, col=2)
fig_2.update_yaxes(title_text = "(%)Change", showline=True, linewidth=1, linecolor='black', mirror=True, gridcolor='lightgray', row=1, col=2)

fig_2.add_annotation(
    text=f"<b>{amt_earned_string_port2}<br>{investment_info_port2}<br>{vol_string_port2}</b>",
    xref="paper", yref="paper",
    x=0.5, y=-0.28,  # add more separation (previously -0.2)
    showarrow=False,
    font=dict(size=17, color="black"),
    align="center"
)


fig_2.update_layout(
    title_text="Stock Initial Prices and Growth(GICS Portfolio(2))",
    showlegend=False,
    width=1300,
    height=600,
    margin=dict(t=80, b=150, l=80, r=80)  
)


# -- App pages


# -- App Layout
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url'),

    # --- Navigation Bar ---
    html.Div(
        children=[
            dcc.Link("🏠 Home", href='/', className='nav-link'),
            dcc.Link("💰 Portfolio 1", href='/port1', className='nav-link'),
            dcc.Link("💰 Portfolio 2", href='/port2', className='nav-link'),
        ],
        style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'gap': '30px',
            'padding': '15px 0',
            'backgroundColor': '#f8f9fa',
            'borderBottom': '2px solid #e0e0e0',
        }
    ),

    html.Hr(style={'border': 'none', 'height': '1px', 'backgroundColor': '#ddd'}),
    html.Div(id="page-content")
])



home_page = html.Div(
    style={"margin": "40px", "font-family": "Arial, sans-serif"},
    children=[
        # Title
        # Title
        html.H1(
            "📊 Portfolio Comparison Dashboard",
            style={
                "textAlign": "center",
                "marginBottom": "15px",
                "fontWeight": "bold",
                "fontSize": "38px",
                "color": "#1f77b4",
                "textShadow": "1px 1px 2px #ddd",
                "letterSpacing": "0.5px",
            },
        ),
        
        # Description
        html.Div(
            [
                html.P(
                    """
                    This dashboard compares two portfolio strategies:
                    """,
                    style={
                        "textAlign": "center",
                        "fontSize": "18px",
                        "color": "#444",
                        "marginBottom": "5px",
                    },
                ),
                html.Ul(
                    [
                        html.Li("Graph Theory: Grouping similar stocks via clustering, selecting one representative per cluster."),
                        html.Li("Sector-based: Grouping by GICS/ETF sector, choosing the highest Sharpe ratio per group."),
                    ],
                    style={
                        "textAlign": "center",
                        "maxWidth": "850px",
                        "margin": "auto",
                        "lineHeight": "1.6",
                        "color": "#333",
                        "fontSize": "16px",
                    },
                ),
                html.P(
                    """
                    The goal is to visualize diversification, risk, and performance differences 
                    between these approaches. Click the links above to see more detailed figures
                    about these portfolios.
                    """,
                    style={
                        "textAlign": "center",
                        "fontStyle": "italic",
                        "color": "#555",
                        "marginTop": "15px",
                    },
                ),
                html.P(
                    "📅 Investment Period: September 8th – October 10th, 2025",
                    style={
                        "textAlign": "center",
                        "fontWeight": "600",
                        "color": "#2a9d8f",
                        "marginTop": "10px",
                        "fontSize": "15px",
                    },
                ),
            ]
        ),


        html.Br(),

        # Portfolio 1
        html.Div([
            html.H2("Portfolio 1: Graph Theory-Based Portfolio", style={"marginTop": "30px"}),
        
            dash_table.DataTable(
                data=portfolio_1_display.to_dict("records"),
                columns=[{"name": i, "id": i} for i in portfolio_1_display.columns],
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "padding": "8px"},
                style_header={"backgroundColor": "#f2f2f2", "fontWeight": "bold"},
                page_size=10
            ),
        
            dcc.Graph(
                figure=fig,  
                style={"marginTop": "20px"}
            )
        ]),

        html.Br(),

        # Portfolio 2
        html.Div([
            html.H2("Portfolio 2: Sector (GICS)-Based Portfolio", style={"marginTop": "30px"}),
        
            dash_table.DataTable(
                data=portfolio_2_display.to_dict("records"),
                columns=[{"name": i, "id": i} for i in portfolio_2_display.columns],
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "padding": "8px"},
                style_header={"backgroundColor": "#f2f2f2", "fontWeight": "bold"},
                page_size=10
            ),
        
            dcc.Graph(
                figure=fig_2,  
                style={"marginTop": "20px"}
            )
        ])
        
    ]
)
    
    
    
# ==== Create function to create main portfolio analysis plot
def portfolio_main_plot(df):
    # Line chart with automatic color grouping (like hue)
    fig_line = px.line(
        df,
        x='timestamp',
        y=df['pct_change']*100,
        color='Symbol',
        markers=True,
        title="Daily % Change Over Time"
    )
    
    # Box plot (same automatic color mapping)
    fig_box = px.box(
        df,
        x='Symbol',
        y=df['pct_change']*100,
        color='Symbol',
       # boxmean='sd',
        title="Distribution of Daily % Changes (Boxplot)"
    )
    fig_box.for_each_trace(lambda t: t.update(showlegend=False))  # hide legend
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=False, vertical_spacing=0.12,
                        subplot_titles=("Daily % Change Over Time", "Distribution of Daily % Changes"))
    
    # Add traces from fig_line
    for trace in fig_line.data:
        fig.add_trace(trace, row=1, col=1)
    fig.add_hline(y=0, line_color="black", line_width=2, line_dash="dash", row=1, col=1)

    
    # Add traces from fig_box
    for trace in fig_box.data:
        fig.add_trace(trace, row=2, col=1)
    fig.add_hline(y=0, line_color="black", line_width=2, line_dash="dash", row=2, col=1)
    
    # Final layout
    fig.update_layout(
        height=900,
        title_text="Stock Daily Percent Changes: Trend and Distribution",
        showlegend=True,
        template="plotly_white"
    )
    
    fig.update_yaxes(title_text="% Change (Daily)", row=1, col=1)
    fig.update_yaxes(title_text="% Change Distribution", row=2, col=1)
    return fig
    

# ===== Create function to present individual stocks
def stock_vis(df, ticker, portfolio_df):
   # Training and investment periods
    train_start = '2024-09-09'
    train_end   = '2025-09-07'
    inv_start   = '2025-09-08'
    inv_end     = '2025-10-10'
   
   

    # 1 filter
    ticker_df = df.query('Symbol == @ticker')
    # Create figure
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,row_heights=[0.35, 0.65])
    #(security_df["timestamp"].dt.date >= inv_start) & (security_df["timestamp"].dt.date <= inv_end)
    ticker_df_date_filtered = ticker_df[(ticker_df['timestamp'] >= inv_start)]

    fig.add_trace(
        go.Candlestick(
            x=ticker_df_date_filtered['timestamp'],
            open=ticker_df_date_filtered['open'],
            high=ticker_df_date_filtered['high'],
            low=ticker_df_date_filtered['low'],
            close=ticker_df_date_filtered['close'],
            name="GDXJ"
        ),
        row=1, col=1
    )
    
    # -- Find rolling stats
    rolling_mean, support, resistance = find_mean_support_resistance(ticker_df)
    ticker_df['rolling_mean'] = rolling_mean
    ticker_df['support'] = support
    ticker_df['resistance'] = resistance    
    
    train_df = ticker_df[(ticker_df['timestamp'] >= train_start) & (ticker_df['timestamp'] <= train_end)]
    inv_df = ticker_df[(ticker_df['timestamp'] >= inv_start)]


    # Identify breakouts
    breakout_above = ticker_df[ticker_df['close'] > ticker_df['resistance']]
    breakout_below = ticker_df[ticker_df['close'] < ticker_df['support']]


    fig.add_trace(go.Scatter(
        x=train_df['timestamp'], y=train_df['close'],
        mode='lines', name='Close (Training)',
        line=dict(color='royalblue', width=5)
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=inv_df['timestamp'], y=inv_df['close'],
        mode='lines', name='Close (Investment)',
        line=dict(color='firebrick', width=5)
    ), row=2, col=1)

    # Rolling average (20-day)
    fig.add_trace(go.Scatter(
        x=ticker_df['timestamp'], y=ticker_df['rolling_mean'],
        mode='lines', name='20D Rolling Avg',
        line=dict(color='black', width=2, dash='dash')
    ), row=2, col=1)

    # Support
    fig.add_trace(go.Scatter(
        x=ticker_df['timestamp'], y=ticker_df['support'],
        mode='lines', name='Support',
        line=dict(color='green', width=2, dash='dot')
    ), row=2, col=1)

    # Resistance
    fig.add_trace(go.Scatter(
        x=ticker_df['timestamp'], y=ticker_df['resistance'],
        mode='lines', name='Resistance',
        line=dict(color='red', width=2, dash='dot')
    ), row=2, col=1)    
    
    fig.add_trace(go.Scatter(
        x=breakout_above['timestamp'],
        y=breakout_above['close'],
        mode='markers',
        name='Breakout Above',
        marker=dict(symbol='triangle-up', size=12, color='magenta', line=dict(width=1, color='black'))
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=breakout_below['timestamp'],
        y=breakout_below['close'],
        mode='markers',
        name='Breakout Below',
        marker=dict(symbol='triangle-down', size=12, color='gold', line=dict(width=1, color='black'))
    ), row=2, col=1)
    
    
    row = portfolio_df.query('Symbol == @ticker')
    amt = round((row.amt_earned.values[0] if not row.empty else 0), 2)
    
    avg_ret = round((ticker_df_date_filtered.close.pct_change().mean() * 100), 2)
    std_ret = round((ticker_df_date_filtered.close.pct_change().std()), 2)
    amt_text = f"+${amt}" if amt >= 0 else f"-${abs(amt)}"
    
    title_st = (
        f"{ticker} Performance<br>"
        f"Return: {amt_text}<br>"
        f"Average Daily Return: {avg_ret}%<br>"
        f"Volatility: {std_ret}<br>"
    )
    
    
    # --- Layout adjustments ---
    fig.update_layout(
        height=1200,
        title=dict(
            text=title_st,
            x=0.5,
            xanchor='center',
            yanchor='top',
            y=0.97,               # moves title slightly down (1.0 is top edge)
            font=dict(size=22),   # optional: increase size
            pad=dict(t=30)        # adds extra padding above title
        ),
        margin=dict(t=150),       # increase top margin to make space
        showlegend=True,
        template='plotly_white'
    )
    fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
    fig.update_xaxes(title_text="Date(9/8/2025-10/10/2025)", row=1, col=1)
    fig.update_yaxes(title_text="Price($)", row=1, col=1)
    fig.update_yaxes(title_text="Close Price($)", row=2, col=1)
    
    return fig

# ===== Page for Portfolio 1
# --- Creat dropdown options
options_port1 = ["Portfolio 1"] + p1_tickers
port1_page = html.Div(
    children = [
         html.H1("Portfolio 1 Analysis"),
         
         html.P(
             """
             The goal of this page is to display the performance of the portfolio as well
             as all of the stocks within it. This portfolio was created using graph theory to
             group similar stock together, and investing in one stock out of every cluster.
             """,
             style={
                 "textAlign": "center",
                 "fontStyle": "italic",
                 "color": "#555",
                 "marginTop": "15px",
            },
        ),
         
         
        dcc.Dropdown(
            id='port1dropdown',
            value=options_port1[0],
            options=[{"label": opt, "value": opt} for opt in options_port1],
            style={
                'width': '40%',
                'margin': '10px auto',
                'padding': '6px 10px',
                'border': '1px solid #ccc',
                'borderRadius': '8px',
                'fontSize': '15px',
                'backgroundColor': '#fafafa',
                'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.05)',
                'textAlign': 'left'
            },
            clearable=False,
            searchable=True
        ),
         
         html.Br(),
         
         html.Div(
             children=[
               dcc.Graph(id="port1")     
             ], style={'text-align':'center', 'display':'inline-block', 'width':'100%'}    
         )
    ], 
    style={'text-align':'center', 'display':'inline-block', 'width':'100%'}
)    



# ==== Port 2 page
options_port2 = ["Portfolio 2"] + p2_tickers
port2_page = html.Div(
    children = [
         html.H1("Portfolio 2 Analysis"),
         
         html.P(
             """
             The goal of this page is to display the performance of the portfolio as well
             as all of the stocks within it. This portfolio was created by choosing the best
             performing stock(by sharpes ratio) from every sector.
             """,
             style={
                 "textAlign": "center",
                 "fontStyle": "italic",
                 "color": "#555",
                 "marginTop": "15px",
            },
        ),
         
         
        dcc.Dropdown(
            id='port2dropdown',
            value=options_port2[0],
            options=[{"label": opt, "value": opt} for opt in options_port2],
            style={
                'width': '40%',
                'margin': '10px auto',
                'padding': '6px 10px',
                'border': '1px solid #ccc',
                'borderRadius': '8px',
                'fontSize': '15px',
                'backgroundColor': '#fafafa',
                'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.05)',
                'textAlign': 'left'
            },
            clearable=False,
            searchable=True
        ),
         
         html.Br(),
         
         html.Div(
             children=[
               dcc.Graph(id="port2")     
             ], style={'text-align':'center', 'display':'inline-block', 'width':'100%'}    
         )
    ], 
    style={'text-align':'center', 'display':'inline-block', 'width':'100%'}
)  
    
## PAGE LINK CALLBACK ###########################################
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)

def display_page(pathname):
    if pathname == "/port1":
        return port1_page
    elif pathname == "/port2":
        return port2_page
    return home_page
#Page CALLBACK####################################################


# =============== Portfolio 1 Page callback for dropwdown
@app.callback(
    Output("port1", "figure"),
    Input("port1dropdown", "value")
)
def update_port1_plot(selected_value):
    # Case 1: Entire portfolio
    if selected_value == "Portfolio 1":
        fig = portfolio_main_plot(p1_df_prices)
    
    
    
    elif selected_value in p1_tickers:
        fig = stock_vis(p1_PRICES_ALL, selected_value, portfolio_1_amt_earned_total)
    # (Later: add elif cases for individual stocks)
    # Example:
    # elif selected_value in p1_df_prices['Symbol'].unique():
    #     filtered_df = p1_df_prices[p1_df_prices['Symbol'] == selected_value]
    #     fig = portfolio_main_plot(filtered_df)
    
    else:
        fig = go.Figure()  # empty placeholder
    
    return fig


# =============== Portfolio 1 Page callback for dropwdown
@app.callback(
    Output("port2", "figure"),
    Input("port2dropdown", "value")
)
def update_port1_plot(selected_value):
    # Case 1: Entire portfolio
    if selected_value == "Portfolio 2":
        fig = portfolio_main_plot(p2_df_prices)
    
    elif selected_value in p2_tickers:
        fig = stock_vis(p2_PRICES_ALL, selected_value, portfolio_2_amt_earned_total)
    # (Later: add elif cases for individual stocks)
    # Example:
    # elif selected_value in p1_df_prices['Symbol'].unique():
    #     filtered_df = p1_df_prices[p1_df_prices['Symbol'] == selected_value]
    #     fig = portfolio_main_plot(filtered_df)
    
    else:
        fig = go.Figure()  # empty placeholder
    
    return fig


if __name__ == "__main__":

    app.run(debug=True, port=8054)
