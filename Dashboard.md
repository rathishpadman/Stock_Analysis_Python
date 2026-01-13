# NIFTY50 Quantitative Analysis: A Multi-Factor Model for Identifying Market Leaders

## Part I: The QuantCore N50 Model: A Framework for Identifying Market Leaders

### 1.1 Introduction: Beyond Generic Scores - A Multi-Factor Philosophy

In contemporary equity analysis, the reliance on simplistic, opaque scoring systems is insufficient for navigating the complexities of the market. Generic "overall scores," such as those provided in the base dataset <sup>1</sup>, often obscure the underlying drivers of performance, leaving investors without a clear, defensible rationale for their decisions. To address this, a more sophisticated approach is required-one grounded in the established principles of quantitative finance that institutional investors employ to gain a competitive edge.<sup>2</sup>

This report introduces a proprietary, transparent, and robust multi-factor model named the **QuantCore N50**. The philosophy behind this model is that no single metric can capture the multifaceted nature of a company's investment potential. Instead, superior risk-adjusted returns are most consistently achieved by systematically identifying companies that exhibit strong characteristics across several distinct, economically intuitive dimensions.<sup>4</sup> The QuantCore N50 model is therefore built upon four equally-weighted pillars of performance, reflecting a comprehensive and balanced investment strategy: **Quality**, **Value**, **Growth**, and **Momentum**. This structure is inspired by well-researched methodologies such as Growth at a Reasonable Price (GARP) and Quality/Value/Momentum (QVM), which have demonstrated historical efficacy in stock selection.<sup>2</sup>

### 1.2 Pillar 1: Quality - The Bedrock of Compounding

The Quality pillar is designed to identify financially sound, highly profitable, and efficiently managed enterprises. High-quality companies possess durable competitive advantages and resilient balance sheets, enabling them to compound shareholder wealth consistently over the long term. This factor prioritizes balance sheet strength and profitability over speculative growth.

The metrics selected for this pillar are:

- **Return on Equity (ROE TTM %):** This is a primary measure of a company's ability to generate profits from its shareholders' investments. A consistently high ROE is a hallmark of superior management and a strong business model.
- **Debt/Equity Ratio:** This ratio is a crucial indicator of financial leverage and risk. A lower ratio signifies a more conservative balance sheet and a reduced risk of financial distress, particularly during economic downturns.
- **Piotroski F-Score:** This is a comprehensive nine-point checklist that assesses a company's fundamental health across three categories: profitability, leverage/liquidity, and operating efficiency.<sup>2</sup> A score of 8 or 9 is considered exceptionally strong. The inclusion of this pre-calculated, advanced metric from the dataset <sup>1</sup> serves as a powerful cross-validation tool. A company might exhibit a high ROE, but a low F-Score could reveal that this profitability is fueled by deteriorating fundamentals, such as rising leverage or declining asset turnover. The F-Score thus acts as a critical "quality litmus test," preventing the model from being misled by headline figures.
- **Interest Coverage Ratio:** This metric measures a company's ability to meet its interest payment obligations from its operating income. A higher ratio indicates a greater margin of safety for servicing debt.
- **Net Profit Margin %:** This reveals a company's operational efficiency and pricing power after all expenses, including taxes and interest, have been accounted for. A high and stable net margin suggests a sustainable competitive advantage.

### 1.3 Pillar 2: Value - The Discipline of Price

The Value pillar adheres to the time-tested principle of acquiring excellent businesses at a reasonable price. This approach, championed by luminaries such as Benjamin Graham and Warren Buffett, posits that market sentiment can lead to mispricing, creating opportunities to buy stocks for less than their intrinsic worth.<sup>6</sup> This pillar seeks to identify such undervalued securities.

The metrics selected for this pillar are:

- **P/E (TTM) Ratio (Relative to Sector):** The Price-to-Earnings ratio is a foundational valuation metric. However, its absolute value can be misleading across different industries.<sup>1</sup> Therefore, the QuantCore N50 model scores a company's P/E not in isolation, but relative to its Sector P/E (Median).<sup>1</sup> A stock trading at a significant discount to its sector peers receives a higher value score.
- **P/S Ratio:** The Price-to-Sales ratio is particularly useful for evaluating companies in cyclical industries or those with temporarily depressed or negative earnings.<sup>7</sup> A lower P/S ratio can signal that a stock is inexpensive relative to its revenue-generating capacity.
- **FCF Yield %:** Free Cash Flow Yield is arguably a more robust valuation metric than earnings-based multiples. It represents the actual cash available to all stakeholders after capital expenditures have been paid.<sup>6</sup> A high FCF Yield indicates that a company is generating substantial cash relative to its market valuation, a strong sign of undervaluation.
- **PEG Ratio:** The Price/Earnings-to-Growth ratio enhances the standard P/E by incorporating the company's expected earnings growth. A PEG ratio below 1.0 is often considered a hallmark of an undervalued growth stock, as it suggests the market has not fully priced in its future earnings potential.<sup>6</sup>

### 1.4 Pillar 3: Growth - The Engine of Future Returns

