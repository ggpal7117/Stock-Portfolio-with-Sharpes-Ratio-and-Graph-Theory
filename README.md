# Stock Portfolio with Sharpe's Ratio & Graph-Theory Clustering 📈

Welcome to Stock Portfolio with Sharpe's Ratio & Graph-Theory Clustering — a Python project that builds and evaluates stock portfolios based on clustering stocks with similar return behaviors, and selecting the highest Sharpe-ratio stock from each cluster. It also includes a live interactive dashboard (built with Dash) for exploring results.

Dashboard: https://stock-portfolio-with-sharpes-ratio-and.onrender.com

## 🚀 Project Overview

This project aims to explore an alternative, cluster-based approach to portfolio construction by combining techniques from financial analysis and graph theory. The core idea:

Use graph theory to cluster stocks (from the S&P 500 + major indexes listed on CNBC) based on similarity of their return time series.

For each cluster, compute the Sharpe ratio of each stock and select the one with the highest Sharpe ratio — provided it meets a predefined threshold — to include in the portfolio.

Compare this cluster-based portfolio with a second portfolio built using a simpler and more traditional grouping: by GICS (sector) classification.

Visualize and compare the performance of the portfolios and individual stocks via an interactive dashboard built with Dash.

## Key Findings

The GICS-sector-based portfolio outperformed the graph-theory-clustered portfolio (by a modest margin) in this implementation.

The project demonstrates how clustering and alternative grouping strategies can provide insights beyond conventional sector-based diversification.


## ✅ Why This Project Matters

Showcases a fusion of quantitative finance (portfolio theory / Sharpe ratio) and graph theory/network analysis.

Demonstrates an end-to-end workflow: data acquisition → data processing → clustering & analysis → portfolio construction → interactive visualization.

Useful as a reference or educational tool for anyone interested in alternative portfolio construction methods, financial data analysis, and dashboarding.

The dashboard makes results accessible to both technical and non-technical audiences — a good example of how data science work can be communicated clearly.
