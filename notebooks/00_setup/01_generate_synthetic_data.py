# Databricks notebook source
# MAGIC %md
# MAGIC # Executive Decision Studio — Synthetic Data Generation
# MAGIC **Alinta Energy | Databricks Executive Decision Studio**
# MAGIC
# MAGIC Generates realistic synthetic data across all EDS tables including:
# MAGIC - Generation asset register
# MAGIC - Board and strategy documents (15 documents with full content)
# MAGIC - Financial data (FY24-FY27, monthly, 4 business units)
# MAGIC - KPI time-series (12 KPIs, Jan 2024 – Dec 2026)
# MAGIC - Risk register (50 items)
# MAGIC - Action items (100 items)
# MAGIC - Decision register (50 records)

# COMMAND ----------

# MAGIC %pip install faker --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import uuid
import random
import math
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pyspark.sql import Row
from pyspark.sql.functions import current_timestamp, lit
from faker import Faker

fake = Faker('en_AU')
random.seed(42)

CATALOG = "ausnet_process_intel_catalog"
spark.sql(f"USE CATALOG {CATALOG}")

print("Starting Alinta Energy synthetic data generation...")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Asset Register

# COMMAND ----------

assets = [
    {
        "asset_id": "ASSET-001",
        "asset_name": "Loy Yang B Power Station",
        "asset_type": "thermal",
        "capacity_mw": 1480.0,
        "fuel": "brown_coal",
        "location": "Traralgon",
        "state": "VIC",
        "market": "NEM",
        "commissioning_year": 1993,
        "status": "operating",
        "owner_bu": "Generation",
    },
    {
        "asset_id": "ASSET-002",
        "asset_name": "Yandin Wind Farm",
        "asset_type": "wind",
        "capacity_mw": 400.0,
        "fuel": "wind",
        "location": "Dandaragan",
        "state": "WA",
        "market": "WEM",
        "commissioning_year": 2020,
        "status": "operating",
        "owner_bu": "Generation",
    },
    {
        "asset_id": "ASSET-003",
        "asset_name": "Newman Power Station",
        "asset_type": "gas_peaker",
        "capacity_mw": 180.0,
        "fuel": "gas",
        "location": "Newman",
        "state": "WA",
        "market": "WEM",
        "commissioning_year": 1981,
        "status": "operating",
        "owner_bu": "Generation",
    },
    {
        "asset_id": "ASSET-004",
        "asset_name": "Wagerup Power Station",
        "asset_type": "gas_peaker",
        "capacity_mw": 220.0,
        "fuel": "gas",
        "location": "Wagerup",
        "state": "WA",
        "market": "WEM",
        "commissioning_year": 2003,
        "status": "operating",
        "owner_bu": "Generation",
    },
    {
        "asset_id": "ASSET-005",
        "asset_name": "Pinjarra Power Station",
        "asset_type": "gas_peaker",
        "capacity_mw": 180.0,
        "fuel": "gas",
        "location": "Pinjarra",
        "state": "WA",
        "market": "WEM",
        "commissioning_year": 1997,
        "status": "operating",
        "owner_bu": "Generation",
    },
]