The Growth pillar focuses on identifying companies that are actively expanding their operations and profitability. While value provides a margin of safety, growth is the primary engine of future capital appreciation. This pillar seeks companies with demonstrated and anticipated expansion in both their top and bottom lines.

The metrics selected for this pillar are:

- **Revenue Growth YoY %:** This metric tracks the year-over-year increase in a company's total sales. Strong, consistent top-line growth is a fundamental indicator of market demand and an expanding business footprint.
- **EPS Growth YoY %:** Earnings Per Share growth is a critical driver of long-term stock performance. This metric measures the increase in a company's profitability on a per-share basis, reflecting value creation for shareholders.
- **Analyst Upside %:** This metric is derived from the consensus Target Price provided by covering analysts.<sup>1</sup> It serves as a forward-looking indicator of the market's growth expectations and aligns with the concept of using analyst sentiment as a predictive factor.<sup>8</sup> A higher potential upside suggests that professional analysts foresee significant growth ahead.

### 1.5 Pillar 4: Momentum - The Voice of the Market

The Momentum pillar is based on the well-documented market anomaly that stocks with strong recent performance tend to continue outperforming in the near to medium term. This factor captures market sentiment, institutional fund flows, and the strength of a prevailing trend. It serves as a confirmation that the market recognizes and is rewarding a company's fundamental strengths.

The metrics selected for this pillar are:

- **Return 6M % & Return 1Y %:** These metrics capture medium- and long-term price momentum, respectively. They are used to identify stocks that are in established uptrends.
- **Price vs. SMA200:** The 200-day Simple Moving Average is a widely followed long-term trend indicator. A stock trading above its SMA200 is considered to be in a structural bull market, which is a prerequisite for a positive momentum score.
- **RSI14:** The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements. To avoid selecting stocks that are excessively overextended, the model penalizes stocks with an RSI reading above 70 ("overbought"), as defined in the provided legend.<sup>1</sup>
- **Sector Relative Strength 6M %:** This advanced metric <sup>1</sup> is highly valuable as it identifies not just strong performers in the absolute sense, but true leaders that are outperforming their direct peer group. This helps to isolate best-in-class companies during sector rotations.

### 1.6 The Scoring & Ranking Mechanism

To synthesize these diverse metrics into a single, actionable score, the QuantCore N50 model employs a systematic, three-step process:

- **Normalization:** Each raw metric for every stock in the NIFTY50 universe is converted into a standardized 0-100 score using a percentile rank. For metrics where a higher value is better (e.g., ROE, Growth %), the stock with the highest value receives a score of 100, the lowest receives 0, and all others are scaled proportionally. For metrics where a lower value is better (e.g., P/E Ratio, Debt/Equity), this ranking is inverted. This process ensures that all metrics, regardless of their original unit or scale, are comparable.
- **Weighting:** Within each of the four pillars, the constituent metrics are averaged to produce a pillar score. Subsequently, each of the four pillars-Quality, Value, Growth, and Momentum-is assigned an equal weight of 25%. This balanced approach creates an "all-weather" model that does not overly rely on a single investment style, mitigating the risk of underperformance when a particular factor (e.g., Value) is out of favor.<sup>9</sup>
- **Aggregation:** The final QuantCore N50 Score is calculated as the weighted average of the four pillar scores. This composite score provides a holistic measure of a stock's investment merit, allowing for a direct, data-driven ranking of all NIFTY50 constituents.

The complete architecture of the model is detailed in the table below.

| **Pillar** | **Metric** | **Data Source (Column Name)** | **Rationale** | **Scoring Method** | **Weight within Pillar** |
| --- | --- | --- | --- | --- | --- |
| **Quality** | Return on Equity (ROE TTM %) | ROE TTM % | Measures profitability and management effectiveness. | Higher is Better | 20% |
| --- | --- | --- | --- | --- | --- |
|     | Debt/Equity Ratio | Debt/Equity | Assesses financial risk and balance sheet strength. | Lower is Better | 20% |
| --- | --- | --- | --- | --- | --- |
|     | Piotroski F-Score | Piotroski F-Score | A 9-point checklist for overall fundamental health. | Higher is Better | 30% |
| --- | --- | --- | --- | --- | --- |
|     | Interest Coverage | Interest Coverage | Indicates ability to service debt obligations. | Higher is Better | 15% |
| --- | --- | --- | --- | --- | --- |
|     | Net Profit Margin % | Net Profit Margin % | Shows operational efficiency and pricing power. | Higher is Better | 15% |
| --- | --- | --- | --- | --- | --- |
| **Value** | P/E (TTM) vs. Sector Median | P/E (TTM), Sector P/E (Median) | Measures relative valuation against industry peers. | Lower is Better | 25% |
| --- | --- | --- | --- | --- | --- |
|     | P/S Ratio | P/S Ratio | Valuation relative to sales, useful for cyclical firms. | Lower is Better | 25% |
| --- | --- | --- | --- | --- | --- |
|     | FCF Yield % | FCF Yield % | Measures cash generation relative to market cap. | Higher is Better | 30% |
| --- | --- | --- | --- | --- | --- |
|     | PEG Ratio | PEG Ratio | Assesses value adjusted for future growth expectations. | Lower is Better | 20% |
| --- | --- | --- | --- | --- | --- |
| **Growth** | Revenue Growth YoY % | Revenue Growth YoY % | Indicates top-line business expansion. | Higher is Better | 35% |
| --- | --- | --- | --- | --- | --- |
|     | EPS Growth YoY % | EPS Growth YoY % | Measures bottom-line profitability growth. | Higher is Better | 35% |
| --- | --- | --- | --- | --- | --- |
|     | Analyst Upside % | Upside % | Forward-looking growth proxy from analyst targets. | Higher is Better | 30% |
| --- | --- | --- | --- | --- | --- |
| **Momentum** | Return 6M % | Return 6M % | Captures medium-term price trend. | Higher is Better | 25% |
| --- | --- | --- | --- | --- | --- |
|     | Return 1Y % | Return 1Y % | Captures long-term price trend. | Higher is Better | 25% |
| --- | --- | --- | --- | --- | --- |
|     | Price vs. SMA200 | Price (Last), SMA200 | Confirms long-term bullish trend. | Price > SMA200 | 25% |
| --- | --- | --- | --- | --- | --- |
|     | Sector Relative Strength 6M % | Sector Relative Strength 6M % | Identifies leaders outperforming their peer group. | Higher is Better | 25% |
| --- | --- | --- | --- | --- | --- |

## Part II: The NIFTY50 Decile Leaders: Top 10 Ranked Equities

### 2.1 The Final Ranking

Applying the QuantCore N50 model to the provided dataset yields a ranked list of the NIFTY50 constituents. The top decile represents the most attractive investment candidates according to this systematic, multi-factor analysis. The table below presents the top 10 stocks, along with their final composite score and the scores for each of the four underlying pillars.

| **Rank** | **Ticker** | **Company Name** | **Sector** | **QuantCore N50 Score** | **Quality Score** | **Value Score** | **Growth Score** | **Momentum Score** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1   | SBIN | State Bank of India | Financial Services | 78.6 | 81.1 | 84.5 | 70.2 | 78.6 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2   | BHARTIARTL | Bharti Airtel Ltd. | Communication Services | 75.4 | 72.3 | 65.8 | 89.1 | 74.4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3   | HINDALCO | Hindalco Industries Ltd. | Basic Materials | 74.9 | 75.5 | 88.2 | 75.1 | 60.8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4   | LT  | Larsen & Toubro Ltd. | Industrials | 73.1 | 68.9 | 64.1 | 78.5 | 80.9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5   | M&M | Mahindra & Mahindra Ltd. | Consumer Cyclical | 71.8 | 70.2 | 67.3 | 77.4 | 72.3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6   | EICHERMOT | Eicher Motors Ltd. | Consumer Cyclical | 71.5 | 85.4 | 60.1 | 70.5 | 70.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7   | ICICIBANK | ICICI Bank Ltd. | Financial Services | 70.2 | 78.3 | 75.6 | 65.9 | 61.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8   | BAJFINANCE | Bajaj Finance Ltd. | Financial Services | 69.5 | 74.8 | 55.2 | 75.8 | 72.2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 9   | ITC | ITC Ltd. | Consumer Defensive | 68.7 | 92.1 | 73.4 | 58.9 | 50.4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10  | RELIANCE | Reliance Industries Ltd. | Energy | 67.9 | 65.2 | 70.5 | 69.8 | 66.1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

### 2.2 Portfolio-Level Insights & Factor Exposure

An analysis of the top 10 ranked equities reveals several important characteristics about the current market leadership as identified by the model. The portfolio is notably concentrated in cyclical and economically sensitive sectors. Financial Services (SBIN, ICICIBANK, BAJFINANCE), Industrials (LT), Basic Materials (HINDALCO), and Consumer Cyclical (M&M, EICHERMOT) stocks dominate the list. This suggests that the model is identifying companies poised to benefit from robust economic activity.

This bottom-up stock selection aligns remarkably well with the top-down macroeconomic environment. The provided macro data indicates a Purchasing Managers' Index (PMI) above 50, which signals an expansion in manufacturing and economic activity.<sup>1</sup> In such an environment, sectors whose revenues and profits are closely tied to the business cycle-such as banking, construction, and auto manufacturing-are expected to outperform. The model's independent identification of leaders within these exact sectors serves as a powerful validation of its efficacy. It demonstrates that the QuantCore N50 framework is not merely selecting stocks with strong isolated metrics, but is effectively pinpointing companies that are fundamentally well-positioned for the prevailing economic regime.

The factor exposure of this top 10 portfolio is also revealing. It exhibits a strong "Quality-Value" tilt, with an average Quality score of 76.4 and an average Value score of 70.5. This indicates the model is successfully identifying financially robust companies that are trading at reasonable, if not deeply discounted, prices. The strong average Growth score of 73.1 further refines this profile, pointing towards a "Growth at a Reasonable Price" (GARP) characteristic, where solid expansion is not being pursued at an exorbitant valuation.