asset_rows = [Row(**a) for a in assets]
asset_df = spark.createDataFrame(asset_rows)
asset_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.eds_synthetic.asset_register")
print(f"[OK] asset_register: {asset_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Board and Strategy Documents

# COMMAND ----------

documents = [
    {
        "doc_id": "DOC-001",
        "title": "FY2025 Group Strategy Review — Navigating the Energy Transition",
        "doc_type": "strategy",
        "classification": "RESTRICTED",
        "access_tier_level": 1,
        "business_area": "Group",
        "effective_date": date(2024, 7, 1),
        "author": "Group Strategy & Corporate Development",
        "version": "v2.1",
        "content": """ALINTA ENERGY GROUP
FY2025 GROUP STRATEGY REVIEW — NAVIGATING THE ENERGY TRANSITION

EXECUTIVE SUMMARY

Alinta Energy stands at a pivotal inflection point in the Australian energy landscape. As the nation accelerates its transition to a low-carbon economy, the Group must balance the near-term imperative to maintain reliable, affordable energy supply with the long-term strategic necessity of decarbonising its generation portfolio. This strategy review, approved by the Board on 1 July 2024, sets out Alinta's five-year strategic roadmap to 2029.

Australia's National Electricity Market is undergoing the fastest large-scale energy transformation of any developed nation. Renewable energy penetration in the NEM exceeded 38% in FY24, driven by record solar and wind capacity additions. Wholesale electricity prices in Victoria averaged $98/MWh in FY24, compared to $75/MWh in FY22, reflecting tighter supply conditions as aging thermal assets retire. The Western Australian WEM market continues its transformation under the Wholesale Electricity Market reform, with the new capacity mechanism driving investment signals.

STRATEGIC PRIORITIES FY2025-FY2029

1. MANAGED TRANSITION OF LOYS YANG B
Loy Yang B (1,480 MW, brown coal) remains Alinta's single largest asset and the biggest strategic variable. The asset generated 8.4 TWh in FY24 and contributed approximately $380 million to Group EBITDA. Market analysis indicates the asset remains economic until approximately 2028-2030 under base-case carbon price projections, but faces increasing risk from accelerating renewable entry and potential carbon policy tightening post-2026 Federal election. Management has engaged Jacobs Engineering to develop a detailed transition study encompassing technical decommissioning requirements, workforce transition planning for approximately 600 direct employees, and site remediation cost estimates currently projected at $350-500 million. The Board has approved a strategic review process to evaluate options including: continued operation to natural end-of-life, early accelerated retirement (2027), conversion to gas, and potential sale to a specialist operator.

2. WESTERN AUSTRALIA GROWTH PLATFORM
Alinta's WA business represents a significant organic growth opportunity. The Group's existing WEM generation portfolio (Yandin Wind Farm 400 MW, Newman Power Station 180 MW, Wagerup Power Station 220 MW, Pinjarra Power Station 180 MW) provides a strong platform. Management is evaluating three development projects: (a) Yandin Wind Farm Stage 2 expansion of 200 MW (estimated capex $380 million, FID targeted H2 FY26), (b) Oakajee battery storage project of 200 MW / 800 MWh (capex $280 million, FID H1 FY27), and (c) Merredin Solar Farm of 150 MW (capex $180 million, FID FY27). These projects would add approximately 550 MW of new renewable capacity in WA by FY28.

3. RETAIL MARKET POSITIONING
Alinta's Retail business serves approximately 1.1 million customer accounts across gas and electricity in QLD, NSW, VIC, SA, and WA. Churn rates elevated to 22% in FY24 as customers sought cheaper tariffs amid cost-of-living pressures. Management is implementing a digital transformation program (total investment $85 million over three years) targeting a 25% reduction in cost-to-serve and improved Net Promoter Score from +18 to +30 by FY27. Key initiatives include a new CRM platform migration to Salesforce, AI-powered tariff optimisation for small business customers, and an enhanced EV charging bundle product.

4. TRADING AND RISK MANAGEMENT
The Energy Trading division achieved EBITDA of $42 million in FY24, exceeding budget by $12 million through disciplined position management during Q2 volatility events. The Risk Committee has approved an increase in the Value-at-Risk limit from $15 million to $20 million (95% confidence, 10-day horizon) to capture additional spread trading opportunities in the NEM, subject to enhanced daily reporting to the CFO.

5. CAPITAL ALLOCATION FRAMEWORK
The Board has reaffirmed the Group's capital allocation priorities: (1) Maintain investment-grade credit metrics (Net Debt/EBITDA < 3.5x); (2) Fund organic growth projects with WACC hurdle rate of 9.5%; (3) Progressive ordinary dividend policy with 50-70% payout ratio; (4) Return surplus capital to shareholders when leverage is below 2.5x. The FY25 capital programme totals $420 million, comprising $180 million sustaining capex, $160 million growth capex in WA renewables, and $80 million in retail digital transformation.

FINANCIAL OUTLOOK

Group revenue is forecast at $3.2 billion for FY25, with EBITDA of $580 million (margin 18.1%) and NPAT of $195 million. Net debt is targeted at $1.4 billion at 30 June 2025 (2.4x EBITDA leverage). The five-year strategy targets cumulative free cash flow of $1.8 billion and a portfolio EBITDA mix shift from 65% thermal / 35% renewable+retail in FY24 to 40% thermal / 60% renewable+retail by FY29.

RISK OUTLOOK
The primary strategic risks to this plan are: (1) accelerated carbon policy beyond base case; (2) faster-than-expected thermal price cannibalisation from new renewable entry; (3) retail margin compression from elevated wholesale prices; (4) WA government intervention in WEM capacity payments; and (5) ESG investor pressure on financing costs for coal-linked assets. The Board has satisfied itself that the risk management framework is appropriate for the Group's risk profile.

This strategy was approved by the Alinta Energy Board of Directors on 1 July 2024.
""",
        "is_synthetic": True,
        "source_system": "BoardVantage",
    },
    {
        "doc_id": "DOC-002",
        "title": "Board Paper: Loy Yang B Transition — Strategic Options Analysis",
        "doc_type": "board_paper",
        "classification": "RESTRICTED",
        "access_tier_level": 1,
        "business_area": "Generation",
        "effective_date": date(2024, 9, 15),
        "author": "CEO / Head of Strategy",
        "version": "v1.3",
        "content": """ALINTA ENERGY BOARD OF DIRECTORS
BOARD PAPER — LOY YANG B TRANSITION: STRATEGIC OPTIONS ANALYSIS

FOR DECISION — September 2024 Board Meeting

PURPOSE
This paper presents the Board with a structured analysis of strategic options for Loy Yang B Power Station (LYB) in the context of Australia's accelerating energy transition. The Board is asked to provide guidance on the preferred strategic direction to allow management to progress detailed planning through FY25.

BACKGROUND
Loy Yang B is a 1,480 MW brown coal power station located in the Latrobe Valley, Victoria, commissioned in 1993. The station operates four generating units of 370 MW each. In FY24, LYB generated 8.4 TWh, representing approximately 7.2% of NEM total generation, and contributed $380 million (65%) of the Generation division's EBITDA of $583 million. The asset employs approximately 600 direct staff and 200 permanent contractors.

The competitive environment for LYB has deteriorated materially since FY21. Renewable energy capacity additions are suppressing daytime wholesale prices, creating a "duck curve" effect with extreme evening price spikes. LYB's baseload generation profile means it earns relatively little from the high-value evening peaks. In FY24, LYB earned an average pool price of $88/MWh versus a system average of $98/MWh, due to its coal cost stack and inability to ramp quickly.

STRATEGIC OPTIONS

OPTION A: CONTINUE OPERATION TO FY2032 (BASE CASE)
Under this option, LYB operates as currently planned to FY2032 or until a natural end-of-life event. NPV analysis under base case carbon price assumptions yields a station NPV of approximately $520 million over the period FY25-FY32. This option requires $180 million of sustaining capex over the period and maintains full employment. Key risks include: accelerated carbon policy tightening reducing NPV by up to $200 million; increasing insurance costs and potential financing restrictions due to ESG policy of major insurers; growing community and investor pressure. Under a high renewable penetration scenario modelled by AEMO's 2024 ISP, LYB's annual generation falls to 6.1 TWh by FY30 and 4.0 TWh by FY32, materially impacting revenue.

OPTION B: ACCELERATED RETIREMENT BY FY2027
Early retirement of LYB by 30 June 2027 would crystallise decommissioning and remediation costs of approximately $420 million (net of scrap value), with workforce transition costs of $45 million. The NPV impact relative to Option A is negative $85 million under base case assumptions, but is positive $65 million under the high carbon price scenario. Early retirement would significantly improve Alinta's ESG profile and may unlock approximately 50-75 bps of financing cost improvement on the Group's $1.4 billion debt facility at next refinancing (estimated FY26). This option requires a detailed FY27 closure plan to be submitted to the Victorian Government by December 2024 under the Latrobe Valley Authority transition framework.

OPTION C: CONVERSION TO GAS COMBINED CYCLE (GAS CCGT)
Technical assessment by Jacobs Engineering indicates that the LYB site could accommodate a 600 MW gas CCGT plant repowering three of the four units, with an estimated capital cost of $900 million. The existing transmission infrastructure, water cooling system, and site would be retained. Gas supply would require a new contract from Bass Strait or Queensland sources. Under gas price assumptions of $9-12/GJ long-term, the NPV of the converted asset over 25 years is approximately $380 million at a 9.5% discount rate. This option would reduce Scope 1 emissions by approximately 80% relative to current operations. Key risks include securing long-term gas supply at acceptable prices and increasing competition from batteries and pumped hydro for dispatchable capacity.

OPTION D: SALE TO A SPECIALIST OPERATOR
An indicative market sounding conducted by Goldman Sachs (October 2024) identified limited acquirer appetite for LYB at acceptable valuation given ESG constraints of major institutional capital pools. The most likely purchaser profile would be a specialist mining or resources company for electricity self-supply, or a private equity vehicle with a managed-wind-down investment thesis. Indicative valuation range from the market sounding was $150-280 million, representing a significant discount to book value. Management does not recommend this option at this time.

FINANCIAL SUMMARY

| Option | NPV (Base) | NPV (High Carbon) | Employment Impact | Capex Required |
|--------|-----------|-------------------|------------------|----------------|
| A: Continue to FY32 | $520M | $320M | No change | $180M |
| B: Early Retirement FY27 | $435M | $385M | 600 redundancies | $420M decommission |
| C: Gas CCGT Conversion | $380M | $520M | 200 net new | $900M |
| D: Sale | $150-280M | N/A | Transfer with asset | Nil |

MANAGEMENT RECOMMENDATION
Management recommends that the Board endorse a phased approach: (1) continue LYB operations in FY25 and FY26 under current plans; (2) authorise management to conduct a detailed FY2027 closure readiness study (budget $2.5 million) commencing Q1 FY25; (3) re-evaluate the options at the March 2025 Board meeting with updated ISP scenario modelling and revised carbon price forecasts. This approach preserves optionality while demonstrating to stakeholders a credible transition pathway.

BOARD DECISIONS SOUGHT
1. Note the strategic options analysis for Loy Yang B Power Station.
2. Endorse management's recommended phased approach to transition planning.
3. Approve $2.5 million budget for FY27 closure readiness study.
4. Note the governance framework for ongoing Board oversight of the LYB transition.

Submitted by: Chief Executive Officer | Chief Strategy Officer
Date: 15 September 2024
""",
        "is_synthetic": True,
        "source_system": "BoardVantage",
    },
    {
        "doc_id": "DOC-003",
        "title": "FY2025 Group Financial Results — Half Year Report (1H FY25)",
        "doc_type": "financial_report",
        "classification": "CONFIDENTIAL",
        "access_tier_level": 2,
        "business_area": "Group",
        "effective_date": date(2025, 2, 28),
        "author": "Chief Financial Officer",
        "version": "v1.0",
        "content": """ALINTA ENERGY GROUP
HALF YEAR FINANCIAL RESULTS — 1H FY2025 (1 JULY 2024 – 31 DECEMBER 2024)

FINANCIAL HIGHLIGHTS

Group revenue for the six months ended 31 December 2024 was $1,618 million, up 4.2% on 1H FY24 ($1,552 million). Underlying EBITDA was $298 million, up 6.4% on prior half ($280 million), representing an EBITDA margin of 18.4% (1H FY24: 18.0%). Underlying NPAT was $101 million, up 12.2% on prior half ($90 million). Operating cash flow was $245 million, supporting continued investment in growth capex.

GENERATION DIVISION
Generation EBITDA: $198 million (1H FY24: $185 million, +7.0%)

Loy Yang B performed strongly in the half, generating 4.6 TWh (1H FY24: 4.4 TWh) and achieving an average pool price of $94/MWh. The unit 3 planned outage in September 2024 was completed in 21 days, three days ahead of schedule and $1.2 million under budget. Unplanned availability was 94.2%, in line with the historical average.

Western Australia generation continued to benefit from capacity cost recovery payments under the new WEM capacity mechanism. Yandin Wind Farm generated 740 GWh in the half, with a capacity factor of 41% (above the P50 production forecast of 38%). Gas generation assets at Newman, Wagerup and Pinjarra contributed $28 million to EBITDA, primarily from capacity payments and merchant gas exposure.

RETAIL DIVISION
Retail EBITDA: $68 million (1H FY24: $72 million, -5.6%)

Retail margin was impacted by elevated wholesale electricity costs in Q1 FY25 (July-September 2024), with the NEM spot price spiking to an average of $145/MWh during the August heat events. Hedging provided partial protection, with the retail book 85% hedged at an average strike of $82/MWh. Customer accounts declined by 18,000 to 1.07 million, primarily due to increased competition from Origin, AGL, and the growing portfolio of smaller new entrants offering solar-optimised tariffs. The Salesforce CRM implementation reached Phase 2 completion in November 2024.

TRADING DIVISION
Trading EBITDA: $24 million (1H FY24: $18 million, +33.3%)

The trading desk outperformed in the half, capitalising on NEM price volatility in Q1 FY25. Structured products and Financial Transmission Rights (FTR) contributed $8 million. The Q2 FY25 book is positioned for continued volatility in the SA-VIC interconnector region.

CORPORATE
Corporate costs: -$62 million (1H FY24: -$65 million, +3.5% improvement)

Cost reduction initiatives delivered $3 million of savings in the half, primarily from procurement renegotiations and headcount efficiency in shared services.

BALANCE SHEET AND CASH FLOW
Net debt at 31 December 2024: $1,385 million (30 June 2024: $1,342 million)
Net Debt / EBITDA: 2.4x (on annualised 1H FY25 EBITDA basis)
Gearing (Net Debt / Total Capital): 38.2%

Capital expenditure in the half totalled $198 million, comprising:
- LYB sustaining capex: $82 million (including Unit 3 planned outage)
- Yandin Stage 2 pre-FID studies: $12 million
- Retail digital transformation: $38 million
- Gas generation sustaining capex: $22 million
- Other / corporate: $44 million

The $600 million syndicated revolving credit facility was refinanced in October 2024 at BBSY + 175 bps, representing a 15 bps improvement on the prior facility, partly attributable to the improved ESG rating from MSCI (upgraded from B to BB in August 2024).

OUTLOOK FOR 2H FY25
Management reaffirms FY25 EBITDA guidance of $590-620 million. Key sensitivities for 2H FY25 include:
- NEM pool price (each $10/MWh movement = approximately $25 million EBITDA)
- Loy Yang B availability (each 1% below plan = approximately $8 million EBITDA)
- Retail customer net adds (target: stabilise customer base by June 2025)
- Timing of Yandin Stage 2 Final Investment Decision (expected Q4 FY25)

Interim dividend declared: 12.5 cents per share (1H FY24: 11.5 cents per share), payable 28 February 2025. This represents a payout ratio of 62% of underlying NPAT.

Prepared by: Chief Financial Officer | Investor Relations
Date: 28 February 2025
""",
        "is_synthetic": True,
        "source_system": "SAP",
    },
    {
        "doc_id": "DOC-004",
        "title": "Competitive Intelligence Report: Australian Retail Energy Market FY2025",
        "doc_type": "competitive_intel",
        "classification": "CONFIDENTIAL",
        "access_tier_level": 2,
        "business_area": "Retail",
        "effective_date": date(2024, 10, 1),
        "author": "Strategy & Market Intelligence",
        "version": "v1.2",
        "content": """ALINTA ENERGY — COMPETITIVE INTELLIGENCE REPORT
AUSTRALIAN RETAIL ENERGY MARKET FY2025

CLASSIFICATION: CONFIDENTIAL — ELT AND ABOVE ONLY

EXECUTIVE OVERVIEW
The Australian retail energy market is undergoing structural change driven by solar penetration, battery adoption, cost-of-living pressures, and digitally native competitors. This report provides Alinta's competitive intelligence assessment across the major retail energy players for FY2025.

MARKET SHARE ANALYSIS (National, Residential + SME)

| Retailer | Market Share | Change YoY | Customer Count |
|----------|-------------|------------|----------------|
| Origin Energy | 24.8% | -0.3% | 4.5M accounts |
| AGL Energy | 22.1% | -0.8% | 4.0M accounts |
| Energy Australia | 15.3% | -0.2% | 2.8M accounts |
| Alinta Energy | 6.0% | -0.2% | 1.07M accounts |
| Momentum Energy | 4.2% | +0.4% | 0.76M accounts |
| Simply Energy | 3.8% | +0.1% | 0.68M accounts |
| Other (100+ retailers) | 23.8% | +1.0% | 4.3M accounts |

KEY COMPETITOR PROFILES

ORIGIN ENERGY
Origin remains the market leader but has been executing a significant transformation programme following its acquisition by Brookfield Asset Management (completed March 2024) and MidOcean Energy. The new ownership has accelerated capital deployment into renewables and batteries. Origin's Eraring Power Station closure (2025) creates significant market supply tightness in NSW, which is expected to elevate NEM pool prices in FY26. Origin's retail business is targeting a 30% reduction in cost-to-serve through its 'Project Nova' AI-driven operations transformation. Alinta should watch for aggressive retail pricing as Origin attempts to maintain market share post-Eraring.

AGL ENERGY
AGL continues its contested transformation following the failed demerger. The company's Generation spin-off plans were abandoned in 2022, but AGL has pivoted to a decarbonisation strategy that commits to coal-free generation by 2035 (revised from 2043). Liddell closure (April 2023) and Bayswater planned closure (2030) define AGL's thermal asset runway. AGL's retail business reported EBITDA margin of 5.2% in FY24, below Alinta's 7.5%, suggesting pricing pressure. AGL's recent launch of 'Energy Intelligence' — an AI-powered usage optimisation product — is garnering positive NPS responses from the market.

ENERGY AUSTRALIA
EA continues to struggle with brand perception following the pandemic-era bill deferral controversies. Its parent CLP Holdings has been exploring strategic options for the Australian business. Market intelligence suggests CLP is not a willing seller at current valuations but is under investor pressure to simplify its portfolio. EA's Mortlake gas peakers in Victoria represent competition for Alinta in the high-value peaking market.

EMERGING DIGITAL COMPETITORS
Several digitally native retailers are taking meaningful share in the 25-44 demographic. Amber Electric (3.2% in key markets), Brighte Energy, and Nectr (parent GreenPower Energy) are all growing on solar-battery arbitrage product propositions. Alinta has no direct equivalent product; management is evaluating a partnership approach with a solar financing provider to close this gap.

CUSTOMER INSIGHT — NET PROMOTER SCORE BENCHMARKING (IBISWorld, Sep 2024)
- Amber Electric: +42
- Momentum Energy: +31
- Simply Energy: +28
- Alinta Energy: +18
- AGL Energy: +12
- Origin Energy: +8
- Energy Australia: +3

Alinta's NPS of +18 is mid-pack but below the digital native disruptors. Key detractors cite billing complexity and difficulty navigating tariff options. The Salesforce CRM upgrade (Phase 2 complete) is expected to address root cause.

REGULATORY ENVIRONMENT
The Albanese Government's 'Energy Bill Relief' extension ($300 rebate per household in FY25) has partially insulated customers from rising wholesale costs but created operational complexity for retailers in administering the rebates. The Australian Energy Regulator's Default Market Offer (DMO) for FY25 was set at approximately $1,850/year in QLD and $2,100/year in NSW (2-4 person household, flat tariff), representing a 5% increase on FY24, providing some retail margin relief.

STRATEGIC IMPLICATIONS FOR ALINTA RETAIL
1. The churn risk from solar-battery customers is the most significant structural threat; Alinta should prioritise a bundled solar-storage-EV product by H1 FY26.
2. Digital acquisition cost ($18 CAC) is significantly below traditional channels ($95 CAC); accelerate digital channel investment.
3. SME segment (350,000 accounts, 28% of retail revenue) is underweight relative to market; targeted SME AI energy advisory service could capture premium positioning.
4. Review pricing architecture for time-of-use tariffs to improve competitiveness with digital native offerings.

Prepared by: Strategy & Market Intelligence | October 2024
""",
        "is_synthetic": True,
        "source_system": "SharePoint",
    },
    {
        "doc_id": "DOC-005",
        "title": "ESG & Climate Risk Report FY2024 — Board Climate Disclosure",
        "doc_type": "board_paper",
        "classification": "CONFIDENTIAL",
        "access_tier_level": 1,
        "business_area": "Group",
        "effective_date": date(2024, 8, 30),
        "author": "Chief Sustainability Officer",
        "version": "v1.0",
        "content": """ALINTA ENERGY GROUP
FY2024 ESG & CLIMATE RISK REPORT — BOARD CLIMATE DISCLOSURE

Prepared in accordance with TCFD Framework and AASB S2 Climate-related Financial Disclosures

GOVERNANCE
The Board oversees climate-related risks and opportunities through its Risk Committee, which met four times in FY24 to review the Group's climate risk position. The Chief Sustainability Officer (CSO) reports directly to the CEO and presents quarterly to the Board Risk Committee. In FY24, the Board approved the Group's updated Net Zero Roadmap committing to Scope 1 and 2 net zero by 2040, with an interim 50% absolute reduction target by 2030 (baseline FY20).

STRATEGY — CLIMATE SCENARIOS
Alinta conducted a robust climate scenario analysis in FY24 using three IPCC-aligned pathways:
- Orderly Transition (1.5°C): Net Zero by 2050, carbon price rising to $150/tCO2 by 2035
- Delayed Transition (2°C): Delayed policy action, carbon price $50/tCO2 by 2030
- Physical Risk Scenario (3-4°C): High physical risk, minimal policy action

Under the Orderly Transition scenario, Loy Yang B faces material financial impact from a carbon price of $50/tCO2 by FY28 (estimated $180 million annual impact at current generation levels). Under the Delayed Transition scenario, the impact is deferred to FY32. Physical risk analysis identified Yandin Wind Farm as exposed to increasing cyclone frequency in WA, with estimated insurance cost increases of 15-25% by 2035. Loy Yang B faces water stress risk from reduced cooling water availability in the Latrobe Valley under a 3-4°C scenario by 2040.

EMISSIONS PERFORMANCE
Scope 1 emissions: 12.4 million tCO2-e (FY24), down 8.2% from FY20 baseline (13.5 million tCO2-e). The reduction is primarily attributable to lower LYB generation volumes and improved generation efficiency.
Scope 2 emissions: 0.18 million tCO2-e (market-based method), reduced 22% from FY20 through renewable energy procurement for corporate operations.
Scope 3 emissions (Category 11, use of sold products): 8.6 million tCO2-e (estimated), reflecting energy sold to retail customers.
Emission Intensity: 0.89 tCO2-e / MWh (FY24, vs 0.91 in FY23 and 1.02 in FY20).

NET ZERO ROADMAP
FY2025-FY2028: LYB transition (expected 7-10 Mt annual reduction depending on closure timing); WA renewables growth (Yandin Stage 2, Oakajee BESS, Merredin Solar)
FY2028-FY2032: Exit brown coal generation entirely; offset remaining gas generation emissions through contracted carbon credits
FY2032-FY2040: Achieve net zero through portfolio decarbonisation and high-quality offset portfolio

FINANCING & ESG RATINGS
MSCI ESG Rating: BB (upgraded from B in August 2024)
Sustainalytics Risk Score: 32.4 (High Risk) — unchanged; primarily driven by brown coal exposure
GRESB Infrastructure Score: 67/100 (above sector median of 61)

The Group's $600 million syndicated revolving credit facility includes a sustainability-linked pricing mechanism tied to: (1) absolute Scope 1 emissions reduction, (2) renewable energy percentage of generation portfolio, and (3) Board gender diversity target (≥40% female). Alinta achieved the gender diversity target in FY24 (42% female directors), contributing to a 5 bps pricing benefit.

NATURE AND BIODIVERSITY
Yandin Wind Farm completed its third annual biodiversity audit in FY24. Bird and bat monitoring confirmed zero Carnaby's Cockatoo fatalities, consistent with FY22 and FY23 results. The site's offset revegetation programme planted 48,000 native species in FY24. Loy Yang B's Hazelwood Pondage rehabilitation programme remains on track.

SOCIAL PERFORMANCE
Total Recordable Injury Frequency Rate (TRIFR): 2.1 per million hours worked (FY24, vs 2.8 in FY23 and 4.1 in FY20) — best ever performance. Lost Time Injury Frequency Rate: 0.4 per million hours worked (FY24 target: <0.5). Indigenous Participation: 3.2% of FY24 recruitment intake identified as Indigenous (target: 5% by FY26). Community investment: $4.8 million in FY24 through the Alinta Foundation and local community programs.

RECOMMENDATIONS TO BOARD
1. Approve updated TCFD disclosure for inclusion in FY24 Annual Report
2. Note management's progress against Net Zero Roadmap interim targets
3. Approve 2025 climate scenario analysis budget of $0.8 million
4. Consider commissioning an independent assessment of Nature-related Financial Disclosures (TNFD) readiness for FY26 disclosure

Date: 30 August 2024
""",
        "is_synthetic": True,
        "source_system": "BoardVantage",
    },
    {
        "doc_id": "DOC-006",
        "title": "WA Renewables Growth Programme — Investment Case (Yandin Stage 2)",
        "doc_type": "board_paper",
        "classification": "RESTRICTED",
        "access_tier_level": 1,
        "business_area": "Generation",
        "effective_date": date(2025, 3, 1),
        "author": "Head of Development | CFO",
        "version": "v2.0",
        "content": """ALINTA ENERGY BOARD
INVESTMENT DECISION PAPER — YANDIN WIND FARM STAGE 2

FOR BOARD APPROVAL — March 2025 Board Meeting

PROPOSED INVESTMENT
Yandin Wind Farm Stage 2: 200 MW wind energy development adjacent to the existing Yandin Stage 1 (400 MW, commissioned 2020) in the Shire of Dandaragan, Western Australia.

Total project capital estimate: $385 million (±10%)
Expected first power: Q2 FY2027
Project IRR: 9.8% (pre-tax, nominal, base case)
NPV at 9.5% WACC: +$28 million (base case); +$65 million (high electricity price)

PROJECT DESCRIPTION
Yandin Stage 2 comprises 50 wind turbine generators (4 MW each) supplied by Vestas (V162-4.5 MW platform, downrated to 4 MW for noise management). The project leverages the existing substation at Yandin Station Road, with a new 132 kV collector circuit connecting to the Western Power Eneabba Terminal. Grid connection approval was received from Western Power in November 2024 (SWIS headroom confirmed at 185 MW firm, 200 MW non-firm). Incremental land agreements have been executed with three pastoral lessees for a 30-year term.

COMMERCIAL STRUCTURE
- WEM Capacity Mechanism: 180 MW certified capacity at BRCP of $219,000/MW/year = $39.4 million per year
- Merchant revenue: 200 MW × 42% CF × 8,760 hrs × $75/MWh average = $55 million per year
- Operating costs: $14/MWh all-in (O&M, insurance, lease, corporate)
- Annual EBITDA contribution: approximately $68 million per year (FY27 onwards)

The project does not require a Power Purchase Agreement due to the WEM Capacity Mechanism providing sufficient revenue floor. Sensitivity analysis indicates the project remains above hurdle rate even if the WEM electricity pool price falls to $55/MWh or the capacity price declines 20% from current levels.

FINANCING
The project will be funded via: (1) Alinta Energy Group balance sheet (equity component $135 million, 35% of total cost); (2) project-level green financing of $250 million at a target rate of BBSY + 185 bps for 18-year tenor. Goldman Sachs has been mandated as green debt advisor; term sheet negotiations are at an advanced stage with three major Australian banks (ANZ, CBA, Macquarie).

CONSTRUCTION EXECUTION
Preferred EPC contractor: Vestas (lump sum $295 million, fixed price, 24-month construction period commencing Q2 FY25 post-FID). Balance of Plant: separate competitive tender process underway, preferred contractor selection expected Q3 FY25. Construction workforce peak: approximately 300 workers; WA First Nations employment target: 8% of construction workforce under the Noongar agreement.

RISK ASSESSMENT
Key project risks and mitigations:
- Grid curtailment risk: Modelled at 4% per annum; Western Power has committed to upgrade Eneabba Terminal by Q1 FY27
- Construction cost escalation: Fixed-price EPC contract with limited liquidated damages carve-outs; contingency of $35 million (10%) included
- WEM regulatory change: Stage 2 capacity declarations locked in for 10 years under existing WEM rules; limited risk to project financials
- Community opposition: No material objections received; environmental approval (EP Act Section 38 referral) expected Q4 FY25

APPROVALS REQUIRED FROM BOARD
1. Approve Final Investment Decision for Yandin Wind Farm Stage 2 (AUD $385 million total project cost)
2. Approve Vestas EPC contract execution (AUD $295 million lump sum)
3. Authorise management to execute project-level green debt facility (AUD $250 million, 18-year tenor)
4. Delegate authority to CEO to approve variations up to $15 million against approved contingency

Submitted by: Head of Asset Development | Chief Financial Officer
Date: 1 March 2025
""",
        "is_synthetic": True,
        "source_system": "BoardVantage",
    },
    {
        "doc_id": "DOC-007",
        "title": "Enterprise Risk Management Framework — FY2025 Update",
        "doc_type": "strategy",
        "classification": "CONFIDENTIAL",
        "access_tier_level": 2,
        "business_area": "Group",
        "effective_date": date(2024, 7, 15),
        "author": "Chief Risk Officer",
        "version": "v3.2",
        "content": """ALINTA ENERGY
ENTERPRISE RISK MANAGEMENT FRAMEWORK — FY2025 UPDATE

EXECUTIVE SUMMARY
This document describes Alinta Energy's Enterprise Risk Management (ERM) Framework for FY2025 and sets out the Group's risk appetite, governance structure, and principal risk categories. The framework is reviewed annually by the Board Risk Committee and approved by the full Board.

RISK GOVERNANCE
The Board retains overall responsibility for risk oversight and sets risk appetite. The Board Risk Committee meets at least four times per year and reviews: the Group Risk Register; material risk movements; risk management effectiveness; and emerging risk horizon scanning. The Chief Risk Officer (CRO) reports to the CEO and has independent access to the Board Risk Committee Chair.

Risk management three lines of defence:
- First Line: Business unit risk owners (operational management, asset teams)
- Second Line: CRO function, ERM team, compliance and legal
- Third Line: Internal Audit (reports directly to Board Audit Committee)

RISK APPETITE STATEMENT
Alinta Energy accepts risk in pursuit of value creation for shareholders and delivery of affordable, reliable energy to customers, subject to the following limits:
- Safety: Zero tolerance for fatalities; LTIFR target <0.5
- Financial: Maximum earnings-at-risk of 15% of annual EBITDA at 95% confidence
- Regulatory: Zero tolerance for material regulatory breaches
- Environmental: Zero tolerance for Category A environmental incidents
- Reputational: No activities that would materially damage Alinta's social licence to operate in key communities

PRINCIPAL RISK CATEGORIES

1. ENERGY TRANSITION RISK
The most material strategic risk for Alinta. Rapid decarbonisation of the Australian energy system threatens the economic life of Loy Yang B and creates both threats and opportunities for the WA portfolio. Carbon price uncertainty is the primary driver of financial exposure in this category.

2. WHOLESALE MARKET RISK
NEM and WEM price volatility creates material earnings risk for both the Generation and Retail businesses. Value-at-Risk (VaR) at 95% confidence, 10-day horizon is managed within a limit of $20 million (Board approved FY25). The Trading Risk Committee monitors trading positions daily.

3. REGULATORY AND POLICY RISK
Australian energy regulation is undergoing the most significant reform in two decades under the National Energy Transformation Partnership. Key regulatory risks include: CER rollout impact on retail margins; Integrated System Plan implementation; WEM reform second tranche; renewable energy zone (REZ) network access rules.

4. CYBER AND INFORMATION SECURITY RISK
Alinta's Operational Technology (OT) environment at LYB and WA generation assets is subject to increasing cyber threat. A SOC2 Type II audit completed in FY24 identified three high-priority findings, all of which have been remediated. The Group increased its cybersecurity budget by 35% in FY25 to $12 million annually.

5. PHYSICAL CLIMATE RISK
Acute and chronic physical climate risks affect Alinta's generation and network assets. Key exposures: LYB cooling water reliability (drought risk); Yandin cyclone exposure; gas infrastructure flood risk (Newman/Pinjarra). Insurance renewal in FY25 saw a 22% premium increase for physical climate risk coverage.

6. SUPPLY CHAIN AND WORKFORCE RISK
Critical spare parts availability for LYB turbines has tightened as the global supply chain for coal plant components contracts. Long lead time items are now managed on a 24-month forward procurement horizon. Workforce risk at LYB relates to skills attrition as uncertainty about the plant's long-term future affects recruitment and retention.

RISK REGISTER SUMMARY (FY25 Top 10 Risks)
1. LYB Transition — Carbon Policy Acceleration (CRITICAL)
2. NEM/WEM Wholesale Price Volatility (HIGH)
3. Retail Customer Churn — Solar/Battery Competition (HIGH)
4. Cyber Attack on OT Infrastructure (HIGH)
5. WEM Regulatory Change — Capacity Mechanism Reform (MEDIUM-HIGH)
6. LYB Unplanned Outage (Major) (MEDIUM-HIGH)
7. Gas Supply Disruption — WA Assets (MEDIUM)
8. Financing Cost Increase — ESG Brownout Risk (MEDIUM)
9. Environmental Incident — LYB Ash Disposal (MEDIUM)
10. Key Person Risk — CEO and CRO Succession (MEDIUM)

Document approved by Board Risk Committee: 15 July 2024
""",
        "is_synthetic": True,
        "source_system": "SharePoint",
    },
    {
        "doc_id": "DOC-008",
        "title": "Regulatory Submission: WEM Capacity Mechanism Review — Alinta Position Paper",
        "doc_type": "regulatory",
        "classification": "INTERNAL",
        "access_tier_level": 3,
        "business_area": "Trading",
        "effective_date": date(2024, 11, 30),
        "author": "Regulatory Affairs",
        "version": "v1.0",
        "content": """ALINTA ENERGY
REGULATORY SUBMISSION — WEM CAPACITY MECHANISM REVIEW
Submitted to the Economic Regulation Authority of Western Australia

30 November 2024

INTRODUCTION
Alinta Energy welcomes the opportunity to provide input to the ERA's review of the Wholesale Electricity Market (WEM) Capacity Mechanism. Alinta is a significant participant in the WEM, operating approximately 980 MW of generation capacity across four sites (Yandin Wind Farm 400 MW, Newman Power Station 180 MW, Wagerup Power Station 220 MW, Pinjarra Power Station 180 MW), and serving approximately 250,000 electricity and gas customers in Western Australia.

EXECUTIVE SUMMARY OF ALINTA'S POSITION
Alinta Energy supports the continued operation of a capacity mechanism in the WEM as an essential tool for ensuring resource adequacy and supporting investment in dispatchable generation. However, we submit that the current Bilateral Reserve Capacity Price (BRCP) structure requires reform to: (1) better reflect the long-run marginal cost of new entrant dispatchable capacity; (2) provide technology-neutral access for demand response, batteries, and virtual power plants; and (3) reduce administrative complexity for smaller participants.

CAPACITY ADEQUACY ASSESSMENT
Alinta's modelling indicates the WEM faces a capacity adequacy challenge in the 2027-2029 period as older thermal plant retires and forecast demand growth from electrification (EV charging, heat pumps, data centres) accelerates. Under AEMO WA's Indicative Capacity Credit calculation, the WEM's reserve margin is projected to decline to 5.8% by FY28 (system standard: 7.7%), creating potential reliability risk. The BRCP must be set at a level sufficient to incentivise new investment in dispatchable resources.

ALINTA'S RECOMMENDED REFORMS
1. BRCP METHODOLOGY: Transition from the current administratively-set BRCP to a competitive auction mechanism (similar to NEM IRPM) within three years, with an interim price cap of $250,000/MW/year to prevent excessive market power exercise.
2. TECHNOLOGY NEUTRALITY: Amend the capacity certification rules to explicitly recognise aggregated battery storage, demand response, and VPP participation on equal footing with traditional generation assets.
3. FORWARD CURVE: Introduce a 3-year forward capacity market to support project financing certainty for new entrant investors, reducing the cost of capital for green energy projects.
4. INTERCONNECTION: Alinta supports the staged development of an East-West interconnector to improve market integration, noting that modelling indicates a 1,000 MW interconnector could reduce WEM capacity costs by approximately $45 million per year.

GAS GENERATION TRANSITION ISSUES
Newman Power Station (commissioned 1981) and Pinjarra Power Station (commissioned 1997) are approaching end of technical life. These assets provide critical firming capacity in the Pilbara and South West Interconnected System respectively. Alinta urges the ERA to ensure the capacity mechanism provides sufficient revenue to incentivise reinvestment decisions in replacement dispatchable capacity at these sites. Without adequate capacity revenue certainty, Alinta may be unable to justify the $120-180 million capital investment required to repower these sites.

CONCLUSION
Alinta Energy is committed to a constructive and long-term role in the WA energy market. We are investing in WA renewables (Yandin Stage 2, proposed Oakajee BESS) and supporting the transition to a clean energy system. The WEM Capacity Mechanism is a critical enabler of this transition and Alinta urges the ERA to implement the recommended reforms on a priority basis.

For enquiries: Director, Regulatory Affairs | Alinta Energy
""",
        "is_synthetic": True,
        "source_system": "SharePoint",
    },
    {
        "doc_id": "DOC-009",
        "title": "FY2026 Budget Paper — Group Financial Plan",
        "doc_type": "financial_report",
        "classification": "RESTRICTED",
        "access_tier_level": 1,
        "business_area": "Group",
        "effective_date": date(2025, 5, 1),
        "author": "Chief Financial Officer",
        "version": "v1.0",
        "content": """ALINTA ENERGY GROUP
FY2026 BUDGET PAPER — GROUP FINANCIAL PLAN

BOARD APPROVAL SOUGHT — May 2025 Board Meeting

FY2026 KEY FINANCIAL TARGETS
Revenue: $3,350 million (+4.7% on FY25 guidance)
EBITDA: $620 million (+5.1%)
EBITDA Margin: 18.5%
NPAT: $215 million (+10.3%)
Capital Expenditure: $480 million
Free Cash Flow: $195 million
Net Debt (30 June 2026): $1,450 million
Leverage (Net Debt / EBITDA): 2.3x

GENERATION BUDGET
Generation EBITDA: $415 million
- Loy Yang B: $385 million (based on 8.6 TWh generation, average pool price $102/MWh, sustaining capex $90 million)
- WA Gas portfolio: $30 million (capacity payments + merchant)
- Yandin Wind Farm Stage 1: $65 million (900 GWh, $72/MWh average net pool + capacity)
- Yandin Stage 2 contribution: nil (first power Q2 FY27)

RETAIL BUDGET
Retail EBITDA: $140 million (up from $135 million FY25 guidance)
Customer accounts target: 1.10 million (net +30,000 from digital growth initiatives)
Cost to serve target: $105/account (down from $115 in FY25, reflecting Salesforce CRM benefits)
Margin per account target: $127/year (FY25: $126)

TRADING BUDGET
Trading EBITDA: $45 million
VaR limit: $20 million (maintained)
New product approvals: Semi-virtual power plant structured products; demand response aggregation

CORPORATE
Corporate costs: -$118 million
IT & Digital Investment (expensed): $38 million
Digital Transformation capitalised capex: $42 million

CAPEX PROGRAMME FY2026
- LYB sustaining capex: $90 million (Unit 2 planned outage in Q3 FY26)
- Yandin Stage 2 construction (equity contribution): $115 million
- Oakajee BESS pre-FID studies: $18 million
- Retail digital transformation: $35 million
- WA gas sustaining: $28 million
- Corporate and other: $32 million
- Contingency: $20 million
TOTAL: $338 million growth/strategic + $118 million sustaining = $480 million total

SENSITIVITIES
- NEM pool price ±$10/MWh: ±$25 million EBITDA
- LYB availability ±1%: ±$8 million EBITDA
- Gas price (WA contracts) ±$1/GJ: ±$3 million EBITDA
- Interest rate ±25 bps: ±$3.5 million finance costs
- AUD/USD ±5c (equipment imports): ±$2 million capex

DIVIDEND GUIDANCE
Board has approved a final FY25 dividend of 16 cents per share (full year: 28.5 cents, payout ratio 66%). FY26 interim dividend guidance: 13 cents per share (to be confirmed at H1 FY26 result).

The FY26 Budget reflects continued execution of the Group's five-year strategy with a focus on managing the LYB transition, investing in WA renewables growth, and rebuilding retail market position through digital leadership.

Submitted for Board approval: 1 May 2025
""",
        "is_synthetic": True,
        "source_system": "SAP",
    },
    {
        "doc_id": "DOC-010",
        "title": "Cybersecurity & OT Security Programme Update — Board Briefing",
        "doc_type": "board_paper",
        "classification": "RESTRICTED",
        "access_tier_level": 1,
        "business_area": "Group",
        "effective_date": date(2024, 12, 1),
        "author": "Chief Information Security Officer",
        "version": "v1.1",
        "content": """ALINTA ENERGY
CYBERSECURITY & OT SECURITY PROGRAMME UPDATE — BOARD BRIEFING

Classification: BOARD RESTRICTED — Not for wider distribution

PURPOSE
This paper provides the Board with an update on Alinta Energy's cybersecurity posture, the FY25 OT Security Uplift Programme, and key cyber incidents from FY24. The Board is asked to note the programme status and approve additional funding of $3.5 million for accelerated OT network segmentation at Loy Yang B.

CYBER THREAT LANDSCAPE
The energy sector remains one of the highest-targeted industries globally for state-sponsored and criminal cyber actors. In FY24, the Australian Cyber Security Centre (ACSC) reported a 23% increase in cyber incidents against critical infrastructure operators, with energy utilities specifically targeted for: business email compromise (BEC); ransomware; and OT-targeted intrusions (Volt Typhoon and similar APT groups). Alinta engaged Mandiant to conduct a threat intelligence review in August 2024. The review assessed Alinta's threat profile as HIGH, primarily due to LYB's status as a critical infrastructure asset with significant potential for national electricity system impact.

FY24 INCIDENTS
Three notable incidents occurred in FY24:
1. Business Email Compromise attempt (September 2024): A vendor impersonation attack targeting Accounts Payable was detected and blocked by Alinta's email security gateway. No financial loss. Post-incident review identified improvements to supplier payment verification processes.
2. Phishing campaign (March 2024): 1,240 phishing emails received; 3 staff clicked links; endpoint detection prevented execution. Security awareness training reinforced.
3. Dark web data exposure (May 2024): Credentials of two Alinta employees found on dark web credential dump from a third-party breach. Passwords reset and MFA enforcement confirmed.

No material operational impact resulted from any FY24 incident. All incidents were reported to the ACSC under the Security of Critical Infrastructure (SOCI) Act 2018 reporting obligations.

OT SECURITY UPLIFT PROGRAMME
The FY25 OT Security Uplift Programme is a $12 million, 18-month programme to materially improve the cybersecurity posture of Alinta's OT environments (LYB, Yandin, Newman, Wagerup, Pinjarra). Programme status at December 2024:

Phase 1 (Complete — $3.8M): OT asset discovery and inventory; Purdue Model reference architecture review; OT SIEM deployment at LYB (Microsoft Sentinel OT).
Phase 2 (In Progress — $4.2M budget): Network segmentation at LYB (firewalls between Level 0-2 OT zones and Level 3 DMZ); Secure remote access replacement (Claroty for vendor remote access). Expected completion: March 2025. ADDITIONAL FUNDING REQUEST: $3.5 million for accelerated full network segmentation across all WA gas generation sites, not originally in scope but assessed as HIGH priority by Mandiant. Board approval sought.
Phase 3 (Planned — $4.0M): OT security monitoring centre integration; annual red team exercises; supply chain security uplift.

BOARD DECISIONS SOUGHT
1. Note the FY24 cyber incident summary and the adequacy of responses.
2. Note the OT Security Uplift Programme progress.
3. Approve $3.5 million supplementary budget for accelerated OT network segmentation at WA gas generation sites.

CISO: | CEO: | Date: 1 December 2024
""",
        "is_synthetic": True,
        "source_system": "BoardVantage",
    },
    {
        "doc_id": "DOC-011",
        "title": "Retail Transformation Programme — Q2 FY25 Progress Report",
        "doc_type": "strategy",
        "classification": "CONFIDENTIAL",
        "access_tier_level": 2,
        "business_area": "Retail",
        "effective_date": date(2024, 12, 31),
        "author": "Head of Retail Transformation",
        "version": "v1.0",
        "content": """ALINTA ENERGY RETAIL
TRANSFORMATION PROGRAMME — Q2 FY25 PROGRESS REPORT (October–December 2024)

PROGRAMME OVERVIEW
The Alinta Retail Transformation Programme is a $85 million, 3-year programme to transform Alinta's retail energy business from a traditional utility model to a digitally-led, customer-centric energy services company. The programme was approved by the Board in July 2023 and commenced in September 2023.

PROGRESS SUMMARY — Q2 FY25
Overall programme status: ON TRACK (RAG: Amber — one workstream behind plan)

WORKSTREAM 1: SALESFORCE CRM MIGRATION (RAG: GREEN)
Phase 1 (billing data migration, 600,000 mass market accounts): COMPLETE — October 2024
Phase 2 (SME migration, 350,000 accounts + enhanced service workflows): COMPLETE — November 2024
Phase 3 (advanced analytics, AI-driven next best action, EV bundle product): In progress. Target: March 2025.
Phase 2 benefits realised: Call handling time reduced by 18% (target: 20%); digital self-service deflection rate improved from 42% to 54% (target: 60%).

WORKSTREAM 2: DIGITAL ACQUISITION (RAG: GREEN)
Digital channel acquisition share: 38% of new customers (target by end FY25: 45%)
Cost of Acquisition (digital): $18 per customer (target: $15 — gap being addressed by SEO/SEM optimisation)
Cost of Acquisition (traditional/call centre): $88 per customer
New product launches in Q2 FY25: (1) Time-of-Use 3.0 tariff (responsive to AEMO 5-minute settlement); (2) AI Energy Advisor beta (300 SME pilot customers)

WORKSTREAM 3: AI ENERGY ADVISOR (RAG: AMBER — BEHIND PLAN)
This workstream aims to deploy an AI-powered energy advisory service for SME customers, providing automated tariff optimisation, demand flexibility recommendations, and solar/battery ROI analysis. The workstream fell 6 weeks behind plan in Q2 due to delayed integration with the AMI data platform. Revised go-live: April 2025 (original: February 2025). Cost impact: $0.6 million additional integration effort, within programme contingency.

WORKSTREAM 4: SOLAR-EV BUNDLE PRODUCT (RAG: AMBER)
Market testing of the Alinta Solar + Battery + EV bundle (branded 'PowerUp') is completing in Q2 FY25 with a 500-customer pilot in Perth. Early NPS: +38 (significantly above Alinta average). Commercial launch deferred to July 2025 pending finalisation of the partner solar financing arrangement (Brighte Finance preferred, commercial terms under negotiation).

FINANCIAL PERFORMANCE
Programme spend to date: $32.4 million (of $85 million total budget, 38%)
FY25 programme spend: $22 million (budget: $24 million, 8% underspend — primarily phasing)
Benefits realised to date: $6.2 million p.a. (annualised) from CRM cost savings
Target benefits run-rate by June 2026: $24 million p.a.

CUSTOMER METRICS
NPS: +22 (Q2 FY25) vs +18 (FY24 full year) — improving trajectory
Customer accounts: 1,072,000 (October 2024), down 8,000 from June 2024 but net adds recovering in December.
Churn rate: 19.8% (Q2 FY25 annualised, vs 22% FY24 full year) — improvement noted.

NEXT QUARTER PRIORITIES (Q3 FY25 — January–March 2025)
- Complete Salesforce Phase 3 (AI next best action engine)
- Launch AI Energy Advisor to full SME base
- Finalise PowerUp (Solar-EV) commercial terms with Brighte
- Commence WA-specific tariff redesign for NEM/WEM convergence customers

Programme Sponsor: Chief Customer Officer | Programme Director: Head of Retail Transformation
""",
        "is_synthetic": True,
        "source_system": "SharePoint",
    },
    {
        "doc_id": "DOC-012",
        "title": "People & Culture Strategy FY2025-FY2027 — Workforce of the Future",
        "doc_type": "strategy",
        "classification": "INTERNAL",
        "access_tier_level": 3,
        "business_area": "Group",
        "effective_date": date(2024, 8, 1),
        "author": "Chief People Officer",
        "version": "v1.0",
        "content": """ALINTA ENERGY
PEOPLE & CULTURE STRATEGY FY2025-FY2027 — WORKFORCE OF THE FUTURE

EXECUTIVE SUMMARY
Alinta Energy's people are its most important asset. This strategy sets out how we will build the workforce capabilities required to navigate the energy transition, deliver excellent customer outcomes, and maintain Alinta's position as an employer of choice in the Australian energy sector.

WORKFORCE CONTEXT
Alinta employs approximately 2,400 FTEs as at 1 July 2024, plus approximately 600 contractors. The workforce is concentrated in three clusters: (1) LYB Operations & Maintenance in the Latrobe Valley (700 FTEs); (2) Retail and Customer Operations in Perth, Adelaide, Brisbane, and Sydney (900 FTEs); (3) Corporate, Trading, and Development in Perth CBD (400 FTEs); (4) WA Generation Operations (400 FTEs).

The strategic context presents significant workforce challenges: LYB's uncertain future creates retention and recruitment challenges; the energy transition requires new skills in renewables, grid technology, and data/AI; the tight labour market for qualified electrical engineers and tradespeople affects all divisions.

STRATEGIC PILLARS

PILLAR 1: WORKFORCE TRANSITION — LYB
The LYB workforce transition is the most significant people challenge in Alinta's history. Alinta has committed to no forced redundancies at LYB before a firm closure date is announced, and has established a dedicated Transition Support Team. Key programmes: (a) Skills mapping and transferability assessment for 700 LYB staff (technical trades transferable to WA renewables and gas sector); (b) Voluntary Early Departure Package available from FY25 (60 expressions of interest received); (c) Latrobe Valley Authority partnership for regional employment pathways; (d) WA Relocation Support Programme for LYB staff willing to relocate to WA (35 expressions of interest).

PILLAR 2: CAPABILITY BUILDING — ENERGY TRANSITION SKILLS
New capability requirements: Renewable energy O&M (wind, solar, BESS); Data analytics and AI; Cybersecurity (OT/IT); Energy markets and derivatives trading; Project delivery (major capital projects).
Programme: Alinta has partnered with the University of Western Australia and Federation University for three tailored upskilling programmes launching in FY25 (200 participants year 1). Annual training spend increased to $3,800/FTE (up 22% from FY23). Graduate programme expanded from 15 to 25 graduates per year with new data science and AI specialisation stream.

PILLAR 3: DIVERSITY & INCLUSION
Target: 40% female leadership by FY27 (current: 36%). Target: 5% Indigenous employees by FY27 (current: 2.8%). Target: 0 gender pay gap at Band 5 and below by FY26 (current: 3.2% gap). Focus on flexible work arrangements post-COVID has resulted in 68% of corporate staff on hybrid arrangements (target: maintain). Mental health: Alinta's EAP utilisation rate of 8.2% is above industry average (5.1%), reflecting strong culture of psychological safety.

PILLAR 4: CULTURE AND ENGAGEMENT
Employee engagement score: 72 (FY24, Gallup Q12 methodology; Australian benchmark: 68). Executive commitment: CEO to conduct quarterly "Town Hall" sessions in all major locations. Values refresh: 'Energise, Connect, Care, Perform' brand refresh launched October 2024.

KEY METRICS FY27 TARGETS
- Voluntary turnover: <12% (FY24: 14.2%)
- Internal mobility rate: >25% of vacancies filled internally (FY24: 19%)
- Female leadership: 40% (FY24: 36%)
- Indigenous employment: 5% (FY24: 2.8%)
- Engagement score: 76+ (FY24: 72)
- LTIFR: <0.3 (FY24: 0.4)

Approved by: Chief People Officer | CEO
Date: 1 August 2024
""",
        "is_synthetic": True,
        "source_system": "SharePoint",
    },
    {
        "doc_id": "DOC-013",
        "title": "Trading & Hedging Strategy Review — FY2025 Annual Update",
        "doc_type": "strategy",
        "classification": "RESTRICTED",
        "access_tier_level": 1,
        "business_area": "Trading",
        "effective_date": date(2024, 7, 1),
        "author": "Head of Energy Trading | CRO",
        "version": "v2.0",
        "content": """ALINTA ENERGY — ENERGY TRADING & RISK MANAGEMENT
FY2025 TRADING AND HEDGING STRATEGY REVIEW

APPROVED BY TRADING RISK COMMITTEE — 1 JULY 2024

EXECUTIVE SUMMARY
This document sets out Alinta Energy's approved trading and hedging strategy for FY2025. The strategy is reviewed annually and approved by the Trading Risk Committee (TRC), comprising the CEO, CFO, CRO, and Head of Energy Trading, with oversight from the Board Risk Committee.

MARKET OUTLOOK FY2025

NEM Wholesale Electricity
AEMO's FY25 outlook indicates continued high price volatility in Q1 (July-September 2024) driven by summer demand peaks and reduced hydro availability in NSW/VIC following below-average inflows. Base case annual average pool price forecasts: VIC $98/MWh; NSW $108/MWh; QLD $88/MWh; SA $115/MWh. Upside risk from potential Callide C Unit 4 extended outage (currently offline since November 2023). Downside risk from strong wind and solar output suppressing daytime prices.

Gas Markets
East Coast gas prices have moderated from FY23 highs, with STTM Adelaide Hub averaging $9.8/GJ in FY24. LNG netback pricing remains the dominant price setter for southern markets. Contract supply for Q1 FY25 is secured at $10.2/GJ for Victorian retail gas hedging requirements. WA gas prices under fixed-price contracts for Alinta's WA generation portfolio.

HEDGING STRATEGY FY2025

GENERATION BOOK (NEM)
LYB's generation output of approximately 8.5 TWh in FY25 is to be hedged as follows:
- Q1 FY25 (Jul-Sep): 90% forward sold at $95/MWh (cap and floor structure)
- Q2 FY25 (Oct-Dec): 75% forward sold at $88/MWh (swaps)
- Q3 FY25 (Jan-Mar): 55% forward sold at $92/MWh (swaps + options)
- Q4 FY25 (Apr-Jun): 35% forward sold at $85/MWh (swaps)
Decreasing hedge ratios in outer quarters reflect diminishing liquidity in the forward curve and desire to capture higher spot prices in shoulder periods.

RETAIL BOOK (NEM)
Retail load of approximately 6.2 TWh in FY25 is hedged with 85-95% coverage for Q1 (summer demand peaks), declining to 70-80% in Q3-Q4. Retail hedge instruments: Fixed-price swaps (60%); Caps at $300/MWh (20%); Collars (15%); Unhedged merchant exposure (5%).

WEM BOOK
WA generation and retail positions are managed through the WEM's bilateral contract market. Key contracts: (1) Synergy hedge for Yandin Stage 1 output ($68/MWh, 30% of generation); (2) 6 C&I supply contracts at average $82/MWh fixed price; (3) Spot market exposure approximately 40% of WEM generation output.

RISK LIMITS FY2025
- Value-at-Risk (VaR): $20 million (95% CI, 10-day holding period) — Board approved
- Stop-loss limit: $8 million (monthly), $15 million (quarterly) — triggers mandatory TRC review
- Counterparty credit exposure limit: $50 million (any single counterparty)
- Structured product position limit: notional $200 million

NEW PRODUCTS APPROVED FY2025
- Semi-virtual power plant (sVPP) products: structured derivatives based on aggregated demand response
- Financial Transmission Rights (FTRs) on SA-VIC and NSW-QLD interconnectors
- Carbon unit forward contracts (ACCU futures via ASX)

PERFORMANCE REVIEW FY24
FY24 EBITDA from Trading: $42 million (budget: $30 million). Key outperformance drivers: (1) Q2 FY24 NEM volatility — unhedged LYB spot exposure during high-price events contributed $8 million; (2) FTR portfolio generated $6 million; (3) ACCU long position contributed $4 million as carbon credit prices rose from $32 to $41/tonne.

Head of Energy Trading | Chief Risk Officer
1 July 2024
""",
        "is_synthetic": True,
        "source_system": "SharePoint",
    },
    {
        "doc_id": "DOC-014",
        "title": "Board Skills Matrix & Governance Review FY2025",
        "doc_type": "board_paper",
        "classification": "RESTRICTED",
        "access_tier_level": 1,
        "business_area": "Group",
        "effective_date": date(2024, 10, 15),
        "author": "Company Secretary | Board Nomination Committee",
        "version": "v1.0",
        "content": """ALINTA ENERGY
BOARD SKILLS MATRIX & GOVERNANCE REVIEW FY2025

BOARD NOMINATION COMMITTEE — October 2025

INTRODUCTION
This paper presents the Board Nomination Committee's annual review of Board composition, skills, and governance practices. The review confirms that Alinta's Board continues to meet the requirements of the ASX Corporate Governance Principles and Recommendations (4th Edition) and the relevant provisions of the Corporations Act 2001.

BOARD COMPOSITION
The Alinta Energy Board comprises 8 Non-Executive Directors (NEDs) including an Independent Chair, and one Executive Director (the CEO). The Board composition as at 1 October 2024:
- Independent Chair: Industry background in energy regulation and infrastructure
- Independent NED (Deputy Chair): Finance and capital markets
- Independent NED: Energy industry executive (renewables focus)
- Independent NED: Digital transformation and technology
- Independent NED: Legal and governance
- Independent NED: ESG and sustainability
- NED (nominee of Hong Kong parent entity): Energy M&A and strategy
- NED (nominee of Hong Kong parent entity): Financial services and risk
- Executive Director / CEO

Board diversity: 4 female directors (44% — exceeds 40% target); 1 director with Indigenous heritage; average tenure 4.3 years; age range 48-72 years.

SKILLS MATRIX ASSESSMENT

| Skill Area | Proficiency Level (Board Average) | Gap Assessment |
|------------|----------------------------------|----------------|
| Energy industry & markets | Advanced | No gap |
| Financial acumen | Advanced | No gap |
| Risk management | Advanced | No gap |
| Digital & technology | Intermediate | Gap noted — see below |
| ESG / climate | Intermediate | No gap |
| Regulatory & government | Intermediate | No gap |
| Capital markets & M&A | Advanced | No gap |
| Operations & safety | Intermediate | Gap noted |
| International markets | Basic | No gap (not material) |
| AI & data science | Basic | PRIORITY GAP |

IDENTIFIED SKILL GAPS
1. AI & Data Science: As Alinta accelerates its digital transformation and AI deployment (including this Executive Decision Studio platform), the Board has limited direct experience with AI systems, data governance, and algorithmic risk. The Nomination Committee recommends recruiting one NED with a profile in applied AI, data science, or technology leadership in FY25.
2. Operational/Technical Leadership: The Board would benefit from a director with direct experience in large-scale infrastructure operations (power station or equivalent). Succession to the current Operations-background NED (retiring June 2025) should prioritise this skillset.

COMMITTEE STRUCTURE AND EFFECTIVENESS
The four standing Board Committees (Audit & Risk; People & Remuneration; Nomination; Safety & Sustainability) were assessed as functioning effectively. Key improvements recommended: (1) Increase Safety & Sustainability Committee frequency from 2 to 4 meetings per year given the LYB closure planning process; (2) Establish a Technology & Cyber ad hoc subcommittee to provide more intensive oversight of the OT security programme.

DIRECTOR SUCCESSION PLANNING
Three NEDs have tenure exceeding six years. The Nomination Committee's succession plan provides for: (1) Non-renewal of one long-tenure NED at the October 2025 AGM; (2) External search for AI/technology NED (mandate to be issued January 2025); (3) Internal review of Deputy Chair succession for FY27.

BOARD EVALUATION
The annual Board evaluation (conducted by Spencer Stuart) found overall Board effectiveness at 7.6 / 10 (FY24: 7.3 / 10). Areas of highest performance: strategy oversight; financial rigour; risk culture. Areas for improvement: forward-looking technology horizon scanning; diversity of thought in decision-making; meeting time allocation between compliance matters and strategic discussion.

Submitted by: Board Nomination Committee Chair
Date: 15 October 2024
""",
        "is_synthetic": True,
        "source_system": "BoardVantage",
    },
    {
        "doc_id": "DOC-015",
        "title": "Capital Allocation Framework & Dividend Policy — Board Approval",
        "doc_type": "board_paper",
        "classification": "RESTRICTED",
        "access_tier_level": 1,
        "business_area": "Group",
        "effective_date": date(2025, 1, 15),
        "author": "Chief Financial Officer",
        "version": "v1.2",
        "content": """ALINTA ENERGY
CAPITAL ALLOCATION FRAMEWORK & DIVIDEND POLICY — BOARD APPROVAL

FOR BOARD APPROVAL — January 2025 Board Meeting

EXECUTIVE SUMMARY
This paper presents Alinta Energy's updated Capital Allocation Framework (CAF) for Board approval. The framework has been revised to reflect: (1) the updated strategic plan incorporating WA renewables growth; (2) the evolving LYB transition scenario; and (3) feedback from institutional investors at the November 2024 investor day. The Board is asked to approve the updated framework and confirm the progressive dividend policy.

CAPITAL ALLOCATION HIERARCHY
Alinta's capital allocation priorities, in order, are:

1. MAINTAIN FINANCIAL RESILIENCE (non-discretionary)
- Maintain Net Debt / EBITDA below 3.5x at all times
- Maintain minimum liquidity of $300 million (cash + undrawn facilities)
- Fund sustaining capex requirements to maintain safe, reliable operations
- Meet all regulatory and compliance capital requirements

2. INVEST IN VALUE-CREATING GROWTH (discretionary)
- Fund growth projects exceeding 9.5% pre-tax WACC hurdle rate
- Priority 1: WA Renewables (Yandin Stage 2, Oakajee BESS, Merredin Solar) — high-return, ESG-aligned
- Priority 2: Retail Digital Transformation — defensive investment to protect retail market position
- Priority 3: Trading capability — incremental, capital-light growth
- Growth capex ceiling: $200 million per year without Board approval; projects > $50 million require Board approval

3. RETURN CAPITAL TO SHAREHOLDERS (discretionary)
- Progressive ordinary dividend: 50-70% of underlying NPAT payout ratio
- Special dividends / buybacks when Net Debt / EBITDA < 2.0x and no higher-return internal uses

DIVIDEND POLICY
The Board has approved a progressive ordinary dividend policy targeting 50-70% NPAT payout ratio with year-on-year growth in ordinary DPS (absent extraordinary circumstances). FY25 guidance: total dividend of 28-30 cents per share (FY24: 26 cents), representing 60-65% NPAT payout.

WACC AND HURDLE RATES
Group WACC: 9.5% (pre-tax, nominal)
- Renewable energy projects in WA: WACC 9.0% (lower risk profile, regulated-like revenue)
- Thermal generation (LYB sustaining): WACC 12.0% (risk premium for carbon/regulatory risk)
- Retail investments: WACC 10.5%
- Trading: WACC 11.0%

All new growth investments presented to the Board must include: base case NPV, upside/downside sensitivity range, strategic rationale, risk assessment, and ESG impact assessment.

BALANCE SHEET MANAGEMENT
Target leverage range: Net Debt / EBITDA of 2.0x-3.0x
- Below 2.0x: Excess capital returned to shareholders or deployed into bolt-on M&A
- 2.0x-3.0x: Preferred operating range; normal capital allocation applies
- 3.0x-3.5x: Growth capex paused until leverage returns to 3.0x; dividend maintained
- Above 3.5x: Board immediate review; potential dividend reduction; equity capital raise considered

Credit rating target: Maintain Baa2 / BBB equivalent (Moody's / S&P) to preserve access to investment-grade debt markets and sustainability-linked financing.

SHAREHOLDER RETURNS ANALYSIS
Over the FY22-FY24 period, Alinta returned $380 million to shareholders via: ordinary dividends ($280 million); special dividend ($60 million, FY23); share buyback ($40 million, FY22). At current leverage of 2.4x, the Board has appetite for continued progressive dividends and notes that, subject to the Yandin Stage 2 FID, the Group would have capacity for an additional special dividend of $50-80 million in FY26 if the WA project financing is executed as planned.

Board approval: Capital Allocation Framework effective 1 January 2025
""",
        "is_synthetic": True,
        "source_system": "BoardVantage",
    },
]

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, DateType, TimestampType

doc_rows = []
for d in documents:
    doc_rows.append(Row(
        doc_id=d["doc_id"],
        title=d["title"],
        doc_type=d["doc_type"],
        classification=d["classification"],
        access_tier_level=d["access_tier_level"],
        business_area=d["business_area"],
        effective_date=d["effective_date"],
        author=d["author"],
        version=d["version"],
        content=d["content"],
        is_synthetic=d["is_synthetic"],
        source_system=d["source_system"],
        created_at=datetime.utcnow(),
    ))

docs_df = spark.createDataFrame(doc_rows)
docs_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.eds_synthetic.documents")
print(f"[OK] documents: {docs_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Financial Data (FY24-FY27, monthly, 4 business units)

# COMMAND ----------

import itertools

business_units = {
    "Retail": {
        "annual_revenue": 900.0,
        "annual_ebitda": 135.0,
        "annual_capex": 45.0,
        "annual_opex": 765.0,
    },
    "Generation": {
        "annual_revenue": 1200.0,
        "annual_ebitda": 380.0,
        "annual_capex": 160.0,
        "annual_opex": 820.0,
    },
    "Trading": {
        "annual_revenue": 200.0,
        "annual_ebitda": 42.0,
        "annual_capex": 5.0,
        "annual_opex": 158.0,
    },
    "Corporate": {
        "annual_revenue": 0.0,
        "annual_ebitda": -150.0,
        "annual_capex": 30.0,
        "annual_opex": 150.0,
    },
}

# FY = July-June; FY24 = Jul 2023 - Jun 2024
fiscal_years = [2024, 2025, 2026, 2027]
data_types = ["actuals", "budget", "forecast"]

financial_rows = []

def get_fy_quarter(month):
    # FY quarter (Jul=Q1, Oct=Q2, Jan=Q3, Apr=Q4)
    offset = (month - 7) % 12
    return (offset // 3) + 1

def get_fy(year, month):
    return year + 1 if month >= 7 else year

for fy in fiscal_years:
    # FY runs Jul (fy-1) to Jun (fy)
    months = []
    for m in range(7, 13):
        months.append(date(fy - 1, m, 1))
    for m in range(1, 7):
        months.append(date(fy, m, 1))

    for bu_name, bu_params in business_units.items():
        for dt in data_types:
            # Skip forecast for past FYs, actuals for far future
            if fy < 2026 and dt == "forecast":
                continue
            if fy > 2025 and dt == "actuals":
                continue

            for period in months:
                # Monthly base = annual / 12 with seasonal variance
                month_idx = period.month
                # Revenue seasonality: higher in summer (Jan-Feb) and winter (Jun-Jul)
                seasonal_factor = 1.0
                if bu_name == "Retail":
                    if month_idx in [1, 2, 6, 7, 8]:
                        seasonal_factor = 1.12
                    elif month_idx in [3, 4, 9, 10]:
                        seasonal_factor = 0.92
                elif bu_name == "Generation":
                    if month_idx in [1, 2, 6, 7, 8]:
                        seasonal_factor = 1.18
                    elif month_idx in [4, 5, 10, 11]:
                        seasonal_factor = 0.85

                noise = 1 + random.gauss(0, 0.04)
                budget_variance = 1.0 if dt == "actuals" else (1 + random.gauss(0, 0.015))

                base_rev = bu_params["annual_revenue"] / 12 * seasonal_factor * noise * budget_variance
                base_ebitda = bu_params["annual_ebitda"] / 12 * seasonal_factor * noise * budget_variance
                base_capex = bu_params["annual_capex"] / 12 * (1 + random.gauss(0, 0.1))
                base_opex = bu_params["annual_opex"] / 12 * seasonal_factor * noise * budget_variance

                # Net debt: grows with capex, reduces with cash flow
                base_net_debt = 1350.0 + (fy - 2024) * 50 + random.gauss(0, 20)
                base_cf = base_ebitda * 0.75 - base_capex / 4

                fy_actual = get_fy(period.year, period.month)
                fq = get_fy_quarter(period.month)

                financial_rows.append(Row(
                    id=str(uuid.uuid4()),
                    business_unit=bu_name,
                    period=period,
                    fiscal_year=fy_actual,
                    fiscal_quarter=fq,
                    revenue=round(max(base_rev, 0), 2),
                    ebitda=round(base_ebitda, 2),
                    capex=round(max(base_capex, 0), 2),
                    opex=round(max(base_opex, 0), 2),
                    net_debt=round(max(base_net_debt, 0), 2),
                    cash_flow=round(base_cf, 2),
                    data_type=dt,
                    currency="AUD",
                    created_at=datetime.utcnow(),
                ))

fin_df = spark.createDataFrame(financial_rows)
fin_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.eds_synthetic.financial_data")
print(f"[OK] financial_data: {fin_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. KPI Time Series

# COMMAND ----------

kpi_definitions = [
    {"kpi_id": "KPI-001", "kpi_name": "LYB Plant Availability Factor", "category": "operational", "business_unit": "Generation", "asset_name": "Loy Yang B Power Station", "unit": "%", "target": 93.0, "lower": 88.0, "upper": 99.0, "base_val": 93.5, "std": 2.5},
    {"kpi_id": "KPI-002", "kpi_name": "Yandin Capacity Factor", "category": "operational", "business_unit": "Generation", "asset_name": "Yandin Wind Farm", "unit": "%", "target": 38.0, "lower": 25.0, "upper": 52.0, "base_val": 40.0, "std": 6.0},
    {"kpi_id": "KPI-003", "kpi_name": "Group LTIFR", "category": "safety", "business_unit": "Group", "asset_name": None, "unit": "per_mhw", "target": 0.5, "lower": 0.0, "upper": 1.5, "base_val": 0.45, "std": 0.12},
    {"kpi_id": "KPI-004", "kpi_name": "Retail Customer NPS", "category": "customer", "business_unit": "Retail", "asset_name": None, "unit": "score", "target": 25.0, "lower": 5.0, "upper": 50.0, "base_val": 20.0, "std": 4.0},
    {"kpi_id": "KPI-005", "kpi_name": "Group EBITDA Margin", "category": "financial", "business_unit": "Group", "asset_name": None, "unit": "%", "target": 18.0, "lower": 14.0, "upper": 24.0, "base_val": 18.2, "std": 1.5},
    {"kpi_id": "KPI-006", "kpi_name": "Net Debt to EBITDA", "category": "financial", "business_unit": "Group", "asset_name": None, "unit": "x", "target": 2.5, "lower": 1.5, "upper": 3.5, "base_val": 2.4, "std": 0.2},
    {"kpi_id": "KPI-007", "kpi_name": "Retail Customer Churn Rate", "category": "customer", "business_unit": "Retail", "asset_name": None, "unit": "%", "target": 18.0, "lower": 10.0, "upper": 28.0, "base_val": 21.0, "std": 2.5},
    {"kpi_id": "KPI-008", "kpi_name": "Group Scope 1 Emissions Intensity", "category": "ESG", "business_unit": "Group", "asset_name": None, "unit": "tCO2e_MWh", "target": 0.87, "lower": 0.70, "upper": 1.05, "base_val": 0.89, "std": 0.03},
    {"kpi_id": "KPI-009", "kpi_name": "WEM Yandin Pool Revenue", "category": "financial", "business_unit": "Generation", "asset_name": "Yandin Wind Farm", "unit": "AUD_M", "target": 25.0, "lower": 15.0, "upper": 40.0, "base_val": 26.0, "std": 4.0},
    {"kpi_id": "KPI-010", "kpi_name": "Retail Cost to Serve per Account", "category": "financial", "business_unit": "Retail", "asset_name": None, "unit": "AUD", "target": 110.0, "lower": 90.0, "upper": 140.0, "base_val": 115.0, "std": 6.0},
    {"kpi_id": "KPI-011", "kpi_name": "LYB Forced Outage Rate", "category": "operational", "business_unit": "Generation", "asset_name": "Loy Yang B Power Station", "unit": "%", "target": 3.0, "lower": 0.0, "upper": 15.0, "base_val": 3.5, "std": 2.8},
    {"kpi_id": "KPI-012", "kpi_name": "Retail Digital Acquisition Share", "category": "customer", "business_unit": "Retail", "asset_name": None, "unit": "%", "target": 40.0, "lower": 20.0, "upper": 60.0, "base_val": 32.0, "std": 3.0},
]

# Monthly from Jan 2024 to Dec 2026
start = date(2024, 1, 1)
end = date(2026, 12, 1)
periods = []
d = start
while d <= end:
    periods.append(d)
    d = d + relativedelta(months=1)

kpi_rows = []
for kdef in kpi_definitions:
    val = kdef["base_val"]
    trend = 0.0
    if kdef["kpi_id"] in ["KPI-004", "KPI-012"]:  # NPS, Digital share - improving
        trend = 0.3
    elif kdef["kpi_id"] == "KPI-007":  # Churn - decreasing
        trend = -0.15
    elif kdef["kpi_id"] == "KPI-008":  # Emissions - decreasing
        trend = -0.002
    elif kdef["kpi_id"] == "KPI-010":  # Cost to serve - decreasing
        trend = -0.5

    for i, period in enumerate(periods):
        val += trend + random.gauss(0, kdef["std"] * 0.15)
        # Add occasional anomalies
        is_anomaly = False
        if random.random() < 0.04:
            val += random.choice([-1, 1]) * kdef["std"] * 2.5
            is_anomaly = True
        val = max(kdef["lower"], min(kdef["upper"], val))
        kpi_rows.append(Row(
            kpi_id=kdef["kpi_id"],
            kpi_name=kdef["kpi_name"],
            category=kdef["category"],
            business_unit=kdef["business_unit"],
            asset_name=kdef["asset_name"],
            period=period,
            value=round(val, 3),
            unit=kdef["unit"],
            target=kdef["target"],
            lower_threshold=kdef["lower"],
            upper_threshold=kdef["upper"],
            is_anomaly=is_anomaly,
            created_at=datetime.utcnow(),
        ))

kpi_df = spark.createDataFrame(kpi_rows)
kpi_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.eds_synthetic.kpi_timeseries")
print(f"[OK] kpi_timeseries: {kpi_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Risk Register (50 items)

# COMMAND ----------

risk_categories = {
    "regulatory": [
        ("Carbon price escalation beyond modelled scenarios reduces LYB economic life by 3-5 years", "Likely", "Catastrophic", "Critical", 20, "CEO/CFO"),
        ("AEMO 2025 ISP requires accelerated REZ transmission investment ahead of Alinta's WA renewables timeline", "Possible", "Major", "High", 15, "Head of Regulatory"),
        ("WEM Capacity Mechanism reform reduces capacity revenue below project hurdle rates", "Possible", "Major", "High", 12, "Head of Trading"),
        ("Victorian Government imposes mandatory LYB closure date before FY2030", "Unlikely", "Catastrophic", "High", 14, "CEO"),
        ("AER Default Market Offer reduction compresses retail margins below 5%", "Possible", "Moderate", "Medium", 9, "CEO Retail"),
        ("SOCI Act expanded obligations increase OT security compliance costs by $5M+", "Likely", "Minor", "Medium", 8, "CISO"),
        ("National Energy Transformation Partnership requires accelerated network decarbonisation", "Likely", "Moderate", "Medium", 10, "Head of Regulatory"),
        ("Environmental Protection Act review imposes new LYB ash disposal conditions", "Possible", "Moderate", "Medium", 9, "COO Generation"),
        ("Privacy Act reforms increase data management obligations and breach penalty exposure", "Likely", "Minor", "Medium", 7, "General Counsel"),
    ],
    "market": [
        ("NEM renewable energy oversupply suppresses pool prices below $70/MWh by FY27", "Possible", "Major", "High", 15, "Head of Trading"),
        ("Retail customer churn accelerates to >25% due to solar-battery competition", "Likely", "Major", "High", 16, "CEO Retail"),
        ("LNG price spike raises east coast gas costs to $14+/GJ, increasing LYB fuel costs", "Unlikely", "Major", "Medium", 10, "CFO"),
        ("Origin Energy aggressive retail pricing post-Eraring closure drives market share loss", "Likely", "Moderate", "Medium", 10, "CEO Retail"),
        ("WEM interconnection to NEM reduces WA capacity payments", "Unlikely", "Major", "Medium", 10, "Head of Trading"),
        ("New digital-native retail entrant acquires 200,000+ Alinta customers within 18 months", "Possible", "Major", "High", 12, "CEO Retail"),
        ("Carbon credit (ACCU) price falls 40% reducing trading portfolio value", "Possible", "Moderate", "Medium", 9, "Head of Trading"),
        ("Yandin Stage 2 electricity prices average $60/MWh vs $75/MWh forecast", "Possible", "Major", "High", 12, "CFO"),
        ("AGL or Origin acquires a digital retail platform and rapidly gains share", "Possible", "Moderate", "Medium", 8, "CEO"),
    ],
    "operational": [
        ("LYB Unit 1 major unplanned outage (>60 days) during summer peak", "Possible", "Major", "High", 15, "COO Generation"),
        ("Yandin turbine major component failure (gearbox/blade) requiring 6+ month repair", "Unlikely", "Moderate", "Medium", 8, "COO Generation"),
        ("LYB coal supply disruption (mine conveyor failure) reduces generation output 25%", "Possible", "Major", "High", 12, "COO Generation"),
        ("Newman Power Station cooling tower failure requires 3-month repair", "Unlikely", "Moderate", "Medium", 6, "COO Generation"),
        ("Salesforce CRM Phase 3 failure disrupts retail operations for 2 weeks", "Unlikely", "Moderate", "Medium", 7, "CEO Retail"),
        ("Gas pipeline rupture affecting Wagerup or Pinjarra supply", "Rare", "Major", "Medium", 8, "COO Generation"),
        ("Critical spare parts unavailability delays LYB outage return by 30+ days", "Possible", "Moderate", "Medium", 9, "COO Generation"),
        ("Safety incident — Class A environmental at LYB ash pond", "Rare", "Catastrophic", "High", 14, "COO Generation"),
        ("Yandin road access flooding during construction of Stage 2", "Unlikely", "Minor", "Low", 4, "Head of Development"),
        ("WA gas market supply curtailment event during extreme heat period", "Rare", "Major", "Medium", 10, "COO Generation"),
    ],
    "ESG": [
        ("LYB Scope 1 emissions exceed FY25 Net Zero Roadmap interim target", "Possible", "Major", "High", 12, "CSO"),
        ("Institutional investor divestment campaign targets Alinta over LYB coal exposure", "Likely", "Moderate", "Medium", 10, "CFO"),
        ("Yandin Wind Farm bird strike triggers environmental remediation requirement", "Unlikely", "Moderate", "Medium", 6, "COO Generation"),
        ("Gender pay gap audit reveals Band 3 and 4 structural inequality", "Possible", "Minor", "Low", 4, "CPO"),
        ("LYB workforce community unrest if transition timeline not communicated clearly", "Possible", "Major", "High", 12, "CPO/CEO"),
        ("Sustainalytics downgrade increases financing costs on ESG-linked facilities by 20 bps", "Possible", "Moderate", "Medium", 9, "CFO"),
        ("Greenwashing allegation relating to Alinta's net zero marketing claims", "Unlikely", "Major", "Medium", 10, "CMO/General Counsel"),
        ("TNFD biodiversity disclosure obligations require material Yandin site remediation", "Unlikely", "Moderate", "Medium", 6, "CSO"),
    ],
    "cyber": [
        ("Ransomware attack on LYB OT environment causes multi-day generation outage", "Possible", "Catastrophic", "Critical", 20, "CISO"),
        ("State-sponsored APT attack on Alinta corporate network — data exfiltration", "Possible", "Major", "High", 15, "CISO"),
        ("BEC fraud — successful vendor impersonation payment fraud >$5M", "Possible", "Major", "High", 12, "CISO/CFO"),
        ("Customer data breach exposes >100,000 retail customer records", "Unlikely", "Major", "High", 12, "CISO"),
        ("IT system outage during NEM high price event prevents optimal dispatch", "Unlikely", "Major", "Medium", 10, "CTO"),
        ("Third-party software supply chain compromise (SolarWinds-type)", "Unlikely", "Major", "Medium", 10, "CISO"),
        ("Critical OT vulnerability in LYB SCADA system actively exploited", "Rare", "Catastrophic", "Critical", 18, "CISO"),
    ],
    "financial": [
        ("Interest rate increase to 6%+ extends Alinta leverage above 3.5x EBITDA", "Unlikely", "Major", "Medium", 10, "CFO"),
        ("AUD/USD depreciation increases LYB capex costs by 15%+ (imported spares)", "Possible", "Minor", "Low", 5, "CFO"),
        ("Yandin Stage 2 construction cost overrun of >15% vs fixed-price EPC", "Unlikely", "Major", "Medium", 10, "CFO"),
        ("Rating agency downgrade to sub-investment-grade restricts financing options", "Rare", "Catastrophic", "High", 14, "CFO"),
        ("Counterparty default on major NEM hedge contract (>$50M notional)", "Rare", "Major", "Medium", 8, "Head of Trading"),
        ("Defined benefit superannuation fund deficit crystallises", "Rare", "Moderate", "Low", 5, "CFO"),
        ("LYB asset impairment of $300M+ required due to early closure decision", "Possible", "Major", "High", 12, "CFO"),
    ],
}

statuses = ["open", "in_progress", "accepted"]
mitigations_templates = {
    "regulatory": ["Active regulatory engagement programme; submissions to all relevant consultations", "Scenario analysis in annual strategy review; hedge strategies in place", "Legal review of regulatory changes; proactive government engagement"],
    "market": ["Hedging programme provides 80%+ short-term coverage; retail tariff flexibility", "Digital transformation programme accelerating competitive positioning", "Portfolio diversification reducing single-market exposure"],
    "operational": ["Preventive maintenance programme; critical spare parts stockholding increased", "Redundant systems in place; business continuity plan tested quarterly", "Engineering assessments completed; remediation plan in place"],
    "ESG": ["Net Zero Roadmap with interim milestones; third-party verification", "Stakeholder engagement programme; transparent disclosure framework", "ESG-linked financing structure aligning incentives"],
    "cyber": ["OT Security Uplift Programme ($12M, 18 months); Mandiant engagement; SOC monitoring", "Multi-factor authentication; zero trust network access; employee awareness training", "Incident response plan tested bi-annually; cyber insurance ($100M) in place"],
    "financial": ["Conservative leverage target (2.0-3.0x); revolving credit facility headroom $300M+", "Interest rate hedging; FX forward contracts for major capex items", "Stress testing at 150% cost overrun; fixed-price EPC contract in place"],
}

risk_rows = []
risk_idx = 1
review_base = date(2025, 3, 1)

for cat, risks in risk_categories.items():
    mitigations = mitigations_templates[cat]
    for risk_desc, likelihood, consequence, rating, score, owner in risks:
        review = review_base + relativedelta(months=random.randint(0, 6))
        risk_rows.append(Row(
            risk_id=f"RISK-{risk_idx:03d}",
            category=cat,
            description=risk_desc,
            likelihood=likelihood,
            consequence=consequence,
            rating=rating,
            risk_score=score,
            owner=owner,
            mitigation=random.choice(mitigations),
            status=random.choice(statuses),
            review_date=review,
            created_at=datetime.utcnow(),
        ))
        risk_idx += 1

risk_df = spark.createDataFrame(risk_rows)
risk_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.eds_synthetic.risk_register")
print(f"[OK] risk_register: {risk_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Action Items (100 items)

# COMMAND ----------

meetings = [
    "Board Meeting Sep-2024", "Board Meeting Oct-2024", "Board Meeting Nov-2024",
    "Board Meeting Dec-2024", "ELT Meeting Oct-2024", "ELT Meeting Nov-2024",
    "ELT Meeting Dec-2024", "ELT Meeting Jan-2025", "Risk Committee Oct-2024",
    "Risk Committee Dec-2024", "Investment Committee Nov-2024", "Safety & Sustainability Committee Aug-2024",
    "Trading Risk Committee Sep-2024", "People & Remuneration Committee Oct-2024", "Audit Committee Sep-2024",
]

owners = [
    "CEO", "CFO", "COO Generation", "CEO Retail", "Head of Strategy", "CISO", "CRO",
    "CSO", "CPO", "Head of Trading", "Head of Development", "Head of Regulatory",
    "General Counsel", "CTO", "Head of Finance",
]

action_templates = [
    ("Commission FY2027 LYB closure readiness study through Jacobs Engineering", "critical"),
    ("Finalise Yandin Stage 2 EPC contract with Vestas and present to Board", "critical"),
    ("Complete OT network segmentation at all WA gas generation sites", "high"),
    ("Launch AI Energy Advisor product to full SME customer base", "high"),
    ("Conduct regulatory engagement on WEM Capacity Mechanism reform", "high"),
    ("Present updated LYB transition NPV analysis to Risk Committee", "critical"),
    ("Finalise Oakajee BESS pre-FID feasibility study", "high"),
    ("Complete Salesforce CRM Phase 3 implementation", "high"),
    ("Review and update cyber incident response plan", "high"),
    ("Engage Goldman Sachs on Yandin Stage 2 green debt mandate", "critical"),
    ("Commission independent TNFD readiness assessment", "medium"),
    ("Prepare AASB S2 climate disclosure for FY24 Annual Report", "high"),
    ("Recruit AI/Technology NED candidate for Board succession", "high"),
    ("Implement enhanced daily VaR reporting to CFO", "medium"),
    ("Complete Latrobe Valley workforce transition survey", "high"),
    ("Negotiate Brighte Finance terms for PowerUp solar-EV bundle", "high"),
    ("Update Group insurance programme for physical climate risk", "medium"),
    ("Review and update WACC assumptions with external benchmark", "medium"),
    ("Submit WEM Capacity Mechanism review regulatory submission", "high"),
    ("Complete LYB Unit 2 planned outage preparation checklist", "high"),
    ("Implement Financial Transmission Rights trading programme", "medium"),
    ("Develop ACCU portfolio strategy for FY26", "medium"),
    ("Prepare Board paper on gas CCGT conversion feasibility study", "high"),
    ("Update retail tariff architecture for time-of-use 3.0", "medium"),
    ("Commission Merredin Solar Farm site feasibility study", "medium"),
    ("Establish Technology & Cyber Board subcommittee terms of reference", "medium"),
    ("Review key person succession plan for CEO and CRO roles", "high"),
    ("Finalise Noongar employment agreement for Yandin Stage 2", "high"),
    ("Update Enterprise Risk Management Framework for FY26", "medium"),
    ("Implement gender pay equity remediation for Band 3-4", "medium"),
    ("Launch graduate programme data science/AI specialisation stream", "medium"),
    ("Complete LYB ash pond environmental audit FY25", "high"),
    ("Negotiate coal supply agreements for LYB FY26-FY27", "high"),
    ("Review and update Trading Risk limits for FY26", "medium"),
    ("Prepare investor day materials on transition strategy", "high"),
    ("Commission Bass Strait gas supply pricing assessment for CCGT", "medium"),
    ("Implement Yandin bird monitoring enhanced protocol", "low"),
    ("Complete anti-money laundering compliance review (Trading)", "medium"),
    ("Deploy AI-powered customer churn prediction model in CRM", "high"),
    ("Engage KPMG for FY25 sustainability assurance", "medium"),
    ("Prepare LYB decommissioning and remediation cost estimate", "high"),
    ("Review board meeting cadence for LYB transition oversight", "medium"),
    ("Update business continuity plan for cyber outage scenario", "high"),
    ("Negotiate refinancing terms for $600M revolving credit facility", "critical"),
    ("Submit MSCI ESG data update for annual rating review", "medium"),
    ("Present Q3 FY25 trading portfolio performance to Risk Committee", "medium"),
    ("Assess WA grid curtailment risk for Yandin Stage 2 PPA terms", "high"),
    ("Deploy real-time OT threat intelligence feed at LYB", "high"),
    ("Review D&O insurance coverage post-TCFD mandatory disclosure", "medium"),
    ("Finalise FY26 capex programme and present to Board", "high"),
    ("Develop SME targeted energy advisory product proposal", "medium"),
    ("Review critical spare parts inventory for LYB FY26 outage", "high"),
    ("Update ESG-linked KPI targets in revolving credit facility", "medium"),
    ("Commission independent LYB structural integrity assessment", "high"),
    ("Evaluate Merredin Solar Farm land access agreements", "medium"),
    ("Prepare Board paper: East-West interconnector strategic implications", "medium"),
    ("Complete FY25 TRIFR target remediation programme", "medium"),
    ("Update whistleblower policy for FY25 regulatory changes", "low"),
    ("Prepare LYB transition FAQ for Latrobe Valley community", "medium"),
    ("Assess impact of 5-minute settlement on retail portfolio risk", "high"),
    ("Develop FY26 sustainability targets for Board approval", "medium"),
    ("Review financial model for Pinjarra Power Station repowering", "medium"),
    ("Engage with Victorian Government on LYB transition support package", "high"),
    ("Update conflict of interest register for all Board members", "low"),
    ("Complete mandatory SOCI Act sector risk assessment", "high"),
    ("Commission Yandin Stage 2 environmental approval Section 38 referral", "high"),
    ("Prepare half-year results analyst briefing materials", "high"),
    ("Review and update Climate Action Plan for TCFD alignment", "high"),
    ("Assess regulatory implications of AGL Liddell site for LYB planning", "medium"),
    ("Implement enhanced Accounts Payable verification controls", "high"),
    ("Develop VPP product commercial terms for retail launch", "medium"),
    ("Update Group-wide data classification and handling policy", "medium"),
    ("Complete employee engagement survey FY25 and present results", "medium"),
    ("Review LYB coal ash utilisation options (construction materials)", "low"),
    ("Prepare Board briefing on AEMO 2025 Integrated System Plan", "high"),
    ("Negotiate WEM bilateral contract with Synergy for Yandin Stage 2", "high"),
    ("Develop AI governance framework for Executive Decision Studio", "high"),
    ("Complete Newman Power Station condition assessment", "medium"),
    ("Update Wagerup Power Station maintenance strategy", "medium"),
    ("Assess LYB water cooling risk under drought scenario", "medium"),
    ("Prepare FY25 remuneration report for Annual Report", "high"),
    ("Review debt facility covenants for LYB impairment scenario", "high"),
    ("Develop renewable energy certificate (LGC) strategy for FY26", "medium"),
    ("Engage community liaison at Latrobe Valley on LYB transition", "high"),
    ("Implement ACCC retail pricing compliance review", "medium"),
    ("Complete annual review of Group insurance programme", "medium"),
    ("Prepare Board paper on strategic options for corporate HQ", "low"),
    ("Assess impact of BEV adoption on residential demand forecast", "medium"),
    ("Commission WA hydrogen strategy assessment", "low"),
    ("Review Newman Power Station fuel efficiency improvement options", "medium"),
    ("Prepare FY25 Annual Report carbon disclosure section", "high"),
    ("Update ALARP safety case documentation for LYB", "high"),
    ("Develop customer hardship programme enhancements for FY25", "medium"),
    ("Assess regulatory risk of WA standalone power systems competition", "medium"),
    ("Update Treasury policy for commodity price hedging", "medium"),
    ("Review and update delegation of authority framework", "medium"),
    ("Engage APRA on operational risk capital requirements", "medium"),
    ("Submit annual safety performance report to WorkSafe Victoria", "high"),
]

statuses_action = ["open", "in_progress", "complete", "overdue", "deferred"]
action_rows = []
for i, (desc, priority) in enumerate(action_templates):
    created = datetime.utcnow() - timedelta(days=random.randint(10, 180))
    due = date.today() + timedelta(days=random.randint(-30, 90))
    updated = created + timedelta(days=random.randint(0, 30))
    weights = [0.3, 0.3, 0.2, 0.1, 0.1]
    status = random.choices(statuses_action, weights=weights)[0]
    if priority == "critical":
        status = random.choice(["open", "in_progress"])

    action_rows.append(Row(
        action_id=f"ACT-{i+1:04d}",
        description=desc,
        owner=random.choice(owners),
        due_date=due,
        source_meeting=random.choice(meetings),
        status=status,
        priority=priority,
        created_at=created,
        updated_at=updated,
    ))

actions_df = spark.createDataFrame(action_rows)
actions_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.eds_actions.action_items")
print(f"[OK] action_items: {actions_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Decision Register (50 records)

# COMMAND ----------

decisions = [
    ("Board", "strategic", "Approve Group Strategy FY2025-2029 incorporating managed LYB transition and WA renewables growth", "Approved with conditions: LYB closure study to be commissioned, WA projects subject to individual FID", "CEO", "in_progress", ["DOC-001"], date(2024, 7, 1)),
    ("Board", "financial", "Approve FY2025 Budget and capital programme of $420 million", "Approved", "CFO", "complete", ["DOC-009"], date(2024, 7, 1)),
    ("IC", "financial", "Approve Yandin Stage 2 pre-FID study expenditure of $12 million", "Approved", "Head of Development", "complete", ["DOC-006"], date(2024, 7, 15)),
    ("Board", "risk", "Increase Trading VaR limit to $20 million subject to enhanced daily reporting", "Approved", "Head of Trading", "complete", ["DOC-013"], date(2024, 7, 15)),
    ("ELT", "operational", "Approve LYB Unit 3 outage programme and contractor engagement", "Approved; budget $42 million", "COO Generation", "complete", [], date(2024, 8, 5)),
    ("Board", "governance", "Approve updated ESG & Climate Risk framework and TCFD disclosure", "Approved; CSO to present quarterly", "CSO", "complete", ["DOC-005"], date(2024, 8, 30)),
    ("Board", "strategic", "Endorse phased approach to LYB transition; approve $2.5M closure readiness study", "Approved as recommended", "CEO", "in_progress", ["DOC-002"], date(2024, 9, 15)),
    ("RC", "risk", "Note OT Security Uplift Programme Phase 1 completion; approve Phase 2 commencement", "Approved; monthly updates to RC", "CISO", "complete", ["DOC-010"], date(2024, 9, 30)),
    ("ELT", "operational", "Approve Salesforce CRM Phase 2 go-live and retail migration plan", "Approved", "CEO Retail", "complete", [], date(2024, 10, 7)),
    ("Board", "governance", "Note Board Skills Matrix; approve AI/technology NED search mandate", "Approved; Spencer Stuart to be engaged", "Chair", "in_progress", ["DOC-014"], date(2024, 10, 15)),
    ("IC", "financial", "Approve execution of $600M revolving credit facility refinancing", "Approved; target BBSY + 175 bps", "CFO", "complete", [], date(2024, 10, 20)),
    ("ELT", "strategic", "Approve submission of WEM Capacity Mechanism review position paper", "Approved", "Head of Regulatory", "complete", ["DOC-008"], date(2024, 11, 25)),
    ("Board", "financial", "Approve interim FY25 dividend of 12.5 cents per share", "Approved; payable 28 February 2025", "CFO", "complete", ["DOC-003"], date(2024, 11, 30)),
    ("RC", "risk", "Approve $3.5M supplementary OT security budget for WA gas sites", "Approved; CISO to report quarterly", "CISO", "in_progress", ["DOC-010"], date(2024, 12, 1)),
    ("ELT", "operational", "Note Retail Transformation Programme Q2 FY25 status; approve AI Advisor go-live deferral", "Noted; revised April 2025 target approved", "CEO Retail", "complete", ["DOC-011"], date(2024, 12, 16)),
    ("Board", "financial", "Approve updated Capital Allocation Framework and progressive dividend policy", "Approved; effective 1 January 2025", "CFO", "complete", ["DOC-015"], date(2025, 1, 15)),
    ("IC", "financial", "Approve engagement of Goldman Sachs as green debt advisor for Yandin Stage 2", "Approved; retainer $0.5M", "CFO", "complete", ["DOC-006"], date(2025, 1, 20)),
    ("ELT", "operational", "Approve Alinta Solar + Battery + EV (PowerUp) commercial pilot expansion", "Approved; 500 customer Perth pilot", "CEO Retail", "complete", ["DOC-011"], date(2025, 1, 28)),
    ("Board", "strategic", "Note 1H FY25 financial results and confirm FY25 EBITDA guidance $590-620M", "Noted; guidance confirmed", "CFO", "complete", ["DOC-003"], date(2025, 2, 28)),
    ("Board", "financial", "Approve Yandin Stage 2 Final Investment Decision ($385M total)", "Approved", "CEO", "in_progress", ["DOC-006"], date(2025, 3, 1)),
    ("IC", "financial", "Approve Vestas EPC contract for Yandin Stage 2 ($295M lump sum)", "Approved; signed 15 March 2025", "Head of Development", "complete", ["DOC-006"], date(2025, 3, 1)),
    ("Board", "financial", "Approve project-level green debt facility mandate ($250M, 18-year tenor)", "Approved; ANZ and CBA preferred mandated banks", "CFO", "in_progress", ["DOC-006"], date(2025, 3, 1)),
    ("ELT", "operational", "Approve LYB Unit 2 outage plan and budget for Q3 FY26", "Approved; budget $45M", "COO Generation", "pending", [], date(2025, 3, 15)),
    ("RC", "risk", "Approve updated risk appetite statement for FY25; note top 10 risk register", "Approved", "CRO", "complete", ["DOC-007"], date(2025, 3, 30)),
    ("ELT", "strategic", "Approve FY26 digital acquisition target of 45% digital share", "Approved", "CEO Retail", "in_progress", ["DOC-011"], date(2025, 4, 1)),
    ("Board", "financial", "Approve FY26 Budget ($620M EBITDA target, $480M capex)", "Approved with note on LYB revenue sensitivity", "CFO", "pending", ["DOC-009"], date(2025, 5, 1)),
    ("IC", "financial", "Approve Oakajee BESS pre-FID feasibility study ($18M)", "Approved", "Head of Development", "pending", [], date(2025, 5, 15)),
    ("ELT", "operational", "Note Q3 FY25 LYB operations performance; no material changes required", "Noted", "COO Generation", "complete", [], date(2025, 3, 20)),
    ("Board", "governance", "Approve AASB S2 climate-related financial disclosures for FY25 Annual Report", "Approved; external assurance to be obtained", "CSO/CFO", "pending", ["DOC-005"], date(2025, 6, 1)),
    ("ELT", "operational", "Approve AI Energy Advisor full SME launch (350,000 accounts)", "Approved; April 2025 go-live", "CEO Retail", "complete", ["DOC-011"], date(2025, 4, 10)),
    ("RC", "risk", "Note increased cyber threat landscape; approve enhanced monitoring spend", "Approved; CISO to report monthly during high threat period", "CISO", "in_progress", [], date(2025, 2, 15)),
    ("Board", "strategic", "Approve updated Net Zero Roadmap with strengthened 2030 interim target", "Approved; 55% absolute reduction target by 2030", "CSO", "complete", ["DOC-005"], date(2025, 4, 15)),
    ("ELT", "financial", "Approve FY26 retail pricing review and TOU 3.0 tariff launch", "Approved", "CEO Retail", "in_progress", [], date(2025, 4, 28)),
    ("IC", "financial", "Note LYB coal supply contract renewal negotiations; approve procurement approach", "Approved; 2-year contract with option", "COO Generation", "in_progress", [], date(2025, 3, 10)),
    ("Board", "governance", "Appoint new independent NED (Technology/AI profile) effective 1 July 2025", "Approved pending successful candidate identification", "Chair", "in_progress", ["DOC-014"], date(2025, 5, 1)),
    ("ELT", "strategic", "Approve WA Hydrogen strategy assessment expenditure ($0.3M)", "Approved", "Head of Strategy", "pending", [], date(2025, 5, 20)),
    ("RC", "risk", "Approve updated counterparty credit limits for FY25 trading book", "Approved", "Head of Trading", "complete", ["DOC-013"], date(2024, 8, 15)),
    ("ELT", "operational", "Approve Pinjarra Power Station enhanced maintenance programme", "Approved; $3.5M budget", "COO Generation", "in_progress", [], date(2025, 2, 5)),
    ("Board", "strategic", "Note Competitive Intelligence Report FY25; approve digital response strategy", "Noted; CEO Retail to present action plan at December Board", "CEO Retail", "complete", ["DOC-004"], date(2024, 11, 15)),
    ("IC", "financial", "Approve Merredin Solar Farm land access agreement negotiations", "Approved; binding option to be executed", "Head of Development", "in_progress", [], date(2025, 3, 25)),
    ("ELT", "governance", "Approve updated delegation of authority framework", "Approved; effective 1 February 2025", "General Counsel", "complete", [], date(2025, 1, 30)),
    ("Board", "financial", "Approve final FY25 dividend of 16 cents per share (full year 28.5 cents)", "Approved; payable August 2025", "CFO", "pending", [], date(2025, 6, 15)),
    ("RC", "risk", "Approve physical climate risk assessment update (3-4°C scenario)", "Approved; $0.8M budget", "CRO", "in_progress", ["DOC-005"], date(2025, 4, 20)),
    ("ELT", "operational", "Approve Yandin Stage 1 O&M contract renewal with Vestas", "Approved; 5-year term at $14/MWh", "COO Generation", "complete", [], date(2025, 2, 20)),
    ("IC", "financial", "Approve financial model assumptions for Yandin Stage 2 project finance", "Approved; assumptions locked for debt term sheet", "CFO", "complete", ["DOC-006"], date(2025, 2, 28)),
    ("Board", "strategic", "Endorse updated People & Culture Strategy FY2025-FY2027", "Endorsed; CPO to report quarterly on LYB transition", "CPO", "complete", ["DOC-012"], date(2024, 8, 5)),
    ("ELT", "operational", "Approve enhanced cyber monitoring programme for LYB during heightened threat period", "Approved; $0.8M additional spend", "CISO", "complete", ["DOC-010"], date(2024, 12, 10)),
    ("Board", "financial", "Approve sustainability-linked KPI resets for revolving credit facility renewal", "Approved", "CFO/CSO", "complete", [], date(2024, 10, 22)),
    ("IC", "financial", "Approve FX hedging strategy for Yandin Stage 2 equipment imports (EUR/AUD)", "Approved; 12-month forward cover at 0.615 EUR/AUD", "CFO", "complete", [], date(2025, 3, 5)),
    ("ELT", "strategic", "Approve launch of East-West interconnector advocacy programme", "Approved; join AEC working group", "Head of Regulatory", "in_progress", [], date(2025, 4, 2)),
]

decision_rows = []
for i, (committee, dtype, desc, outcome, owner, impl_status, doc_ids, dd) in enumerate(decisions):
    decision_rows.append(Row(
        decision_id=f"DEC-{i+1:04d}",
        decision_date=dd,
        committee=committee,
        description=desc,
        decision_type=dtype,
        outcome=outcome,
        owner=owner,
        implementation_status=impl_status,
        supporting_docs=doc_ids,
        created_at=datetime.utcnow(),
    ))

decisions_df = spark.createDataFrame(decision_rows)
decisions_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.eds_actions.decision_register")
print(f"[OK] decision_register: {decisions_df.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Final Summary

# COMMAND ----------

tables = {
    f"{CATALOG}.eds_synthetic.asset_register": "Assets",
    f"{CATALOG}.eds_synthetic.documents": "Documents",
    f"{CATALOG}.eds_synthetic.financial_data": "Financial records",
    f"{CATALOG}.eds_synthetic.kpi_timeseries": "KPI data points",
    f"{CATALOG}.eds_synthetic.risk_register": "Risk items",
    f"{CATALOG}.eds_actions.action_items": "Action items",
    f"{CATALOG}.eds_actions.decision_register": "Decisions",
}

print("\n" + "="*65)
print("EXECUTIVE DECISION STUDIO — Synthetic Data Generation Complete")
print("="*65)
for tbl, label in tables.items():
    count = spark.table(tbl).count()
    print(f"  {label:30s} {count:>6,} rows   [{tbl.split('.')[-1]}]")
print("="*65)
print("\nAlinta Energy synthetic data generation completed successfully.")
print("All data is clearly marked as synthetic (is_synthetic=True where applicable)")
print("Ready for document ingestion and embedding pipeline.")