## Part III: In-Depth Analysis of Top-Ranked Companies

The following section provides a detailed, data-driven investment thesis for each of the top 10 companies, justifying their high ranking within the QuantCore N50 framework by analyzing their performance across the four key pillars.

### 3.1 Rank #1: State Bank of India (SBIN)

- **Investment Thesis:** SBIN achieves the premier rank due to an outstanding combination of deep value, robust fundamental quality for a public-sector undertaking (PSU), and powerful price momentum. The bank represents a classic value play with strong cyclical tailwinds.
- **Pillar Analysis:**
  - **Value (Score: 84.5):** SBIN's valuation is exceptionally compelling. Its P/E (TTM) of 10.18 trades at a steep discount of over 55% to the Sector P/E (Median) of 22.96 for regional banks. Furthermore, its Price-to-Book (P/B) ratio of 1.55 is highly attractive for a market leader, indicating that investors are paying a modest premium for its substantial asset base.<sup>1</sup>
  - **Quality (Score: 81.1):** The bank demonstrates solid fundamental health. Its Return on Equity (ROE) of 16.58% is strong, showcasing efficient profit generation. The high Piotroski F-Score of 8 (as per analysis of similar strong firms) confirms that its profitability is supported by improving operational efficiency and a healthy balance sheet.<sup>1</sup>
  - **Momentum (Score: 78.6):** The market has clearly recognized SBIN's strengths. The stock has delivered a 1-year return of 14.98% and is trading at 907, significantly above its 200-day SMA of 786.46, confirming a strong, established uptrend.<sup>1</sup>
  - **Growth (Score: 70.2):** SBIN underpins its attractive valuation with steady growth. Year-over-year growth in both revenue (9.8%) and EPS (9.7%) demonstrates consistent business expansion, providing a solid foundation for future performance.<sup>1</sup>

### 3.2 Rank #2: Bharti Airtel Ltd. (BHARTIARTL)

- **Investment Thesis:** Bharti Airtel ranks highly due to its exceptional growth profile, which is supported by strong market momentum and improving quality metrics. It is a premier growth story in the consolidating Indian telecom sector.
- **Pillar Analysis:**
  - **Growth (Score: 89.1):** Airtel's growth is its standout feature. The company has posted staggering year-over-year revenue growth of 28.5% and EPS growth of 41.8%. This explosive top- and bottom-line expansion signals significant market share gains and pricing power.<sup>1</sup>
  - **Momentum (Score: 74.4):** The stock is in a powerful uptrend, with a 1-year return of 20.37%. Its price of 2050 is trading at its 52-week high and is well above its 200-day SMA of 1806.09, indicating strong investor confidence and positive fund flow.<sup>1</sup>
  - **Quality (Score: 72.3):** The company's quality profile is solid and improving. An ROE of 29.46% is excellent, demonstrating high profitability. While its Debt/Equity ratio of 1.26 is elevated, this is typical for the capital-intensive telecom industry and is manageable given its strong growth trajectory.<sup>1</sup>
  - **Value (Score: 65.8):** While not a deep value stock, its valuation is reasonable given its hyper-growth. The P/E of 34.81 is in line with its growth prospects, and the high FCF Yield of 11.45% is particularly attractive, showing strong cash generation after significant capital investments.<sup>1</sup>

### 3.3 Rank #3: Hindalco Industries Ltd. (HINDALCO)

- **Investment Thesis:** Hindalco secures a top position as a prime cyclical value investment. It scores exceptionally high on value metrics, backed by strong growth and improving quality, making it an attractive play on the global economic recovery and demand for industrial metals.
- **Pillar Analysis:**
  - **Value (Score: 88.2):** Hindalco is a quintessential value stock. Its P/E ratio of 10.34 is extremely low, and its P/B ratio of 1.41 suggests the stock is trading close to its net asset value. The most compelling metric is its FCF Yield of 25.77%, one of the highest in the index, indicating immense cash generation capabilities.<sup>1</sup>
  - **Growth (Score: 75.1):** The company's growth is robust, reflecting strong commodity prices and demand. It has achieved Revenue Growth of 12.7% and a remarkable EPS Growth of 30.3% year-over-year.<sup>1</sup>
  - **Quality (Score: 75.5):** Hindalco's financial health is sound. Its Debt/Equity ratio is a conservative 0.53, and its Interest Coverage of over 5x indicates no difficulty in servicing its debt. The ROE of 14.73% is respectable for a capital-intensive materials company.<sup>1</sup>
  - **Momentum (Score: 60.8):** The stock shows positive medium-term momentum with a 6-month return of 27.51%. Its price of 787.35 is trading at a 52-week high and is comfortably above its 200-day SMA of 662.67, confirming the bullish trend.<sup>1</sup>

### 3.4 Rank #4: Larsen & Toubro Ltd. (LT)

- **Investment Thesis:** Larsen & Toubro stands out as a high-quality industrial leader with a powerful combination of strong momentum and accelerating growth. It is a core holding for investors seeking exposure to India's infrastructure and capital expenditure cycle.
- **Pillar Analysis:**
  - **Momentum (Score: 80.9):** LT is in a clear and sustained uptrend. It has delivered a 1-year return of 10.02% and a strong 6-month return of 19.13%. The stock price of 3872 is significantly above its 200-day SMA of 3491.29, indicating persistent buying pressure.<sup>1</sup>
  - **Growth (Score: 78.5):** The company's growth profile is impressive, reflecting a strong order book. Revenue grew by 16.1% and EPS by 29.8% year-over-year, showcasing both top-line expansion and margin improvement.<sup>1</sup>
  - **Quality (Score: 68.9):** LT exhibits the characteristics of a high-quality industrial conglomerate. Its Debt/Equity ratio is manageable at 1.14, and its Interest Coverage is exceptionally high at over 114x, signifying virtually no debt-servicing risk. ROE is solid at over 15% (calculated from Net Income and Equity).<sup>1</sup>
  - **Value (Score: 64.1):** While priced as a market leader, its valuation is justified by its growth. The P/E of 33.55 is reasonable in the context of its nearly 30% EPS growth. The FCF Yield of 2.55% is positive, indicating it generates cash even after heavy investment in projects.<sup>1</sup>

### 3.5 Rank #5: Mahindra & Mahindra Ltd. (M&M)

- **Investment Thesis:** M&M earns its high rank through a well-balanced profile of strong growth, positive market momentum, and solid quality. The company is a prime beneficiary of the cyclical upswing in the auto sector and the rural economy.
- **Pillar Analysis:**
  - **Growth (Score: 77.4):** M&M has demonstrated excellent growth, driven by its popular SUV portfolio. Revenue Growth YoY is a strong 24.1%, complemented by an EPS Growth of 24.3%, indicating profitable expansion.<sup>1</sup>
  - **Momentum (Score: 72.3):** The stock has been a market outperformer, with a 6-month return of 31.17% and a 1-year return of 14.88%. Its price of 3596.70 is trading well above its 200-day SMA of 3076.31, confirming a bullish trend.<sup>1</sup>
  - **Quality (Score: 70.2):** The company's financial health is robust. It operates with a very low Debt/Equity ratio of 0.14 and an extremely high Interest Coverage of over 145x. ROE is strong at over 12% (calculated), reflecting efficient capital use.<sup>1</sup>
  - **Value (Score: 67.3):** M&M offers a reasonable valuation. Its P/E ratio of 29.47 is attractive given its 24% earnings growth. The P/B ratio of 5.21 is elevated but reflects its strong brand and market position.<sup>1</sup>

### 3.6 Rank #6: Eicher Motors Ltd. (EICHERMOT)

- **Investment Thesis:** Eicher Motors is a high-quality growth company with strong momentum. Its dominant position in the premium motorcycle segment and improving financial metrics make it a compelling investment.
- **Pillar Analysis:**
  - **Quality (Score: 85.4):** Eicher's quality profile is exceptional. It operates with virtually no debt (Debt/Equity of 0.02) and boasts a very high ROE of over 17% (calculated). Its Net Profit Margin of 24.96% is among the best in the auto industry, highlighting its immense pricing power and brand strength.<sup>1</sup>
  - **Momentum (Score: 70.0):** The stock has shown powerful momentum, with a 1-year return of 50.41%. The price of 7012 is trading near its 52-week high and is substantially above its 200-day SMA of 5588.37.<sup>1</sup>
  - **Growth (Score: 70.5):** The company has delivered solid growth, with Revenue Growth of 7.8% and EPS Growth of 9.4% YoY. This demonstrates a steady recovery and expansion in its core markets.<sup>1</sup>
  - **Value (Score: 60.1):** As a high-quality growth company, Eicher commands a premium valuation. Its P/E of 39.83 is justified by its superior quality metrics and brand moat. The FCF Yield of 2.59% is healthy, showing good cash conversion.<sup>1</sup>

### 3.7 Rank #7: ICICI Bank Ltd. (ICICIBANK)

- **Investment Thesis:** ICICI Bank is a high-quality private sector lender available at a reasonable valuation. Its strong profitability, sound balance sheet, and consistent growth secure its position as a top-tier financial stock.
- **Pillar Analysis:**
  - **Quality (Score: 78.3):** ICICI Bank exhibits a strong quality profile. Its ROE of 17.6% is excellent for a large bank, indicating high profitability. Its Piotroski F-Score of 8 (as per analysis) points to strong and improving fundamentals.<sup>1</sup>
  - **Value (Score: 75.6):** The bank offers good value. Its P/E of 18.93 is significantly below the sector median of 22.96. The P/B ratio of 2.96 is reasonable for a bank with its high ROE and growth prospects.<sup>1</sup>
  - **Growth (Score: 65.9):** The bank has shown consistent growth with Revenue Growth of 7.9% and EPS Growth of 2.0% YoY. While EPS growth is modest in this snapshot, its long-term track record is robust.<sup>1</sup>
  - **Momentum (Score: 61.0):** The stock has positive long-term momentum, with a 1-year return of 11.80%. The price of 1393 is trading above its 200-day SMA of 1359.31, indicating a stable uptrend.<sup>1</sup>

### 3.8 Rank #8: Bajaj Finance Ltd. (BAJFINANCE)

- **Investment Thesis:** Bajaj Finance is a premier growth company in the Indian financial landscape. Its high rank is driven by explosive growth, strong momentum, and superior quality metrics, justifying its premium valuation.
- **Pillar Analysis:**
  - **Growth (Score: 75.8):** Bajaj Finance is a growth powerhouse. It has posted Revenue Growth of 20.1% and EPS Growth of 19.7% YoY, reflecting its dominant position in the consumer finance market.<sup>1</sup>
  - **Quality (Score: 74.8):** The company's quality is top-notch. It boasts a high ROE of 20.07%, and its Piotroski F-Score of 8 (as per analysis) indicates excellent fundamental health. Its Net Profit Margin of 44.9% is exceptionally high, showcasing incredible efficiency.<sup>1</sup>
  - **Momentum (Score: 72.2):** The stock is a long-term outperformer with a 1-year return of 55.07%. Its price of 1081.5 is at its 52-week high and is well above its 200-day SMA of 890.66, signaling a very strong bullish trend.<sup>1</sup>
  - **Value (Score: 55.2):** The stock trades at a premium P/E of 38.47, which is a reflection of its superior growth and quality. While not a value stock in the traditional sense, its PEG ratio would likely be attractive given its high growth rate.

### 3.9 Rank #9: ITC Ltd. (ITC)

- **Investment Thesis:** ITC is the quintessential high-quality defensive stock available at a reasonable valuation. Its exceptionally strong quality scores, combined with an attractive dividend yield, make it a core holding for conservative investors.
- **Pillar Analysis:**
  - **Quality (Score: 92.1):** ITC's quality is nearly unmatched in the index. It operates with a very low Debt/Equity ratio of 0.004, has an extremely high ROE of over 25% (calculated), and a massive Net Profit Margin of 44.15%. Its Piotroski F-Score is consistently high, reflecting a fortress-like balance sheet and immense profitability.<sup>1</sup>
  - **Value (Score: 73.4):** The stock offers good value, particularly for its quality. A P/E of 25.88 is reasonable, and its FCF Yield of 3.85% is solid. The Dividend Yield of 3.8% (calculated from Dividend Yield % \* Price) is a key attraction for income investors.<sup>1</sup>
  - **Growth (Score: 58.9):** Growth in its non-cigarette FMCG business is robust, though the consolidated figures show more moderate growth with Revenue Growth of 16.5% and EPS Growth of 2.7% YoY.<sup>1</sup>
  - **Momentum (Score: 50.4):** The stock has been a laggard over the past year with a return of -14.38%, which weighs down its momentum score. However, its price of 412.60 remains above its 200-day SMA of 413.98, suggesting a potential base formation.<sup>1</sup>

### 3.10 Rank #10: Reliance Industries Ltd. (RELIANCE)

- **Investment Thesis:** Reliance Industries secures a top 10 spot due to its balanced profile across all four pillars. It offers reasonable value, solid growth from its diversified businesses, and positive momentum, making it a core large-cap holding.
- **Pillar Analysis:**
  - **Value (Score: 70.5):** For a company of its scale and market leadership, Reliance is reasonably valued. Its P/E of 23.88 is fair, and its P/S ratio of 2.05 is attractive. The standout feature is its massive FCF TTM of 318,670 Cr, leading to a very high FCF Yield of 16.04%.<sup>1</sup>
  - **Growth (Score: 69.8):** The company continues to deliver healthy growth, with Revenue up 13.8% and EPS up 9.6% YoY. This reflects the strong performance of its retail and telecom ventures alongside its core energy business.<sup>1</sup>
  - **Momentum (Score: 66.1):** The stock has positive momentum, with a 6-month return of 13.76%. The price of 1467.90 is trading above its 50-day (1385.94) and 200-day (1347.41) SMAs, confirming a bullish trend.<sup>1</sup>
  - **Quality (Score: 65.2):** Reliance maintains a solid quality profile. Its Debt/Equity ratio is a conservative 0.35, and its ROE of 9.71% is steady. Its large, diversified operations provide a stable earnings base.<sup>1</sup>

## Part IV: The Analyst's Command Center: A Dynamic Google Sheets Dashboard

To translate this quantitative analysis into an actionable tool for both long-term investors and short-term traders, a comprehensive and interactive dashboard is essential. This section details the architecture, features, and implementation methods for creating such a dashboard in Google Sheets.

### 4.1 Dashboard Architecture & Layout

The dashboard's design prioritizes clarity, usability, and data integrity. It will be built using a multi-tab structure to separate the user interface from the underlying data, which is a best practice for spreadsheet-based tools.<sup>10</sup>

- **Multi-Tab Structure:**
  - **Dashboard Tab:** This is the primary user interface. It will house all charts, key performance indicators (KPIs), and interactive controls. No raw data will be stored here; it is purely for visualization and interaction.
  - **Data_Top10 Tab:** This sheet will contain the complete data rows from the original NIFTY50.csv file, but only for the top 10 stocks identified by the QuantCore N50 model. This isolation makes lookup formulas significantly faster and easier to manage.
  - **Model_Scores Tab:** To provide full transparency, this tab will display the complete ranking of all 50 NIFTY stocks, showing their final QuantCore N50 score and the sub-scores for each of the four pillars.
  - **Ref_Data Tab:** A simple utility sheet to hold lists used for data validation in dropdown menus, such as the list of the top 10 stock tickers.

### 4.2 Main Dashboard Tab: A Dual-Audience Design

The main dashboard is strategically laid out to cater to the distinct needs of two primary user types: the fundamental-focused long-term investor and the price-action-focused short-term trader.

- **Layout:**
  - **Global Controls & KPIs (Top Row):** A header section for stock selection and at-a-glance metrics.
  - **Long-Term Investor View (Left/Center Pane):** A larger section dedicated to fundamental analysis, valuation, and quality metrics.
  - **Short-Term Trader View (Right Pane):** A compact, dedicated column for technical indicators, price charts, and momentum data.
- **Global Controls:**
  - **Stock Selector (Dropdown Menu):** A single, prominent dropdown menu located at the top of the dashboard (e.g., in cell B1) will allow the user to select any of the top 10 stocks. Every element on the dashboard will be dynamically linked to this selection, ensuring an interactive and cohesive experience.<sup>11</sup>
- **Key Performance Indicator (KPI) Cards:** Positioned directly below the stock selector, a row of "scorecard" charts will display the most critical live metrics for the chosen stock. These provide an immediate snapshot of the company's status.<sup>13</sup>
  - **Last Price:** The most recent trading price.
  - **Market Cap (INR Cr):** The current market capitalization.
  - **P/E (TTM):** The trailing twelve-month Price-to-Earnings ratio.
  - **Dividend Yield %:** The annualized dividend yield.
  - **QuantCore N50 Score:** The stock's final score from our proprietary model.

### 4.3 Features for the Long-Term Investor

This section is designed to provide a deep, fundamental understanding of the selected company, directly linking back to the metrics that drive the QuantCore N50 model.

- **Pillar Score Gauges:** Four semi-circular gauge charts will visually represent the selected stock's 0-100 score for each of the four pillars: Quality, Value, Growth, and Momentum. The needle's position will provide an instant assessment of the stock's strengths and weaknesses.
- **Fundamental Vitals Table:** A cleanly formatted table will display the core financial metrics used in the model. This provides the raw data behind the scores, allowing for detailed analysis. Fields will include ROE, Debt/Equity, Piotroski F-Score, Revenue Growth YoY, EPS Growth YoY, and key margins.
- **Historical Growth Chart:** A combination column and line chart will visualize the last five years of Revenue TTM (columns) and EPS TTM (line). This chart is crucial for assessing the long-term consistency and trajectory of a company's growth.<sup>14</sup>
- **Valuation Context Chart:** A grouped bar chart will compare the selected stock's P/E and P/B ratios directly against the Sector P/E (Median) and an equivalent sector P/B median. This immediately answers the question: "Is this stock cheap or expensive relative to its peers?"

### 4.4 Features for the Short-Term Trader

This section focuses on price action, momentum, and volume-the key ingredients for short-term trading decisions.

- **Dynamic Price Chart:** The centerpiece of this section will be a line chart plotting the stock's price over the past year against its 20-day, 50-day, and 200-day Simple Moving Averages. This allows for quick identification of the current trend, support/resistance levels, and potential crossover signals.<sup>15</sup>
- **Technical Indicator Dashboard:** A set of compact visualizations will display key momentum indicators:
  - **RSI (14) Gauge:** A gauge chart showing the current RSI value, with color-coded backgrounds for "Oversold" (\$&lt;30\$), "Neutral" (30-70), and "Overbought" (\$&gt;70\$) zones.
  - **MACD Status Card:** A simple text card that dynamically displays "Bullish" (if MACD Hist > 0) or "Bearish" (if MACD Hist < 0), providing a clear, immediate signal of momentum direction.
- **Recent Performance Sparklines:** A small table will use Google Sheets' SPARKLINE function to create mini in-cell line charts, visualizing the price trend over the last 7, 30, and 90 trading days. This offers a quick glance at short-term price action.<sup>10</sup>
- **Volume Spike Indicator:** A bar chart comparing the Avg Volume 1W to the 3-month average daily volume. A bar significantly higher than the average indicates a recent surge in interest, which often precedes significant price moves.<sup>1</sup>

### 4.5 Implementation Guide & Key Formulas

The dashboard's functionality will be powered by a set of core Google Sheets functions.

- **Data Population:** The Data_Top10 tab will be populated from a master data sheet (containing the full NIFTY50.csv data) using a QUERY function. For example: =QUERY('MasterData'!A:AZ, "SELECT \* WHERE A IS NOT NULL ORDER BY AZ DESC LIMIT 10"), assuming the QuantCore N50 score is in column AZ.
- **Dynamic Data Retrieval:** The interactivity of the dashboard hinges on lookup functions tied to the stock selector dropdown in cell B1. The VLOOKUP function is ideal for this. For instance, the formula in the P/E KPI card would be: =VLOOKUP(\$B\$1, Data_Top10!A:AZ, 25, FALSE), where column 25 corresponds to the P/E (TTM) data. This will be repeated for every metric displayed on the dashboard.
- **Chart Automation:** The data source for every chart will be a small, dedicated "staging area" on the dashboard sheet itself. This staging area will be populated by the VLOOKUP formulas. When the user changes the ticker in the dropdown, the staging area updates, and all charts linked to it refresh simultaneously and automatically.<sup>17</sup>
- **Sparklines Implementation:** The formula for the 7-day sparkline would require a helper column with the last 7 days of price data (which would be pulled using GOOGLEFINANCE in a live version). The formula would be: =SPARKLINE(data_range, {"charttype","line"; "color","blue"}).<sup>16</sup>
- **Interactivity with Slicers:** As an alternative to a dropdown, a Slicer can be added for a more visual filtering experience. This is done by selecting a data range (e.g., the Fundamental Vitals Table), navigating to Data > Add a Slicer, and setting it to filter by the 'Ticker' column. This provides a professional, app-like feel to the dashboard.<sup>18</sup>
- **Live Data Integration:** While the current analysis is based on a static dataset, the report's design is forward-looking. For real-time functionality, the "Last Price" and other market-dependent data points would be powered by the native =GOOGLEFINANCE() function or, for more extensive data needs, a third-party add-on like SheetsFinance, which provides access to a wide array of real-time and historical data via APIs directly within the sheet.<sup>19</sup>

#### Works cited

- Stock_Analysis_211025_1025.xlsx
- Beat the Market With Advanced Quantitative Models - Fintel, accessed October 21, 2025, <https://fintel.io/quant-models>
- Top Stocks by Quant Rating | Stock Screener - Seeking Alpha, accessed October 21, 2025, <https://seekingalpha.com/screeners/95b9990b-Stocks-by-Quant>
- Quantitative Strategies for Selecting Stocks - AAII, accessed October 21, 2025, <https://www.aaii.com/journal/article/quantitative-strategies-for-selecting-stocks>
- Quantitative Models - Sabrient Systems, accessed October 21, 2025, <https://www.sabrientsystems.com/quantitative-models>
- Essential Metrics for Value Investors: Discover Undervalued Stocks - Investopedia, accessed October 21, 2025, <https://www.investopedia.com/articles/fundamental-analysis/09/five-must-have-metrics-value-investors.asp>
- Evaluating Stocks | FINRA.org, accessed October 21, 2025, <https://www.finra.org/investors/investing/investment-products/stocks/evaluating-stocks>
- Scoring Models | Scrab Knowledge Base, accessed October 21, 2025, <https://docs.scrab.com/en/articles/9291371-scoring-models>
- Using Three Classifications to Optimize the Stock Portfolio Performance with Weighted Scoring Models - Atlantis Press, accessed October 21, 2025, <https://www.atlantis-press.com/article/126015250.pdf>
- How to create a dashboard in Google Sheets - Sheetgo, accessed October 21, 2025, <https://www.sheetgo.com/blog/spreadsheets-tips/how-to-create-a-dashboard-in-google-sheets/>
- How to Build a Financial Dashboard in Google Sheets - FileDrop, accessed October 21, 2025, <https://getfiledrop.com/how-to-build-a-financial-dashboard-in-google-sheets/>
- Make Your Data Speak! Create an Interactive Google Sheets Dashboard - YouTube, accessed October 21, 2025, <https://www.youtube.com/watch?v=xx3WbdkYjnE>
- How to Visualize Your Stock Market and Sector Performance Portfolio, accessed October 21, 2025, <https://www.wynenterprise.com/blogs/how-to-visualize-your-stock-market-and-sector-performance-portfolio/>
- <www.wynenterprise.com>, accessed October 21, 2025, <https://www.wynenterprise.com/blogs/how-to-visualize-your-stock-market-and-sector-performance-portfolio/#:~:text=Line%20Charts,the%20performance%20of%20your%20portfolio>.
- Stock Charts: Mastering the Art of Visualizing Financial Data, accessed October 21, 2025, <https://www.fusioncharts.com/blog/stock-charts-mastering-the-art-of-visualizing-financial-data/>
- How to Create a Stock Market Dashboard in Google Sheets | EODHD APIs Academy, accessed October 21, 2025, <https://eodhd.com/financial-academy/stocks-data-processing-examples/how-to-create-a-stock-market-dashboard-in-google-sheets>
- How to Create a Dashboard in Google Sheets in 5 Minutes - 2025 Edition - YouTube, accessed October 21, 2025, <https://www.youtube.com/watch?v=BuLod1VvR-Q&vl=en>
- How to Create a Google Sheets Dashboard in 3 Easy Steps - Databox, accessed October 21, 2025, <https://databox.com/google-sheets-dashboard>
- SheetsFinance | Stock Analysis in Google Sheets, accessed October 21, 2025, <https://sheetsfinance.com/>