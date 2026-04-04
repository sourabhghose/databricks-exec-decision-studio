# Product Requirements Document: Agentic AI Strategic Intelligence Platform

**Organisation:** Alinta Energy  
**Document Owner:** Office of the CEO / Chief Digital & Technology Officer  
**Classification:** Board-Confidential  
**Version:** 1.0 — Draft  
**Date:** April 2026  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Goals & Success Metrics](#3-goals--success-metrics)
4. [User Personas & Access Tiers](#4-user-personas--access-tiers)
5. [Functional Requirements](#5-functional-requirements) *(Capabilities 1–28)*
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Technical Architecture](#7-technical-architecture)
8. [Data Architecture & Knowledge Repository Design](#8-data-architecture--knowledge-repository-design)
9. [Agent Design Specifications](#9-agent-design-specifications) *(22 agents incl. Supervisor)*
10. [UI/UX Requirements](#10-uiux-requirements)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Risks & Mitigations](#12-risks--mitigations)
13. [Open Questions & Assumptions](#13-open-questions--assumptions)
14. [Evaluation, Governance, and Controls](#14-evaluation-governance-and-controls)
15. [Executive Foresight and Alerting](#15-executive-foresight-and-alerting)
16. [Simulation Governance and Decision Assurance](#16-simulation-governance-and-decision-assurance)

---

## 1. Executive Summary

### 1.1 Platform Vision

The **Agentic AI Strategic Intelligence Platform** (hereafter "the Platform") is a Databricks-native, multi-agent reasoning engine and governed knowledge repository purpose-built for the Board of Directors and C-suite of Alinta Energy. It transforms how Alinta's most senior leaders access, synthesise, and act on the organisation's most confidential strategic information — from board papers and financial forecasts to energy market dynamics and competitive intelligence.

Rather than a single chatbot or dashboard, the Platform deploys a coordinated ensemble of specialised AI agents, each designed for a distinct executive function: confidential document Q&A, strategic gap analysis, competitive profiling, digital twin scenario modelling, executive briefing synthesis, regulatory intelligence, portfolio analytics, CEO-level digital assistance, energy market simulation, early-warning signal detection, KPI exception monitoring, meeting intelligence, workflow orchestration, and self-evaluation. These agents share a common governance layer, knowledge repository, and security model — all managed through Databricks Unity Catalog and the Databricks AI Gateway.

### 1.2 Strategic Rationale

**Why now.** The Australian energy sector is in its most complex transition in decades. The accelerating closure of coal-fired generation, the scaling of renewables and storage, the evolution of the NEM and WEM market designs, growing regulatory scrutiny from AEMO, AER, and AEMC, and the entry of new competitors create a decision environment that exceeds the synthesis capacity of manual processes. Alinta's Board and executive team need the ability to rapidly assimilate internal and external information, stress-test strategic options, and respond to market shifts with confidence.

**Why Databricks-native.** Alinta Energy already operates a Databricks Lakehouse. Building on this foundation avoids the cost, complexity, and governance risk of introducing a parallel AI platform. Databricks provides a unified environment for data engineering, analytics, ML model lifecycle, vector search, agent orchestration, and governance — all under Unity Catalog. This means board-grade data classification, row-level and column-level security, lineage tracking, and model governance are enforced from a single control plane rather than stitched together across disparate tools.

**Why agentic.** Traditional BI dashboards and document search tools are passive — they answer only what is explicitly asked and cannot synthesise across domains. An agentic architecture enables proactive intelligence: agents that monitor signals, detect anomalies, draft briefings, prepare meeting materials, and propose strategic options without waiting to be prompted. Multi-agent orchestration allows each capability to be developed, tested, governed, and scaled independently while sharing a common knowledge fabric.

### 1.3 Expected Business Outcomes

| Outcome | Description |
|---------|-------------|
| **Improved decision quality** | Board and C-suite decisions grounded in comprehensive, cited, cross-domain intelligence rather than selectively assembled slide decks. |
| **Reduced time-to-insight** | Board pack and strategic briefing preparation reduced from weeks to hours; ad-hoc executive queries answered in seconds with full source attribution. |
| **Better risk management** | Continuous monitoring of regulatory, market, competitive, and operational signals reduces the probability of strategic blind spots. |
| **Executive productivity uplift** | CEO and C-suite freed from low-value information assembly tasks; meeting intelligence and action tracking reduce follow-up leakage. |
| **Scenario confidence** | Digital twin and market simulation capabilities provide board-grade scenario analysis with transparent assumptions and uncertainty quantification. |
| **Governance assurance** | Every query, retrieval, generation, and action is logged, traceable, and auditable — supporting internal audit, regulatory expectations, and responsible AI commitments. |

---

## 2. Problem Statement

### 2.1 Current-State Pain Points

**Disparate, siloed documents and data.** Alinta's most critical strategic information is scattered across SharePoint document libraries, email inboxes, board portals, financial planning systems, trading platforms, and individual laptops. There is no unified, searchable, governed repository of board papers, strategy documents, investment cases, regulatory submissions, and market analyses. When a Board Director or the CEO needs to trace the evolution of a strategic position across multiple board cycles, the task requires extensive manual effort and institutional memory.

**Heavy manual effort to prepare board packs, briefings, and scenarios.** The Strategy, Finance, and Corporate Affairs teams spend weeks before each board meeting compiling, summarising, and formatting information into board packs. Executive briefings for regulatory hearings, investor meetings, and media engagements require similar labour. Scenario analysis is typically conducted in isolated spreadsheets with limited ability to stress-test across variables or compare alternatives in a structured way.

**Limited ability to synthesise internal and external signals at speed.** The energy transition generates a continuous stream of regulatory changes, policy announcements, competitor actions, technology developments, market movements, and ESG expectations. Today, monitoring is fragmented — different teams track different signals, and there is no systematic mechanism to aggregate, prioritise, and surface what matters most to the Board and C-suite. Critical signals can be missed or identified too late to inform strategy.

**No unified, governed executive AI capability.** While individual teams may experiment with AI tools, there is no enterprise-grade, security-classified, governed AI capability designed for the most sensitive executive information. Ad-hoc use of consumer AI tools for board-level content poses unacceptable confidentiality and governance risks. There is no mechanism for AI-assisted scenario modelling, strategic reasoning, or proactive intelligence at the executive level.

**Executive time consumed by low-value tasks.** The CEO and C-suite spend significant time on tasks that could be augmented by AI: reviewing lengthy documents to extract key points, preparing for meetings, drafting communications, tracking action items, and synthesising information across domains. Without a structured executive AI assistant, this cognitive load reduces the time available for high-value strategic thinking.

### 2.2 Risks of the Status Quo

- **Strategic blind spots**: Without systematic signal detection and synthesis, the Board risks being surprised by regulatory shifts, competitor moves, or market dislocations that were foreseeable.
- **Decision latency**: Manual preparation of board materials and scenario analyses slows the organisation's ability to respond to time-sensitive strategic opportunities or threats.
- **Inconsistent information base**: Different executives may operate from different versions of truth when documents are scattered and unversioned, leading to misalignment.
- **Governance exposure**: Uncontrolled use of consumer AI tools for confidential content creates data leakage risk and compliance exposure under the Australian Privacy Act and critical infrastructure obligations.
- **Competitive disadvantage**: Peers and new entrants investing in AI-augmented executive decision-making will compound their strategic advantage over time.

---

## 3. Goals & Success Metrics

### 3.1 Objectives and Key Results

**Objective 1: Accelerate Executive Decision-Making**

| Key Result | Baseline | Target (12 months) |
|------------|----------|---------------------|
| Time to prepare board packs and strategic briefings | 3–4 weeks | < 3 days for first draft; < 1 week including review |
| Time for CEO/CFO to receive a cited answer to an ad-hoc strategic question | Hours to days (manual research) | < 60 seconds (interactive Q&A) |
| Number of board-cycle documents synthesised per query | Typically 1–3 (manual) | 50+ documents cross-referenced per query |

**Objective 2: Reduce Manual Analysis Effort**

| Key Result | Baseline | Target (12 months) |
|------------|----------|---------------------|
| Analyst hours per board cycle spent on document compilation and summarisation | 200+ hours across Strategy and Finance | Reduction of 60–70% |
| Time to produce a competitive landscape update | 2–3 weeks | < 1 day (agent-generated, human-reviewed) |
| Time to produce a regulatory impact assessment for a new AEMC/AER ruling | 1–2 weeks | < 4 hours (agent-generated draft) |

**Objective 3: Improve Signal Detection and Risk Awareness**

| Key Result | Baseline | Target (12 months) |
|------------|----------|---------------------|
| Percentage of material regulatory/market events surfaced to ExCo within 24 hours | Estimated < 50% | > 95% |
| Reduction in "missed signals" identified in post-incident reviews | No systematic measurement | Establish baseline in Phase 1; 50% reduction by Phase 3 |
| Executive satisfaction with strategic radar and early-warning outputs | N/A | > 4.0 / 5.0 across Board and ExCo |

**Objective 4: Drive Adoption and Executive Satisfaction**

| Key Result | Baseline | Target (12 months) |
|------------|----------|---------------------|
| Weekly active users among target personas (Board + C-suite + ELT) | 0 | > 80% of target persona group |
| Executive Net Promoter Score for the Platform | N/A | > 50 |
| Percentage of board meeting pre-reads generated or augmented by the Platform | 0% | > 60% |

**Objective 5: Deliver Trustworthy Scenario Analysis**

| Key Result | Baseline | Target (18 months) |
|------------|----------|---------------------|
| Simulation accuracy vs. historical outcomes (backtesting) | No capability | Within 15% of actuals on key financial metrics |
| Expert panel agreement rate with simulation-derived strategic recommendations | No capability | > 70% alignment |
| Percentage of simulations that include documented assumptions and uncertainty ranges | N/A | 100% |

**Objective 6: Ensure Governance and Compliance**

| Key Result | Baseline | Target (6 months) |
|------------|----------|---------------------|
| Percentage of agent outputs with full source citations | N/A | 100% for document-based Q&A |
| Percentage of queries with classification-appropriate access enforcement | N/A | 100% |
| Audit trail completeness for all agent interactions | N/A | 100% — every query, retrieval, generation, and action logged |

### 3.2 Leading Indicators (Monitored Continuously)

- Agent response latency (P50, P95) by capability and persona.
- Retrieval precision and recall on curated evaluation sets.
- Hallucination rate measured by the Evaluation Agent on sampled outputs.
- Token consumption and cost per query, per agent, per persona.
- User engagement: session length, follow-up questions, thumbs-up/down, agent re-invocations.
- Action item completion rate from Meeting Intelligence agent.

---

## 4. User Personas & Access Tiers

### 4.1 Persona Definitions

#### 4.1.1 Board Director / Chair

**Role context:** Non-executive directors and the Board Chair. Attend scheduled board meetings and committee meetings (Audit & Risk, People & Remuneration, Safety, etc.). Receive board packs in advance. Must exercise fiduciary duties with access to complete, accurate, and timely information.

**Goals:**
- Rapidly understand the state of the business, key risks, and strategic trajectory before and between board meetings.
- Ask probing questions on board papers and receive precise, cited answers.
- Track decisions and action items across board cycles.
- Understand competitive dynamics and market developments without deep technical energy-market expertise.

**Key decisions:** Strategic direction, capital allocation, CEO performance, risk appetite, M&A, policy positions.

**Pain points:**
- Board packs are voluminous; extracting the material points requires significant reading time.
- Difficult to trace how a strategic position has evolved across multiple board papers.
- Limited ability to independently verify management assertions or explore alternative scenarios.
- Between meetings, no easy way to get a quick update on emerging issues.

**Typical questions:**
- "What was the Board's position on the Pilbara expansion when it was last discussed, and what has changed since?"
- "Summarise the key financial risks flagged in the last three Audit & Risk Committee papers."
- "How does our renewables pipeline compare to AGL's and Origin's announced plans?"
- "What are the top three regulatory developments this quarter that could affect our strategy?"

**Access tier:** Board-Only, ExCo, Confidential, Internal, Public.

---

#### 4.1.2 Chief Executive Officer (CEO)

**Role context:** Accountable for enterprise strategy, performance, and stakeholder management. The most intensive user of the executive assistant capabilities. Requires the broadest information access and the most proactive intelligence.

**Goals:**
- Maintain a continuously updated picture of the business across all domains.
- Receive proactive alerts on issues requiring attention before they escalate.
- Optimise personal productivity: meeting preparation, communications, action tracking.
- Test strategic hypotheses rapidly through scenario modelling.

**Key decisions:** Strategic priorities, organisational structure, stakeholder positioning, crisis response, resource allocation across business units.

**Pain points:**
- Information overload — hundreds of documents, emails, and reports per week.
- Preparation for external engagements (investors, regulators, media, government) is time-consuming.
- Tracking follow-through on decisions and commitments across the organisation.
- Limited ability to quickly model "what if" scenarios across the portfolio.

**Typical questions:**
- "What are the three things I need to know this morning before my 9am leadership meeting?"
- "Draft a response to the Minister's letter on energy reliability, drawing on our latest market position paper."
- "If we accelerated the Yandin wind farm expansion by 18 months, what would be the impact on our capital plan and debt covenants?"
- "What actions from last week's ExCo meeting are overdue?"

**Access tier:** All tiers — Board-Only, ExCo, ELT, BU-Specific, Confidential, Internal, Public.

---

#### 4.1.3 Chief Financial Officer (CFO)

**Role context:** Accountable for financial performance, capital allocation, treasury, tax, and investor relations. Heavy consumer of forecasts, budgets, variance analyses, and financial scenarios.

**Goals:**
- Rapidly compare budget vs. actuals and forecast variances across business units.
- Understand financial implications of strategic scenarios and market movements.
- Prepare investor and analyst briefing materials efficiently.
- Monitor financial KPIs and leading indicators with early anomaly detection.

**Key decisions:** Capital allocation, funding strategy, dividend policy, financial risk management, cost optimisation.

**Pain points:**
- Reconciling financial data across multiple systems and reporting cycles.
- Manual effort to produce scenario-based financial projections.
- Difficulty tracing financial assumptions back to underlying strategic documents.

**Typical questions:**
- "What is the variance between the FY26 budget and latest forecast for the generation business, and what are the key drivers?"
- "Show me the EBITDA impact under three coal-exit scenarios with current gas price assumptions."
- "What did we tell investors about our renewables capex trajectory in the last two reporting periods?"

**Access tier:** Board-Only (financial content), ExCo, ELT, Confidential (financial), Internal, Public.

---

#### 4.1.4 Chief Operating Officer (COO) / Chief Risk Officer (CRO)

**Role context:** Accountable for operational performance, asset management, safety, and enterprise risk. Focused on operational KPIs, incident trends, outage management, and risk register.

**Goals:**
- Monitor operational performance and safety metrics with anomaly detection.
- Assess operational risk implications of strategic decisions and market events.
- Track asset performance, maintenance schedules, and outage impacts.

**Key decisions:** Operational priorities, capital maintenance, safety investments, risk mitigation actions, business continuity.

**Pain points:**
- Risk and operational data spread across multiple systems with no unified view for executive decision-making.
- Difficulty modelling cascading risks (e.g., how a transmission constraint interacts with a planned outage and a gas supply disruption).

**Typical questions:**
- "What are the top five operational risks this quarter and how have they trended?"
- "If Unit 3 at Loy Yang has an unplanned outage during a summer heatwave, what is our financial exposure?"
- "Summarise the last three months of safety incident trends across all sites."

**Access tier:** ExCo, ELT, BU-Specific (operations, risk), Confidential, Internal, Public.

---

#### 4.1.5 Chief Strategy Officer / Strategy & Corporate Development Lead

**Role context:** Leads strategic planning, M&A, corporate development, and long-range portfolio strategy. Primary author and consumer of strategy documents and investment cases.

**Goals:**
- Maintain a comprehensive view of the competitive landscape and market evolution.
- Rapidly produce and iterate strategic analyses and investment cases.
- Test strategic options through scenario modelling and digital twin capabilities.
- Track strategic initiatives and their progress against milestones.

**Key decisions:** Portfolio composition, market entry/exit, M&A targets, partnership strategies, long-range plan assumptions.

**Pain points:**
- Strategy development relies on extensive manual research and document synthesis.
- Competitive intelligence is collected episodically rather than continuously.
- Scenario modelling is constrained by spreadsheet-based tools.

**Typical questions:**
- "Where does Alinta's generation portfolio have gaps relative to the evolving NEM generation mix over the next decade?"
- "Produce a competitive profile of Snowy Hydro including their announced capacity pipeline and recent regulatory positions."
- "Model three scenarios for our WA retail business under different capacity mechanism outcomes."

**Access tier:** Board-Only (strategy documents), ExCo, ELT, Confidential, Internal, Public.

---

#### 4.1.6 Chief Technology Officer (CTO) / Chief Digital Officer (CDO)

**Role context:** Accountable for technology strategy, digital transformation, cybersecurity, and the Platform itself. Sponsor and technical owner of the Agentic AI initiative.

**Goals:**
- Ensure the Platform meets enterprise security, governance, and architecture standards.
- Monitor platform performance, cost, adoption, and AI quality metrics.
- Stay ahead of technology and cybersecurity developments.

**Key decisions:** Technology investments, vendor strategy, cybersecurity posture, AI governance policies, platform roadmap.

**Access tier:** ExCo, ELT, BU-Specific (technology), Confidential, Internal, Public.

---

#### 4.1.7 Executive General Managers (EGMs) and Finance/Strategy Leads

**Role context:** Business unit leaders and their senior strategy/finance reports. Consume and contribute to board papers and strategic analyses within their domain (Retail, Generation, Trading, Corporate).

**Goals:**
- Access domain-specific intelligence and analysis efficiently.
- Contribute to board paper preparation with AI-augmented drafting.
- Monitor BU-specific KPIs and leading indicators.

**Access tier:** ELT, BU-Specific (own business unit), Confidential, Internal, Public. Do not access Board-Only or ExCo-restricted content unless explicitly granted.

---

#### 4.1.8 Executive Assistants and Chiefs of Staff

**Role context:** Support the CEO and C-suite with scheduling, communications, meeting coordination, and action tracking. Key users of the executive assistant and meeting intelligence capabilities.

**Goals:**
- Streamline meeting preparation: pre-reads, agendas, briefing packs.
- Automate action item capture and follow-up tracking.
- Draft routine executive communications and manage information flow.

**Pain points:**
- Significant time spent manually compiling pre-reads and chasing action item owners.
- No single system for tracking executive commitments and decisions.

**Access tier:** Delegated access matching their principal's tier, with audit logging of all delegated actions. Explicit authorisation required for Board-Only content.

---

#### 4.1.9 Trading, Risk, and Market Analytics Leads

**Role context:** Operate Alinta's trading desk and energy market analytics. Primary users of the market simulation and digital twin capabilities. Deep domain expertise in NEM/WEM dispatch, pricing, hedging, and risk management.

**Goals:**
- Run sophisticated market simulations and stress tests for portfolio optimisation.
- Receive early-warning signals on market developments, fuel prices, and policy changes.
- Provide market intelligence inputs to strategy and board processes.

**Key decisions:** Trading positions, hedging strategies, dispatch optimisation, market risk management.

**Access tier:** ELT, BU-Specific (trading, market analytics), Confidential, Internal, Public. Access to simulation models and market data. Do not access Board-Only or M&A-specific content unless explicitly granted.

---

### 4.2 Access Control and Classification Model

#### 4.2.1 Document Classification Tiers

| Tier | Description | Example Content |
|------|-------------|-----------------|
| **Board-Only** | Accessible only to Board Directors, Board Secretary, CEO, and explicitly authorised support staff. | Board papers, board minutes, director correspondence, CEO performance reviews. |
| **ExCo** | Accessible to the Executive Committee (C-suite) and Board. | ExCo papers, executive strategy sessions, M&A pipeline, sensitive financial forecasts. |
| **ELT** | Accessible to the Extended Leadership Team and above. | Business unit strategies, operational reviews, organisational restructuring plans. |
| **BU-Specific** | Accessible to members of a specific business unit and above. | Retail strategy, generation asset plans, trading desk analyses. |
| **Confidential** | Accessible to all employees with a need-to-know, but not externally. | Internal policies, HR guidelines, IT architecture documents. |
| **Internal** | Accessible to all Alinta employees. | Company announcements, intranet content, general procedures. |
| **Public** | No access restrictions. | Published reports, media releases, regulatory filings. |

#### 4.2.2 Access Control Enforcement

Access controls are enforced at every layer of the Platform:

1. **Ingestion**: Every document is classified at ingestion time. Classification is stored as metadata in Unity Catalog and propagated to all derived artefacts (chunks, embeddings, summaries).
2. **Retrieval**: The RAG layer applies classification-based filters before returning any document chunks. A query from a persona with ELT access will never retrieve Board-Only or ExCo chunks.
3. **Generation**: The agent prompt includes the user's access tier. If retrieved context inadvertently includes content above the user's tier (defence-in-depth), the generation layer is instructed to exclude it and log the event.
4. **Response delivery**: All responses include metadata indicating the highest classification tier of the source material used.
5. **Audit**: Every query, retrieval hit, and generated response is logged with the user's identity, access tier, and classification of sources accessed.

**[ASSUMPTION: Alinta Energy operates Azure Active Directory (Entra ID) for identity management. Access tier mappings will be maintained as Unity Catalog group memberships synchronised from Entra ID security groups.]**

#### 4.2.3 Persona-to-Tier Access Matrix

| Persona | Board-Only | ExCo | ELT | BU-Specific | Confidential | Internal | Public |
|---------|:----------:|:----:|:---:|:-----------:|:------------:|:--------:|:------:|
| Board Director / Chair | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| CEO | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| CFO | Yes (financial) | Yes | Yes | Yes | Yes | Yes | Yes |
| COO / CRO | No | Yes | Yes | Yes | Yes | Yes | Yes |
| Chief Strategy Officer | Yes (strategy) | Yes | Yes | Yes | Yes | Yes | Yes |
| CTO / CDO | No | Yes | Yes | Yes | Yes | Yes | Yes |
| EGMs / Finance Leads | No | No | Yes | Own BU | Yes | Yes | Yes |
| Executive Assistants | Delegated | Delegated | Delegated | Delegated | Yes | Yes | Yes |
| Trading / Market Analytics | No | No | Yes | Trading/Market | Yes | Yes | Yes |

---

## 5. Functional Requirements

This section specifies the functional requirements for each of the fifteen agent capabilities. For each capability, we define the purpose, representative user stories, interaction patterns, and key behavioural requirements.

### 5.1 Capability 1: Confidential Q&A over Documents

**Purpose:** Enable Board Directors and C-suite to ask natural-language questions over the full corpus of board papers, strategy documents, financial forecasts, budgets, investment cases, regulatory submissions, and market analyses — and receive precise, cited answers that respect document classification.

**User Stories:**

- *As a Board Director*, I want to ask "What was the agreed position on the Leigh Creek gas supply contract at the November 2025 Board meeting?" and receive the exact answer with citation to the relevant board minute and paper, so I can prepare for the upcoming review.
- *As the CEO*, I want to ask "What are the top five risks to our FY27 EBITDA target?" and receive a synthesised answer drawn from the latest risk register, financial forecast, and strategy review, with each claim attributed to its source.
- *As the CFO*, I want to ask "How has our net debt-to-EBITDA guidance evolved over the last four quarterly board packs?" and receive a time-ordered summary with citations.

**Interaction Patterns:**

- **Primary**: Conversational chat interface with multi-turn follow-up. The user asks a question, receives a cited answer, and can refine or drill deeper.
- **Secondary**: Scheduled digest — e.g., "Every Monday, send me a summary of new documents added to the board repository this week."
- **Tertiary**: Embedded Q&A within document viewers — highlight a passage and ask "explain this" or "what is the latest update on this topic?"

**Behavioural Requirements:**

- Every factual claim in a response must include a citation to a specific document, section, and page (where applicable).
- The agent must indicate the date and version of each cited source.
- If no relevant source is found, the agent must state "I could not find information on this topic in the available documents" rather than speculate.
- If the user's access tier prohibits access to the most relevant sources, the agent must respond based only on permitted sources and disclose: "Note: some documents relevant to this topic are classified above your current access tier."
- Multi-turn memory within a session: the agent retains context from previous turns to support follow-up questions (e.g., "What about for the WA retail business specifically?").
- Session memory does not persist across sessions unless the user explicitly bookmarks a conversation.

---

### 5.2 Capability 2: Strategic Gap Analysis

**Purpose:** Identify gaps in Alinta's strategy relative to industry trends, regulatory shifts, technological change, customer behaviour, and competitor positioning. Proactively surface areas where the current strategic plan may be under-weighted, outdated, or misaligned.

**User Stories:**

- *As the Chief Strategy Officer*, I want to ask "Where are the gaps in our current five-year strategic plan relative to the latest AEMO Integrated System Plan?" and receive a structured gap analysis with specific areas of misalignment.
- *As the CEO*, I want a quarterly strategic gap report that compares our announced strategy to our top three competitors' publicly stated positions.
- *As a Board Director*, I want to understand "Are there emerging technology trends in energy storage or hydrogen that our strategy does not adequately address?"

**Interaction Patterns:**

- **On-demand**: Conversational queries that trigger a multi-step analysis (retrieve strategy docs, retrieve comparators, identify gaps, structure output).
- **Scheduled**: Quarterly or ad-hoc "strategic health check" reports delivered as structured documents or executive summaries.
- **Proactive**: When a material external event (e.g., a new government policy, competitor announcement, or AEMO report) is ingested, the agent assesses its implications against the current strategic plan and flags gaps.

**Behavioural Requirements:**

- Gaps must be categorised (e.g., regulatory alignment, technology portfolio, market positioning, customer proposition, ESG/sustainability, financial resilience).
- Each gap must reference specific sections of Alinta's strategic documents and the external comparator.
- The agent must distinguish between areas where the strategy is explicitly silent vs. areas where the strategy is present but potentially insufficient.
- Confidence scoring: High (clear documentary evidence), Medium (inferred from patterns), Low (speculative or based on limited data).

---

### 5.3 Capability 3: Competitive Analysis

**Purpose:** Provide structured, continuously updated competitor profiles and competitive landscape analyses to support strategy formulation and board discussions.

**User Stories:**

- *As the Chief Strategy Officer*, I want a comprehensive competitive profile of AGL Energy covering their generation portfolio, retail market share, announced investments, regulatory positions, and digital strategy.
- *As a Board Director*, I want to ask "How does our renewables capacity pipeline compare to Origin Energy's as of the latest available data?"
- *As the CEO*, I want to be alerted when a major competitor makes a significant strategic announcement (e.g., new generation project, market entry, M&A activity).

**Interaction Patterns:**

- **On-demand**: Conversational query for specific competitor comparisons or profiles.
- **Structured reports**: Periodic competitive landscape reports (quarterly) covering all major competitors.
- **Alerts**: Real-time or near-real-time notifications when competitor intelligence signals are detected.

**Behavioural Requirements:**

- Competitor profiles must be structured consistently: overview, portfolio, financials (public), strategy (stated), recent actions, strengths, vulnerabilities, and implications for Alinta.
- Sources must be clearly distinguished: public filings, media reports, analyst commentary, Alinta internal assessments.
- The agent must not present speculation as fact. If a competitor's position is inferred rather than stated, this must be labelled.
- Competitors to track: AGL Energy, Origin Energy, EnergyAustralia, Snowy Hydro, Iberdrola (via Infigen), Shell Energy, Engie, Squadron Energy, Neoen, Goldwind, and emerging entrants.

**[ASSUMPTION: Alinta has or will subscribe to relevant external data feeds — analyst reports, market data, news monitoring services — and these will be ingested into the platform.]**

---

### 5.4 Capability 4: Digital Twin / Strategic Scenario Modelling

**Purpose:** Enable the Board and C-suite to model the financial, operational, and strategic consequences of major decisions under multiple scenarios, providing board-grade decision support with transparent assumptions.

**User Stories:**

- *As the CEO*, I want to model: "What happens to our EBITDA, net debt, and emissions trajectory if we exit coal generation two years earlier than planned and accelerate our renewables pipeline?"
- *As the CFO*, I want to compare three capital allocation scenarios side by side: (a) accelerated renewables, (b) gas peaker investment, (c) battery storage expansion — each under high, base, and low demand assumptions.
- *As a Board Director*, I want to stress-test the long-range plan: "What if wholesale electricity prices are 20% below the base case for three consecutive years?"

**Interaction Patterns:**

- **Conversational scenario definition**: The user describes a scenario in natural language; the agent translates it into model parameters, executes the simulation, and returns results.
- **Scenario comparison dashboard**: Side-by-side views of key metrics under different scenarios.
- **Sensitivity analysis**: "Which three assumptions has the EBITDA outcome most sensitive to?"
- **Assumption library**: Pre-defined and user-customisable assumption sets (e.g., "AEMO Step Change", "Current Policy", "Rapid Decarbonisation").

**Behavioural Requirements:**

- All scenario results must be presented with explicit assumptions, data sources, and model version.
- Uncertainty must be communicated — e.g., confidence intervals, distributions, or sensitivity tables rather than single-point estimates.
- The agent must explain the causal logic: "EBITDA declines by $X because [coal revenue loss of $Y] partially offset by [renewables revenue of $Z] and [reduced fuel costs of $W]."
- Scenario outputs must include: financial KPIs (revenue, EBITDA, free cash flow, net debt), risk metrics (VaR, CVaR, earnings-at-risk), operational metrics (capacity factors, emissions), and strategic indicators (market share, customer numbers).
- Simulation results must be labelled as "directional insight" or "decision-grade" depending on model maturity and calibration status.

---

### 5.5 Capability 5: Strategic Recommendation Engine

**Purpose:** Proactively generate data-grounded strategic recommendations and options for board and executive discussions, including structured pros/cons, risk assessments, and implementation considerations.

**User Stories:**

- *As the CEO*, I want the platform to propose "Given the current competitive landscape, regulatory trajectory, and our portfolio position, what are the top three strategic moves Alinta should consider in the next 12 months?"
- *As the Chief Strategy Officer*, I want to evaluate a specific option: "Assess the strategic case for entering the behind-the-meter battery market in Victoria."
- *As a Board Director*, I want the recommendation engine to present options for a decision item with balanced pros and cons.

**Interaction Patterns:**

- **On-demand**: User asks for recommendations on a specific topic or in a specific context.
- **Proactive**: After a strategic gap or early-warning signal is identified, the recommendation engine generates options automatically and queues them for executive review.
- **Board paper augmentation**: When a strategy paper is being prepared, the recommendation engine proposes additional options or risk considerations.

**Behavioural Requirements:**

- Recommendations must be evidence-based, citing internal data and documents.
- Each recommendation must include: rationale, supporting evidence, risks and mitigations, resource implications, timeline, and dependencies.
- The agent must present multiple options (typically 2–4) rather than a single recommendation, to preserve executive agency.
- Recommendations must be clearly labelled as "AI-generated options for executive consideration" — never as directives.
- Confidence scoring on each recommendation with explanation of the basis.

---

### 5.6 Capability 6: Executive Briefing Synthesis

**Purpose:** Auto-generate board-ready summaries, situation reports, talking points, and Q&A packs from large collections of internal and external documents.

**User Stories:**

- *As the Board Secretary*, I want to generate a one-page executive summary of each board paper in the upcoming board pack.
- *As the CEO*, I want talking points for tomorrow's meeting with the Federal Energy Minister, drawing on our latest regulatory position papers, market analysis, and recent government announcements.
- *As the CFO*, I want a Q&A pack anticipating the questions analysts are likely to ask at our next earnings briefing, with suggested responses grounded in our latest financial data.

**Interaction Patterns:**

- **On-demand generation**: User specifies the briefing type, audience, topic, and source documents (or the agent selects relevant sources automatically).
- **Template-driven**: Pre-defined briefing templates (e.g., "Board Paper Summary", "Stakeholder Talking Points", "Regulatory Hearing Prep").
- **Iterative refinement**: The user reviews a draft and requests adjustments (e.g., "Make the tone more cautious on the renewables timeline", "Add a section on WEM reform implications").

**Behavioural Requirements:**

- Outputs must match the expected format for the target audience (Board, investor, regulatory, media).
- Length and level of detail must be controllable: "Give me 200 words" or "Give me a comprehensive brief".
- All claims must be cited. Where a briefing synthesises across multiple sources, footnotes or inline references must be provided.
- The agent must flag areas where source material is conflicting or ambiguous.

---

### 5.7 Capability 7: Regulatory & Market Intelligence

**Purpose:** Continuously track regulatory and market developments from AEMO, AER, AEMC, ESB, state energy regulators, and other relevant bodies, and surface implications for Alinta's strategy, operations, and risk profile.

**User Stories:**

- *As the Chief Strategy Officer*, I want to ask "What are the implications of the latest AEMC capacity mechanism rule change for our WA business?"
- *As the CEO*, I want a weekly regulatory intelligence digest highlighting the top five developments and their assessed impact on Alinta.
- *As the CRO*, I want to be alerted within 24 hours when a new draft determination or rule change is published that could affect Alinta's generation or retail licences.

**Interaction Patterns:**

- **Scheduled digests**: Weekly or fortnightly regulatory/market intelligence summaries delivered to ExCo.
- **On-demand queries**: Conversational questions about specific regulatory topics.
- **Alerts**: Threshold-based notifications for material developments.
- **Impact assessments**: On detection of a significant development, the agent produces a structured impact assessment linking the development to Alinta's assets, markets, and strategic initiatives.

**Behavioural Requirements:**

- The agent must monitor and ingest publications from: AEMO (ISP, ESOO, market notices), AER (determinations, reviews), AEMC (rule changes, reviews), ESB (post-2025 market design), state regulators (ERA-WA, ESCOSA-SA, IPART-NSW, ESC-VIC), federal government energy policy announcements.
- Each development must be assessed for relevance (high/medium/low) and urgency (immediate/near-term/monitor).
- Impact assessments must link to specific Alinta assets, markets, business units, or strategic initiatives.
- External market intelligence (analyst reports, industry body publications, international comparators) should be integrated where available.

**[ASSUMPTION: Alinta will provide or procure access to regulatory publication feeds, and these will be ingested into the platform on a daily or near-real-time basis.]**

---

### 5.8 Capability 8: Portfolio and Financial Analysis

**Purpose:** Enable cross-document analysis of financial performance, forecasts, budgets, capital allocation, and risk/return trade-offs across Alinta's portfolio.

**User Stories:**

- *As the CFO*, I want to ask "Show me the variance between FY26 budget and Q3 forecast for each business unit, broken down by revenue, opex, and capex."
- *As the CEO*, I want to understand "Which capital projects are trending above budget and by how much?"
- *As a Board Director*, I want to compare "How has our capital allocation to renewables vs. thermal changed over the last three long-range plans?"

**Interaction Patterns:**

- **Conversational Q&A**: Natural-language queries over financial documents and datasets.
- **Structured reports**: Automated generation of variance reports, capital allocation summaries, and project performance dashboards.
- **Scenario overlays**: "Show me the same variance analysis under the 'high gas price' scenario."
- **Trend analysis**: "How has metric X trended over the last N periods?"

**Behavioural Requirements:**

- The agent must integrate data from both structured sources (financial databases, Delta Lake tables) and unstructured sources (board papers, budget commentary, investment cases).
- Financial figures must be precise — no rounding or approximation unless requested.
- The agent must distinguish between audited actuals, management estimates, and forecasts.
- Variance explanations must reference underlying business drivers, not just arithmetic differences.
- All financial outputs must include currency, period, and data source metadata.

**[ASSUMPTION: Alinta's financial data (budgets, actuals, forecasts) is available or will be made available in Delta Lake tables within the Databricks Lakehouse, in addition to unstructured financial documents.]**

---

### 5.9 Capability 9: CEO / Executive AI Assistant

**Purpose:** Provide autonomous executive assistant capabilities for the CEO and C-suite — optimising scheduling, drafting communications, preparing meeting materials, capturing meeting intelligence, and tracking action items.

**User Stories:**

- *As the CEO*, I want to say "Draft a reply to [person]'s email about the [topic], noting our position from the last ExCo discussion and suggesting a follow-up meeting next week."
- *As the CEO*, I want to ask "What do I need to prepare for my 2pm meeting with [external stakeholder]?" and receive a pre-read with background, recent interactions, and suggested talking points.
- *As an Executive Assistant*, I want the agent to generate a meeting summary after each ExCo meeting, including decisions made, action items with owners and due dates, and key risks discussed.
- *As the CFO*, I want to say "Remind me on Friday to follow up with [EGM] on the capital project overrun."

**Interaction Patterns:**

- **Conversational**: Natural-language instructions for drafting, scheduling, and information retrieval.
- **Proactive**: Morning briefing ("Here are your top priorities today"), pre-meeting intelligence (auto-generated 15 minutes before each meeting), and end-of-day summary.
- **Task-oriented**: Action item creation, delegation, and follow-up tracking.
- **Email/calendar integration**: Draft emails appear in the executive's Outlook drafts folder for review before sending. Calendar suggestions are presented as proposals, not auto-committed.

**Behavioural Requirements:**

- The agent must never send an email or commit a calendar change without explicit human approval. All actions are proposed, not executed autonomously.
- Communication drafts must match the executive's tone and style. **[ASSUMPTION: Tone/style calibration will be based on a sample of the executive's past communications, provided with consent.]**
- Meeting pre-reads must be concise (1–2 pages) and tailored to the specific meeting context.
- Meeting summaries must distinguish between confirmed decisions, tentative agreements, and open items.
- Action items must be extracted with: description, owner, due date, and source meeting.
- The "executive action register" must be queryable: "What actions are overdue?" "What did we decide about X?"
- Privacy protection: the agent must not share one executive's personal communications or calendar details with another executive unless explicitly authorised.

---

### 5.10 Capability 10: Energy Market Simulation & Market Digital Twin

**Purpose:** Provide agent-based and scenario-based modelling of NEM and WEM market dynamics — prices, dispatch, congestion, demand, fuel prices, outages, renewables penetration, and policy settings — to support portfolio optimisation and strategic decision-making.

**User Stories:**

- *As a Trading Lead*, I want to simulate "What happens to NEM spot prices in Victoria if Loy Yang A Unit 2 has an unplanned outage during a February heatwave while gas prices are $2/GJ above current levels?"
- *As the Chief Strategy Officer*, I want to model "How does the NEM dispatch stack evolve under three different CIS (Capacity Investment Scheme) designs, and what is the impact on Alinta's generation revenue?"
- *As the CEO*, I want a stress test: "Under extreme weather and fuel price conditions similar to the June 2022 market suspension, what is Alinta's financial exposure?"

**Interaction Patterns:**

- **Scenario definition via natural language**: The user describes a scenario; the agent translates it to simulation parameters.
- **Pre-built scenario library**: Standard scenarios (AEMO ISP scenarios, extreme weather, fuel shocks) available for one-click execution.
- **Comparison views**: Side-by-side comparison of scenario outcomes with difference highlighting.
- **Sensitivity explorer**: Interactive adjustment of key parameters to observe impact on outcomes.

**Behavioural Requirements:**

- Simulation models must capture NEM dispatch dynamics (5-minute dispatch, semi-scheduling, interconnector flows, frequency control), WEM market dynamics (bilateral market, reserve capacity mechanism, balancing market), fuel supply and pricing (gas, coal, diesel), renewable generation profiles (wind, solar, hydro), demand profiles (including embedded generation and storage), and transmission constraints.
- All simulation runs must be logged with full parameter sets, model version, input data versions, and execution metadata.
- Results must include uncertainty quantification: confidence intervals, percentile distributions, or scenario-specific probability weights.
- The competitive response simulation capability must model how competitors might react to Alinta's moves — e.g., if Alinta announces early coal exit, how might competitors adjust their bidding behaviour or investment plans?
- Simulation outputs must be clearly labelled: "This is a model-based projection, not a forecast. Results are sensitive to [key assumptions]."

**[ASSUMPTION: Alinta has existing market simulation models (e.g., PLEXOS, Prophet, or internal tools) that can be integrated or whose logic can be replicated within the Databricks environment. Integration patterns will be defined during Phase 3.]**

---

### 5.11 Capability 11: Early Warning & Signal Detection (Executive Radar)

**Purpose:** Continuously monitor a wide range of internal and external signals, detect weak and strong indicators of emerging risks and opportunities, and escalate prioritised intelligence to the Board and C-suite.

**User Stories:**

- *As the CEO*, I want a weekly "strategic radar" that shows me the top emerging signals across regulatory, competitive, technology, market, and operational domains, ranked by assessed impact and urgency.
- *As the CRO*, I want to be alerted immediately if there is a cluster of signals suggesting an emerging supply chain risk for our gas contracts.
- *As a Board Director*, I want to receive a monthly "signals to watch" brief before each Board meeting highlighting the most significant changes since the last meeting.

**Interaction Patterns:**

- **Scheduled reports**: Weekly radar (ExCo), monthly foresight brief (Board), quarterly deep-dive on thematic clusters.
- **Ad-hoc queries**: "What signals are we seeing on hydrogen policy developments in Australia?"
- **Threshold-based alerts**: Immediate notification when a signal cluster exceeds a defined impact/urgency threshold.
- **Signal explorer**: Interactive interface to browse, filter, and drill into detected signals.

**Behavioural Requirements:**

- Signal sources must include: regulatory publications, news media, analyst reports, competitor announcements, social media (sentiment on key topics), energy market data (price movements, demand patterns), internal operational data (asset performance, customer churn), and ESG/climate data.
- Signals must be classified by domain (regulatory, competitive, technology, market, operational, ESG, geopolitical, cyber).
- Each signal must have: source, date, description, assessed impact (high/medium/low), assessed urgency (immediate/near-term/watch), confidence level, and link to affected Alinta assets/strategies.
- Alert fatigue must be managed: the agent must aggregate, cluster, and prioritise rather than forwarding every individual signal. De-duplication across sources is essential.
- The radar must distinguish between signals that require action vs. signals for awareness only.

---

### 5.12 Capability 12: Executive KPI & Exception Monitoring Agent

**Purpose:** Continuously monitor strategic KPIs and leading indicators across financial, operational, customer, ESG, and risk domains, detect anomalies and trend breaks, and provide persona-tailored explanations and action options.

**User Stories:**

- *As the CEO*, I want to be notified if any of my top-10 strategic KPIs deviates from the expected trend by more than a defined threshold.
- *As the CFO*, I want a daily snapshot of key financial metrics (revenue run-rate, cash position, debt levels) with automatic flagging of unusual movements.
- *As the COO*, I want to be alerted if plant availability at any generation asset drops below the seasonal target.

**Interaction Patterns:**

- **Proactive alerts**: Push notifications when a KPI breaches a threshold or an anomaly is detected.
- **Dashboards**: Executive dashboard showing KPI status (green/amber/red), trends, and forecasts.
- **Conversational drill-down**: "Why is customer churn up this month?" triggers a multi-source analysis.
- **Scheduled snapshots**: Daily/weekly KPI summaries tailored to each persona.

**Behavioural Requirements:**

- KPI definitions must be governed and approved by the relevant business owners. The platform stores KPI definitions, thresholds, and ownership metadata.
- Anomaly detection must go beyond simple threshold breaches to detect trend breaks, acceleration/deceleration, and cross-KPI correlations (e.g., revenue up but margin down).
- Explanations must be multi-source: "Customer churn increased by 2.3% this month, driven primarily by [residential segment in Victoria]. Contributing factors appear to be [competitor price promotion by Origin] and [delayed implementation of our retention offer]. Source: [CRM data], [competitor monitoring]."
- Action options must be tailored to the persona: the CFO receives financial levers, the COO receives operational levers, the CEO receives strategic framing.
- KPIs must include: financial (revenue, EBITDA, cash flow, capex, net debt), operational (plant availability, capacity factor, forced outage rate, safety incident rate), customer (customer numbers, churn, NPS, complaints), ESG (emissions intensity, renewable percentage, community investment), and risk (VaR, credit exposure, regulatory compliance).

---

### 5.13 Capability 13: Meeting Intelligence & Action Tracking

**Purpose:** Prepare tailored pre-reads and summaries for every executive meeting, capture decisions and action items, and maintain an "executive action register" that tracks follow-through across meetings and committees.

**User Stories:**

- *As the CEO*, I want a one-page pre-read for each meeting in my calendar, generated 30 minutes before the meeting, covering the agenda, key background, and open items from previous meetings on the same topic.
- *As the Board Secretary*, I want the agent to generate draft board minutes from meeting notes and recordings, structured by agenda item with decisions, actions, and risk items highlighted.
- *As an Executive Assistant*, I want to ask "What actions from the last three ExCo meetings are still open?" and receive a filterable list with owners, due dates, and status.

**Interaction Patterns:**

- **Automated pre-reads**: Generated before each meeting based on calendar data, agenda, and relevant document history.
- **Post-meeting processing**: After a meeting, the agent processes notes (and transcripts, if available) to extract decisions, action items, and key discussion points.
- **Action register**: Persistent, queryable register of all captured actions across all tracked meetings.
- **Follow-up automation**: Reminders sent to action owners approaching or past due dates.

**Behavioural Requirements:**

- Pre-reads must include: meeting context, agenda items, relevant background documents (with links), open actions from prior meetings on the same topic, and suggested questions or watch items.
- Meeting summaries must distinguish: confirmed decisions, provisional agreements, deferred items, and new action items.
- Action items must include: description, owner, due date, priority, originating meeting, and current status.
- The agent must handle multiple meeting cadences: Board meetings (quarterly), Board committees, ExCo (weekly/fortnightly), leadership team meetings, and ad-hoc working groups.
- Late-joiner catch-up: if a participant joins a meeting late, the agent provides a real-time summary of what has been discussed so far. **[ASSUMPTION: Real-time transcription integration with Microsoft Teams is available or will be implemented.]**

---

### 5.14 Capability 14: Workflow Orchestration

**Purpose:** Trigger approved downstream workflows from agent outputs — task creation, notifications, document drafting, slide generation, and register updates — integrating with Alinta's existing enterprise systems under strict governance guardrails.

**User Stories:**

- *As the CEO*, after reviewing a meeting summary, I want to say "Create Jira tasks for each of these action items and assign them to the listed owners."
- *As the Board Secretary*, I want to say "Generate a draft board slide deck from this executive summary, using the Alinta board template."
- *As an Executive Assistant*, I want the agent to send a follow-up email to action item owners whose items are overdue.

**Interaction Patterns:**

- **Conversational trigger**: The user instructs the agent to initiate a workflow.
- **Automated trigger**: Certain agent outputs (e.g., new action items, alert escalations) trigger workflows automatically if pre-approved rules are in place.
- **Approval gates**: For actions with external impact (e.g., sending emails, creating tasks in external systems), the agent presents the proposed action and waits for explicit approval.

**Behavioural Requirements:**

- Integration targets include: Microsoft 365 (Outlook, Teams, SharePoint, OneDrive), Jira / ServiceNow (task and ticket creation), Board portal (document upload), CRM (Salesforce or equivalent), and internal registers.
- Every workflow execution must be logged with: trigger source, action taken, target system, outcome, and approving user.
- The agent must never execute an irreversible action (e.g., sending an external email, creating a public record) without explicit human approval.
- Workflows must be versioned and auditable. Changes to workflow definitions require authorised approval.
- Rate limits and guardrails must prevent runaway automation (e.g., a misconfigured rule sending hundreds of emails).

**[ASSUMPTION: Alinta uses Microsoft 365 (Outlook, Teams, SharePoint) as its core productivity suite. Integration will use Microsoft Graph API via MCP-managed tool servers.]**

---

### 5.15 Capability 15: Evaluation & Self-Check Agent

**Purpose:** Before presenting any output to executives, assess the quality, groundedness, policy compliance, and usefulness of the response. Provide confidence scores and highlight uncertainties, assumptions, and data gaps.

**User Stories:**

- *As a Board Director*, I want assurance that every answer I receive from the platform has been checked for accuracy and completeness.
- *As the CTO*, I want to monitor the quality metrics of all agent outputs over time and identify areas requiring improvement.
- *As the CEO*, I want to see a confidence indicator on every response — "high confidence", "medium confidence — limited source data", or "low confidence — recommend human verification".

**Interaction Patterns:**

- **Inline evaluation**: Every agent output passes through the Evaluation Agent before delivery. The evaluation is transparent — confidence scores and any caveats are displayed to the user.
- **Quality dashboard**: Aggregated quality metrics (groundedness, citation accuracy, hallucination rate, user satisfaction) available to the platform owner and CTO.
- **Feedback loop**: Users can flag outputs as incorrect, unhelpful, or inappropriate. This feedback feeds into continuous improvement.

**Behavioural Requirements:**

- The Evaluation Agent assesses every output on the following dimensions:
  - **Groundedness**: Is every claim supported by a retrieved source? Score 0–1.
  - **Citation quality**: Are citations accurate, specific, and verifiable? Score 0–1.
  - **Retrieval relevance**: Were the retrieved documents the most relevant available? Score 0–1.
  - **Policy compliance**: Does the output comply with classification rules, tone guidelines, and prohibited-content policies? Pass/Fail.
  - **Usefulness**: Is the output likely to answer the user's question or serve their intent? Score 0–1.
  - **Completeness**: Does the output address all parts of the user's query? Score 0–1.
- Composite confidence is communicated as: High (all dimensions > 0.8), Medium (any dimension 0.5–0.8), Low (any dimension < 0.5).
- If confidence is Low, the agent must add a caveat: "This response has lower confidence due to [specific reason]. Human verification is recommended before relying on this information for decisions."
- If policy compliance fails, the output is blocked and the user is informed that the query cannot be answered in its current form, with guidance on how to rephrase.
- All evaluation scores are logged for monitoring, trend analysis, and continuous improvement.

---

### 5.16 Capability 16: Voice-First Executive Interface

**Purpose:** Provide natural-language voice interaction for hands-free querying, briefing consumption, email dictation, and meeting preparation — enabling executives to interact with the platform while in transit, between meetings, or away from a screen.

**User Stories:**

- *As the CEO*, I want to ask "What are my top three issues this morning?" via voice while driving to the office, and hear a concise spoken briefing.
- *As a Board Director*, I want to listen to a summary of the board pre-read on my phone during a taxi ride to the board meeting.
- *As the CFO*, I want to dictate "Draft a reply to the Treasurer about the refinancing timeline" and have the platform compose the email using context from recent correspondence.

**Interaction Patterns:**

- **Voice-in, voice-out**: Full conversational loop via speech. User speaks a question or instruction; the platform responds with synthesised speech and optionally a visual summary on screen.
- **Voice-in, text-out**: User speaks; response appears as text (for noisy environments where listening is impractical).
- **Hybrid**: Voice query triggers a detailed text/visual response (e.g., a chart or table) that the user reads on screen.

**Behavioural Requirements:**

- Voice input must support Australian English accents and energy-industry terminology (e.g., "AEMO", "ESOO", "Loy Yang", "NEM", "WEM").
- Speech-to-text latency must be < 500ms. Text-to-speech synthesis must begin within 1 second of response generation.
- The voice interface routes through the same Supervisor Agent and access control layer as text — no security bypass.
- Voice sessions are transcribed and logged for audit (with appropriate privacy notification to the user).
- The platform must support interruption detection — if the user speaks mid-response, the platform stops and listens.
- Wake-word activation is optional and configurable per user.

**[ASSUMPTION: Azure Speech Services or Deepgram will be used for STT/TTS, deployed within the Australian region to comply with data residency requirements.]**

---

### 5.17 Capability 17: Neuro-Symbolic Knowledge Graph Reasoning

**Purpose:** Provide structured multi-hop reasoning over the relationships between Alinta's assets, markets, strategic initiatives, risks, regulations, competitors, and people — combining LLM reasoning with deterministic graph traversal for complex executive queries.

**User Stories:**

- *As the CEO*, I want to ask "Which strategic initiatives are at risk if the AEMC delays the capacity mechanism by 12 months?" and receive a structured answer tracing the dependency chain from regulation through to initiatives.
- *As the Chief Strategy Officer*, I want to query "Show me all assets, projects, and contracts that depend on our Leigh Creek gas supply agreement" and see a visual relationship map.
- *As a Board Director*, I want to understand "If we divest Loy Yang B, what are all the downstream impacts — on our NEM market position, hedging book, emissions profile, and workforce?"

**Interaction Patterns:**

- **Conversational graph queries**: Natural-language questions that require multi-hop traversal are detected by the Supervisor Agent and routed to the Knowledge Graph Reasoning capability.
- **Visual relationship explorer**: Interactive graph visualisation showing entities and relationships, navigable by clicking on nodes.
- **Impact analysis**: "What if" queries that trace cascading effects through the graph.

**Behavioural Requirements:**

- The knowledge graph must represent: assets, markets, strategic initiatives, risks, regulations, competitors, contracts, KPIs, people (executives/stakeholders), and business units.
- Relationships must be typed and directional (e.g., Initiative `depends_on` Asset, Risk `affects` Initiative, Regulation `applies_to` Market).
- Graph traversal must be deterministic — not LLM-generated speculation. The LLM translates natural language to graph queries; the graph engine executes them.
- Results must include the traversal path (which relationships were followed) for transparency.
- The graph must be automatically enriched when new documents are ingested (entity and relationship extraction).
- Access controls apply to graph entities: a user who cannot access Board-Only documents cannot see relationships derived exclusively from Board-Only sources.

---

### 5.18 Capability 18: AI-Powered Board Pack & Slide Generation

**Purpose:** Automatically generate branded PowerPoint/Keynote board presentations from structured platform outputs — briefings, scenario comparisons, KPI summaries, competitive analyses — using Alinta's corporate templates and style guide.

**User Stories:**

- *As the Board Secretary*, I want to say "Generate a board slide deck for the Q2 strategy update, using the executive briefing from this morning and the latest competitive landscape analysis" and receive a formatted PPTX file in Alinta's board template.
- *As the Chief Strategy Officer*, I want to convert a scenario comparison (three options with financials) into a three-slide summary with charts and bullet points.
- *As an Executive Assistant*, I want to generate a set of talking-point slides for the CEO's investor meeting, pulling from the latest financial snapshot and strategic messaging.

**Interaction Patterns:**

- **Conversational trigger**: User instructs the agent to generate a slide deck from specified content. The agent assembles structured content, selects the appropriate template, and produces PPTX.
- **Template library**: Pre-configured templates for common board slide types (executive summary, financial waterfall, competitive matrix, scenario comparison, KPI dashboard, risk heat map).
- **Iterative refinement**: User reviews the generated deck and requests changes ("Move the risk section before financials", "Add a slide on WEM reform").

**Behavioural Requirements:**

- Generated slides must apply Alinta's corporate branding: fonts, colours, logo placement, layout conventions.
- Charts must be rendered as native PowerPoint chart objects (editable), not images.
- Tables must be native PowerPoint tables (editable).
- All slide content must include source citations in speaker notes.
- The agent must respect classification: Board-Only slides are watermarked and carry classification metadata.
- Maximum deck size per generation: 30 slides. Longer requests are split with user confirmation.

**[ASSUMPTION: Alinta's board presentation templates will be provided in PPTX format for integration into the template library.]**

---

### 5.19 Capability 19: Stakeholder & Investor Sentiment Intelligence

**Purpose:** Monitor and analyse sentiment from investors, analysts, media, politicians, regulators, and community stakeholders toward Alinta and the broader energy sector. Alert executives to sentiment shifts and provide talking-point adjustments.

**User Stories:**

- *As the CEO*, I want to know "What is the current media sentiment about Alinta's coal generation fleet?" before a press conference.
- *As the CFO*, I want to understand "How did analysts react to our last earnings update?" with a breakdown by positive, neutral, and negative commentary.
- *As the Chief Strategy Officer*, I want to monitor "What is the community sentiment around our proposed Pilbara expansion?" from local media and social media.

**Interaction Patterns:**

- **Sentiment dashboard**: Real-time sentiment tracking across source categories (media, analyst, social, regulatory, community), segmented by topic and Alinta entity.
- **On-demand queries**: Conversational questions about sentiment on specific topics.
- **Alerts**: Proactive notification when sentiment shifts negatively beyond a threshold (e.g., sudden spike in negative media coverage).
- **Talking-point adjustment**: When sentiment analysis reveals negative themes, the agent proposes adjusted talking points for the Executive Briefing agent.

**Behavioural Requirements:**

- Sentiment sources must include: Australian media (print, online, broadcast), social media (LinkedIn, Twitter/X, Reddit energy communities), analyst reports and commentary, regulatory language analysis (tone of AER/AEMC determinations), community and local media near Alinta assets, and parliamentary debate (Hansard).
- Sentiment must be scored (positive/neutral/negative) and trended over time.
- The agent must distinguish between sentiment about Alinta specifically vs. the sector generally.
- Source credibility weighting: major outlets and analyst houses weighted higher than anonymous social media.
- The agent must not amplify or distort sentiment — it reports what is observed, with source attribution.

---

### 5.20 Capability 20: Long-Term Executive Memory & Personalisation

**Purpose:** Build persistent, evolving profiles for each executive that capture their preferences, communication style, decision patterns, priority topics, and areas of interest — making the platform increasingly effective and personalised with use.

**User Stories:**

- *As the CEO*, I want the platform to learn that I prefer concise bullet points, always want risk expressed in dollar terms, and care especially about WA operations — without me having to repeat these preferences every session.
- *As a Board Director*, I want the platform to notice that I consistently ask about ESG and decarbonisation topics, and proactively surface ESG implications in my responses.
- *As the CFO*, I want my morning briefing to evolve over time to match the specific financial metrics and variances I actually check, rather than a generic template.

**Interaction Patterns:**

- **Implicit learning**: The platform observes query patterns, feedback signals (thumbs-up/down), topic frequency, and format preferences to build a preference profile.
- **Explicit preferences**: Users can set preferences directly: "Always include WEM impacts in my regulatory briefings", "I prefer tables over narrative for financial data."
- **Preference dashboard**: Users can view and edit their personalisation profile.

**Behavioural Requirements:**

- Personalisation profiles are stored in Unity Catalog tables, governed with the same access controls as other platform data.
- Each user's profile is accessible only to that user and the platform admin (for troubleshooting).
- The platform must not use one executive's preferences to influence another executive's experience.
- Personalisation must not override factual accuracy or classification controls — it affects tone, format, emphasis, and proactive topics, not content access.
- Users can reset their profile at any time ("Forget my preferences").
- Preference signals are extracted from: explicit feedback, query frequency by topic, response format engagement (did the user expand the table or read the narrative?), and stated preferences.

---

### 5.21 Capability 21: Continuous AI Red Teaming & Adversarial Security

**Purpose:** Automatically and continuously test all platform agents against adversarial attacks — prompt injection, classification bypass, data exfiltration, policy circumvention, and manipulation — to ensure board-grade security posture.

**User Stories:**

- *As the CTO*, I want a weekly automated adversarial test report showing whether any agent can be tricked into leaking Board-Only content to an ELT-tier user.
- *As the CRO*, I want assurance that the platform has been tested against the OWASP LLM Top 10 vulnerabilities and that no critical vulnerabilities exist.
- *As the CEO*, I want confidence that the platform cannot be manipulated to produce misleading recommendations or bypass approval workflows.

**Interaction Patterns:**

- **Automated testing**: Scheduled red team runs (weekly) that execute a battery of adversarial tests against all agents.
- **Continuous monitoring**: Runtime detection of potential adversarial inputs in production queries.
- **Security dashboard**: CTO-facing view of red team results, vulnerability status, and remediation progress.
- **Incident alerts**: Immediate notification if a production-time adversarial pattern is detected.

**Behavioural Requirements:**

- The red team framework must test against: prompt injection (direct and indirect), classification tier bypass (can a lower-tier user extract higher-tier content?), data exfiltration via tool abuse (e.g., crafting an email that includes confidential content), policy circumvention (bypassing HITL approval gates), model manipulation (causing the agent to produce biased or misleading outputs), and denial-of-service (token exhaustion attacks).
- Tests must be mapped to OWASP LLM Top 10, MITRE ATLAS, and NIST AI Risk Management Framework.
- Results must include: vulnerability description, severity rating, affected agent(s), reproduction steps, and remediation recommendation.
- All red team activities must be logged and distinguished from production traffic in the audit trail.
- The red team agent must operate in an isolated environment — it must not affect production users or data.

---

### 5.22 Capability 22: ESG & Sustainability Reporting Agent

**Purpose:** Automate ESG data collection, emissions tracking (Scope 1/2/3), sustainability metric monitoring, and regulatory compliance reporting for frameworks including NGER, Safeguard Mechanism, AASB S1/S2 (Australian mandatory climate reporting), and voluntary frameworks (GRI, TCFD, CDP).

**User Stories:**

- *As the CEO*, I want to ask "What is our current emissions trajectory vs. our Safeguard Mechanism baseline, and are we on track for compliance?" and receive a data-grounded answer.
- *As a Board Director*, I want the quarterly ESG report to be auto-generated from the latest operational data, with trend analysis and peer comparison.
- *As the Chief Strategy Officer*, I want to model "If we exit coal two years early, how does our emissions profile change and what is the financial impact of reduced Safeguard Mechanism liability?"

**Interaction Patterns:**

- **On-demand queries**: Conversational questions about ESG metrics, emissions, and sustainability performance.
- **Automated reporting**: Scheduled ESG reports aligned with reporting cycles (quarterly for Board, annually for NGER/CDP).
- **Regulatory compliance monitoring**: Alerts when emissions approach or exceed Safeguard Mechanism baselines.
- **Scenario integration**: ESG metrics included in all digital twin / scenario modelling outputs.

**Behavioural Requirements:**

- The agent must integrate data from: AEMO NEM emissions tracker, NGER reported data, internal operational systems (generation output, fuel consumption), renewable energy certificate (REC) registry, and external ESG benchmarks.
- Emissions calculations must follow the NGER methodology and be auditable.
- Peer comparison must use publicly available data (sustainability reports, NGER data, CDP disclosures) from AGL, Origin, EnergyAustralia, and other comparators.
- The agent must track: Scope 1 (direct generation emissions), Scope 2 (purchased electricity), and Scope 3 (supply chain, customer use — where data is available).
- All ESG outputs must include data sources, calculation methodology, and effective date.

---

### 5.23 Capability 23: M&A Due Diligence & Deal Intelligence Agent

**Purpose:** Provide a secure, isolated AI environment for M&A analysis — supporting target screening, document due diligence, valuation benchmarking, synergy modelling, risk identification, and board paper drafting for the most sensitive corporate transactions.

**User Stories:**

- *As the CEO*, I want to ask "Based on our strategic gap analysis, which potential acquisition targets would best address our renewables capacity shortfall in NSW?" and receive a structured long-list with rationale.
- *As the CFO*, I want to upload a target company's financial statements into the secure deal room and ask "Identify the top ten financial risks in these statements."
- *As the Chief Strategy Officer*, I want to generate a board paper recommending an acquisition, incorporating the target profile, strategic rationale, financial impact, risk assessment, and integration considerations.

**Interaction Patterns:**

- **Isolated deal room**: Each M&A process operates in a separate, access-controlled workspace within the platform. Only explicitly authorised users can access each deal room.
- **Document analysis**: Upload and analyse target documents (financials, contracts, operational data) with AI-assisted summarisation and risk flagging.
- **Valuation support**: Benchmarking against comparable transactions and market multiples.
- **Board paper generation**: Structured output suitable for board investment case presentation.

**Behavioural Requirements:**

- Deal room data must be stored in a separate Unity Catalog schema with access restricted to named deal team members.
- Deal room content must not be accessible to the general platform RAG — complete data isolation.
- Access logging must be enhanced: every document view, query, and response in a deal room is logged with the user's identity.
- The agent must not reference deal room content in responses to users outside the deal team.
- When a deal is completed or abandoned, the deal room can be archived (retained for audit) or destroyed (subject to legal hold requirements).
- The M&A agent shares the same LLM infrastructure but operates under a separate system prompt with heightened confidentiality guardrails.

**[ASSUMPTION: Alinta's M&A activity is periodic rather than continuous. The M&A agent is designed for activation when a deal process is initiated, not as an always-on capability.]**

---

### 5.24 Capability 24: Cross-Device Context Persistence

**Purpose:** Enable seamless continuation of conversations and analyses across desktop, tablet, and mobile devices — so executives never lose context when switching devices.

**User Stories:**

- *As the CEO*, I want to start a complex scenario analysis on my laptop, continue reviewing the results on my iPad during a flight, and ask a follow-up question on my phone at the airport.
- *As a Board Director*, I want to read a board pre-read summary on my desktop, bookmark a question, and pick it up on my tablet in the board meeting.

**Interaction Patterns:**

- **Session persistence**: Conversations are tied to the user's identity, not the device. Switching devices resumes the conversation where it left off.
- **Bookmarking**: Users can bookmark any conversation point for return.
- **Sync indicator**: Visual indicator showing "Continuing from [device] at [time]" when resuming on a new device.

**Behavioural Requirements:**

- All conversation state is stored server-side (Unity Catalog), not on-device.
- Device switching must be seamless — no re-authentication required within the session timeout window (biometric re-authentication acceptable).
- Rich content (charts, tables, slide decks) rendered appropriately for each device form factor.
- Offline viewing of previously loaded content is desirable but not required for MVP.

---

### 5.25 Capability 25: Autonomous Governance Tiering

**Purpose:** Classify every platform capability on a five-tier autonomy scale — from fully supervised to fully autonomous — with governance guardrails calibrated to each tier, providing a framework for progressive autonomy as executive trust builds.

**User Stories:**

- *As the CTO*, I want a clear framework that defines which platform capabilities can act autonomously, which require human approval, and which are advisory only.
- *As a Board Director*, I want assurance that no AI capability can take consequential action without appropriate human oversight, and that the governance framework is regularly reviewed.
- *As the CEO*, I want to progressively increase the autonomy of proven, trustworthy capabilities (e.g., from "supervised execution" to "guided autonomy" for daily briefing generation) as confidence builds.

**Autonomy Tiers:**

| Tier | Name | Description | Example Capabilities |
|------|------|-------------|---------------------|
| 1 | Advisory Only | Agent provides information and analysis. No action capability. Human decides and acts. | Document Q&A, Strategic Gap Analysis, Competitive Analysis. |
| 2 | Supervised Execution | Agent proposes an action and executes only after explicit human approval for each instance. | Email drafting (send after approval), Jira task creation, Board slide generation. |
| 3 | Guided Autonomy | Agent executes pre-approved categories of actions within defined guardrails. Exceptions require human approval. | Scheduled digest delivery, pre-read generation, KPI dashboard refresh. |
| 4 | Delegated Authority | Agent acts autonomously within a defined mandate. Human reviews periodically. Escalates edge cases. | Signal detection and prioritisation, action item reminder emails, KPI anomaly classification. |
| 5 | Fully Autonomous | Agent operates independently with periodic audit review. Reserved for low-risk, well-validated capabilities. | Document classification at ingestion, embedding pipeline execution, log aggregation. |

**Behavioural Requirements:**

- Each capability in the platform must have an assigned autonomy tier, documented in the agent registry.
- Tier assignment requires approval from the CTO and the relevant business sponsor.
- Tier promotion (increasing autonomy) requires evidence: evaluation scores above threshold for 90 consecutive days, zero policy compliance failures, and executive sponsor sign-off.
- Tier demotion (decreasing autonomy) can be immediate if a policy failure or security incident occurs.
- The autonomy tier of each capability is visible to users in the platform UI.

---

### 5.26 Capability 26: Board Decision Audit Trail & Decision Registry

**Purpose:** Maintain a structured, queryable registry of all board and executive committee decisions — linking each decision to the supporting analysis, agents and documents involved, alternatives considered, risk assessment, approvers, and outcome tracking.

**User Stories:**

- *As a Board Director*, I want to ask "What did the Board decide about the Pilbara expansion, and what analysis supported that decision?" and receive the full decision lineage — from the agent-generated briefing through the board paper to the recorded resolution.
- *As the Board Secretary*, I want an automatically maintained register of all board and committee decisions with tracking of follow-through actions.
- *As the CEO*, I want to query "How many strategic decisions from the last 12 months have been fully implemented vs. still in progress?"

**Interaction Patterns:**

- **Automatic capture**: When the Meeting Intelligence agent identifies a decision in board or ExCo meeting notes, it creates a decision record in the registry.
- **Manual augmentation**: The Board Secretary or Chief of Staff can enrich decision records with formal resolution numbers, voting outcomes, and document references.
- **Queryable register**: Conversational queries over the decision register ("Show me all capital allocation decisions above $50M in the last two years").
- **Decision lineage**: Each decision links to: the agent-generated analysis that informed it, the board paper(s), the meeting summary, the recorded vote/resolution, the assigned actions, and the current implementation status.

**Behavioural Requirements:**

- Decision records must include: decision ID, date, meeting, description, decision type (strategic/financial/operational/governance), outcome (approved/rejected/deferred), supporting documents, agent analyses referenced, alternatives considered, risk assessment, owner, and implementation status.
- The registry must support classification — some decisions are Board-Only, others are ExCo.
- Decision records are immutable once finalised (append-only; corrections are recorded as amendments).
- Integration with the action register: decisions that generate action items are linked bidirectionally.
- Regulatory and audit utility: the registry provides evidence for how decisions were informed and made.

---

### 5.27 Capability 27: Multi-Model Intelligent Routing

**Purpose:** Dynamically route queries across a diverse portfolio of AI models — selecting the optimal model for each task based on complexity, required reasoning depth, latency sensitivity, cost, and task type — going beyond simple primary/fallback to true intelligent orchestration.

**User Stories:**

- *As the CTO*, I want the platform to automatically route simple factual lookups to a fast, inexpensive model while sending complex multi-hop strategic reasoning to the most capable model — without users needing to know or care.
- *As the CFO*, I want my quick question "What is Q3 capex?" answered in under 2 seconds (fast model) while my follow-up "Explain the variance drivers and model three remediation scenarios" uses the most capable model (10-15 seconds acceptable).

**Interaction Patterns:**

- **Transparent to users**: Routing is invisible. Users experience consistent quality — simpler queries are just faster and cheaper.
- **Admin dashboard**: CTO/platform admin can view routing decisions, model utilisation, cost distribution, and quality metrics by model.
- **Policy configuration**: Routing policies are configurable by persona, agent, and task type.

**Behavioural Requirements:**

- The routing engine must classify each query/task on dimensions: complexity (simple lookup vs. multi-step reasoning), task type (Q&A, summarisation, code generation, analysis, creative drafting), latency sensitivity (interactive vs. batch), and security sensitivity (board-tier content may require specific model providers).
- Model portfolio must include at minimum: a frontier reasoning model (e.g., Claude 3 Opus / Claude 4), a high-quality general model (e.g., Claude 3.5 Sonnet), a fast/efficient model (e.g., Claude Haiku or Llama 3.1), a code-specialised model (for simulation parameter generation and data analysis), and dedicated embedding and re-ranking models.
- Routing decisions must be logged for cost attribution and quality analysis.
- If the selected model produces a low-quality output (detected by the Evaluation Agent), the system may automatically retry with a more capable model (with latency trade-off communicated to the user).
- Cost optimisation target: 30-40% reduction in token spend vs. routing all queries to the frontier model, with < 5% quality degradation on evaluation benchmarks.

---

### 5.28 Capability 28: Synthetic Board-Level Document & Data Generation

**Purpose:** Generate a comprehensive corpus of realistic synthetic documents and structured datasets that mirror Alinta Energy's actual document landscape — for platform development, ingestion pipeline testing, RAG evaluation, agent quality tuning, executive demonstrations, and adversarial red-team testing. This capability ensures the platform can be developed, tested, and showcased without requiring access to real board-confidential data during early phases.

**User Stories:**

- *As the platform engineering team*, we need a realistic corpus of 100+ board-level documents across all supported formats so we can develop and test the ingestion pipeline, chunking strategies, and classification logic end-to-end.
- *As the CTO*, I want to demo the platform to the Board using synthetic but realistic Alinta content — so directors can see how the system works with familiar asset names, market contexts, and document structures.
- *As the evaluation team*, we need documents with companion Q&A pairs (known-correct answers) so we can automatically measure Q&A agent accuracy, retrieval precision, and hallucination rate.
- *As the red team agent*, I need synthetic documents at every classification tier (Board-Only through Public) to test that access control enforcement works correctly across all agents.

**Document Types to Generate:**

| Document Type | Formats | Classification Tier | Example Content |
|---------------|---------|--------------------:|-----------------|
| Board papers and board packs | PDF, DOCX | Board-Only | Strategic review, investment case for Yandin expansion, CEO report to the Board. |
| Board minutes and resolutions | PDF, DOCX | Board-Only | Minutes of Q2 2025 Board meeting with decisions, votes, and action items. |
| Financial forecasts and budgets | Excel, PDF | ExCo, Board-Only | FY26 budget by business unit, quarterly reforecast, variance commentary. |
| Strategy documents and investment cases | DOCX, PDF, PPTX | ExCo, Board-Only | Five-year strategic plan, renewables acceleration business case. |
| M&A pipeline and due diligence | PDF, DOCX | Board-Only | Target screening memo, preliminary financial analysis for a fictional acquisition. |
| Regulatory submissions and market position papers | PDF | ExCo, ELT | AEMC rule change submission, AEMO ISP response, Safeguard Mechanism compliance plan. |
| Competitive intelligence and analyst reports | PDF | ExCo, ELT | Competitor profile (synthetic AGL, Origin), sector analyst note. |
| Energy market analytics and trading reports | Excel, PDF | ELT, BU-Specific | NEM Q2 2025 market review, WEM capacity mechanism analysis, trading desk weekly report. |
| ESG, sustainability, and decarbonisation reports | PDF, PPTX | ExCo, ELT | Annual sustainability report draft, Scope 1 emissions trajectory analysis. |
| Executive briefings and CEO updates | DOCX, PPTX | ExCo | CEO weekly update, stakeholder meeting talking points, investor briefing pack. |
| Meeting notes and action registers | DOCX | ExCo, ELT | ExCo meeting summary with decisions and action items, Board committee minutes. |
| Correspondence and memos | PDF | Confidential, Internal | Executive memo on organisational restructure, internal policy announcement. |

**Structured Data to Generate (Delta Lake Tables):**

| Dataset | Key Fields | Volume |
|---------|-----------|--------|
| Financial data | revenue, EBITDA, capex, opex, net_debt, cash_flow — by BU, by period (monthly, FY15–FY27) | ~5,000 rows |
| KPI time series | plant_availability, capacity_factor, forced_outage_rate, customer_churn, NPS, emissions_intensity — by asset/BU, by month | ~10,000 rows |
| NEM/WEM market data | region, timestamp, price, demand, generation_by_fuel, interconnector_flow — 5-minute intervals, 12 months | ~1M rows |
| Asset register | asset_name, type, capacity_mw, fuel, location, state, market, commissioning_date, status | ~30 rows |
| Risk register | risk_id, category, description, likelihood, consequence, rating, owner, mitigation, status | ~50 rows |
| Action items | action_id, description, owner, due_date, source_meeting, status, priority | ~200 rows |
| Decision register | decision_id, date, committee, description, outcome, owner, implementation_status | ~100 rows |

**Metadata and Classification Requirements:**

- Every synthetic document must carry the full metadata schema defined in Section 8.1 (`document_type`, `classification`, `business_area`, `effective_date`, `version`, `owner`, `author`, etc.).
- Documents must span all classification tiers to enable end-to-end access control testing.
- Temporal spread: documents should span a 2-year period (FY24–FY26) with appropriate versioning and supersession chains (e.g., Q1 forecast superseded by Q2 reforecast).
- Related documents must cross-reference each other (e.g., a board paper references the financial forecast, which references the market analysis).

**Evaluation Dataset Requirements:**

- Each synthetic document must include companion Q&A pairs — questions with known-correct answers extracted from the document content.
- Minimum 5 Q&A pairs per document, covering: factual lookups, cross-reference queries, temporal queries ("What changed between the Q1 and Q2 forecasts?"), and reasoning queries ("What are the top risks to the renewables pipeline?").
- Q&A pairs stored in a structured evaluation table with: question, expected_answer, source_document_id, source_section, difficulty (easy/medium/hard).
- Evaluation datasets serve as the "golden test set" for automated Q&A agent accuracy measurement.

**Implementation Approach:**

- **Unstructured documents (PDF)**: Generated using LLM-based content generation (Databricks `generate_pdf_documents` tool) with Alinta-specific prompts describing the document type, structure, and content domain. The LLM produces realistic board-level prose, tables, and exhibits.
- **Structured documents (DOCX, PPTX)**: Generated using `python-docx` and `python-pptx` libraries with LLM-generated content injected into professional document templates. Section headings, tables, and formatting match real board document conventions.
- **Spreadsheets (Excel)**: Generated using `openpyxl` with formulae, charts, conditional formatting, and multi-sheet workbooks (e.g., summary tab, BU breakdown tabs, assumptions tab).
- **Structured data (Delta Lake)**: Generated using Faker and PySpark (Databricks `databricks-synthetic-data-generation` skill) with realistic distributions, non-linear trends, seasonality (NEM prices), and referential integrity across tables.
- **Metadata**: Assigned programmatically during generation, conforming to the Section 8.1 schema. Classification tiers distributed across the corpus to cover all access control scenarios.
- **Tagging**: All synthetic artefacts carry `is_synthetic: true` and `source_system: synthetic` metadata to prevent confusion with real data. The ingestion pipeline processes synthetic documents identically to real documents.

**Behavioural Requirements:**

- Synthetic content must be realistic enough to test all platform capabilities meaningfully — the Q&A agent should be able to answer questions, the financial agent should find variances, the competitive agent should extract competitor profiles.
- Synthetic content must be clearly fictional — it must not be mistaken for real Alinta data if encountered outside the platform. All synthetic documents carry a "SYNTHETIC — FOR TESTING ONLY" watermark (removable for clean demo presentations with CTO approval).
- The generation pipeline must be repeatable and version-controlled. A specific seed produces the same corpus, enabling reproducible evaluation benchmarks.
- The corpus must be regenerable when the document schema, agent prompts, or evaluation methodology changes.

**[ASSUMPTION: Synthetic data uses fabricated but plausible Alinta Energy asset names (Loy Yang B, Yandin Wind Farm, Newman Power Station, Wagerup Power Station, etc.) and market contexts. No real Alinta data is used. All financial figures are fictional.]**

---

## 6. Non-Functional Requirements

### 6.1 Security & Privacy

**Encryption:**
- All data at rest encrypted using AES-256 via the cloud provider's managed encryption service (Azure Storage Service Encryption or AWS S3 SSE-KMS).
- All data in transit encrypted using TLS 1.2 or higher.
- Customer-managed encryption keys (BYOK) for board-tier data stored in Unity Catalog-managed storage. **[ASSUMPTION: Alinta's security policy requires BYOK for the most sensitive data classifications.]**

**Identity & Access:**
- All platform access authenticated via Alinta's enterprise identity provider (Azure Entra ID / Azure AD) with multi-factor authentication enforced.
- Role-based access control (RBAC) mapped to Unity Catalog groups, synchronised from Entra ID security groups.
- Service principal identities for system-to-system integrations (e.g., M365 Graph API, board portal), with least-privilege scoping and credential rotation policies.
- Session management: idle timeout of 15 minutes for interactive sessions; session tokens non-transferable.

**Least Privilege:**
- Every agent, tool, and integration operates with the minimum permissions required for its function.
- Access to board-tier data requires explicit group membership — no implicit inheritance from broader organisational roles.
- Delegated access for Executive Assistants is explicitly granted, time-bounded, and fully audited.

**Confidential Computing:**
- Evaluate Azure Confidential Computing (SGX enclaves or AMD SEV-SNP) for the most sensitive workloads — board paper processing, M&A document analysis. **[ASSUMPTION: This will be evaluated during Phase 1 for feasibility and performance impact; not a hard requirement for MVP.]**

**Data Residency:**
- All data must reside within Australia (Azure Australia East / Australia Southeast, or equivalent AWS Sydney region). No data replication outside Australian boundaries.
- LLM inference: if using external model endpoints (e.g., Anthropic API), confirm that no prompt or response data is retained by the provider and that processing occurs within jurisdictions acceptable under Alinta's data residency policy. **[ASSUMPTION: Databricks Model Serving endpoints within the Australian region will be the primary inference path. External endpoint usage, if any, will be governed by the AI Gateway with data residency enforcement.]**

### 6.2 Compliance & Governance

**Australian Privacy Act (1988):**
- The platform processes personal information of Alinta employees (names, roles, email addresses, calendar data) and potentially personal information referenced in documents (e.g., customer data in board papers). All processing must comply with the Australian Privacy Principles (APPs).
- Data minimisation: collect and retain only the personal information necessary for the platform's function.
- Consent and notification: ensure employees are informed about how their data is used within the platform (e.g., meeting transcription, email analysis for executive assistant).

**Critical Infrastructure (SOCI Act 2018):**
- Alinta Energy is a critical infrastructure entity under the Security of Critical Infrastructure Act. The platform must comply with positive security obligations, including risk management program requirements.
- Cyber incident reporting obligations must be considered for the platform as a component of Alinta's critical infrastructure.

**Internal Risk & Audit:**
- All agent interactions, retrievals, generations, tool invocations, and workflow executions must produce immutable audit logs.
- Audit logs must be queryable by internal audit and risk functions.
- The platform must support periodic access reviews (quarterly) and compliance reporting.
- Model governance: all models (LLMs, embedding models, simulation models) must have documented model cards, approval records, and retirement schedules.

### 6.3 Performance

| Workload | Latency Target | Notes |
|----------|---------------|-------|
| Interactive Q&A (single question) | First token < 2s; complete response < 15s | For typical queries against the document corpus. |
| Multi-step agent workflow (e.g., strategic gap analysis) | < 60s for complete output | May involve multiple retrieval and reasoning steps. |
| Executive briefing generation | < 5 minutes | For synthesis across 20–50 source documents. |
| KPI dashboard refresh | < 10s | Near-real-time for connected data sources. |
| Market simulation (single scenario) | < 15 minutes | Depends on simulation complexity; must provide progress indication. |
| Market simulation (batch — 100 scenarios) | < 4 hours | Leveraging distributed compute (PySpark). |
| Scheduled digest generation | Completed by 7:00 AM AEST | Daily/weekly digests generated overnight. |

### 6.4 Reliability & Resilience

**Availability target:** 99.5% uptime for the interactive platform during business hours (7:00 AM – 9:00 PM AEST, Monday to Friday). 99.0% uptime for batch and scheduled workloads.

**Failover strategy:**
- Databricks workspace configured for zone-redundant deployment within the primary Australian region.
- If the primary LLM endpoint is unavailable, the AI Gateway routes to a fallback model (e.g., from Claude to an alternative provider) with degraded-capability notification to the user.
- If the vector search service is unavailable, the Q&A agent degrades gracefully: "Document search is temporarily unavailable. I can still help with questions I can answer from my general knowledge, but I cannot cite specific Alinta documents."

**Behaviour under dependency failures:**

| Dependency | Failure Behaviour |
|------------|-------------------|
| LLM endpoint (primary) | AI Gateway routes to fallback model; user notified of potential quality difference. |
| Vector search | Q&A and retrieval-dependent agents return "document search unavailable" with graceful degradation. |
| External data API (AEMO, news) | Scheduled ingestion retries with exponential backoff; alerts generated if stale > 24 hours. |
| M365 / Graph API | Executive assistant actions queued; user notified of delay. Retried automatically. |
| Simulation compute cluster | Simulation jobs queued; estimated wait time communicated. Auto-scale if within budget. |

**Disaster recovery:**
- RPO (Recovery Point Objective): < 1 hour for all platform data (Delta Lake with time travel provides continuous backup).
- RTO (Recovery Time Objective): < 4 hours for full platform restoration to a secondary region if required.
- DR strategy: Delta Lake replication to a secondary Australian region. Platform infrastructure defined as code (Databricks Asset Bundles / Terraform) for rapid re-deployment.

### 6.5 Explainability & Transparency

- Every agent response must include the reasoning path: which documents were retrieved, which tools were invoked, what logic was applied.
- For simulation outputs, all assumptions must be explicitly listed and the sensitivity to each major assumption must be available on request.
- Users must be able to drill into any cited source to verify claims.
- The platform must maintain a "model card" for each AI component, documenting its purpose, training data (for fine-tuned models), known limitations, and evaluation results.

### 6.6 Cost Governance

**Token budgets:**
- Per-persona daily token limits enforced by the AI Gateway:
  - Board Directors: 50,000 tokens/day (anticipated light interactive use).
  - CEO: 200,000 tokens/day.
  - C-suite: 150,000 tokens/day each.
  - EGMs / Leads: 100,000 tokens/day each.
  - Executive Assistants: 150,000 tokens/day (high usage for meeting intelligence and communications).
- Scheduled/batch workloads (digests, simulations) have separate budgets managed at the platform level.

**Rate limiting:**
- Maximum 20 concurrent queries per persona group to prevent resource exhaustion.
- Simulation jobs limited to 50 concurrent scenarios to manage compute costs.

**Cost attribution:**
- All token consumption, compute usage, and storage costs attributed to the originating persona, agent, and use case.
- Monthly cost reports provided to the CTO/CDO and CFO.
- Cost anomaly alerts: if daily spend exceeds 2x the trailing 7-day average, an alert is generated for platform operations.

**Optimisation policies:**
- Prompt caching for frequently asked questions and common retrieval patterns.
- Tiered model routing: simpler queries routed to smaller/faster models; complex multi-step reasoning routed to the most capable model. AI Gateway manages this routing based on query classification.
- Embedding generation is a one-time cost per document version; re-embedding only on document update.

---

## 7. Technical Architecture

### 7.1 Architecture Overview

The Platform is structured as nine interconnected layers, each implemented on Databricks-native services where possible, with external integrations managed through governed tool servers.

**Layer 1 — Data Ingestion & Processing:** Ingest documents and structured data from internal and external sources into Delta Lake, with classification, chunking, embedding, metadata enrichment, and entity/relationship extraction for the knowledge graph. Includes a synthetic data generation pipeline that produces realistic board-level documents (PDF, DOCX, PPTX, Excel) and structured datasets into the same Unity Catalog Volumes and Delta Lake tables targeted by production ingestion — tagged with `source_system: synthetic` to prevent confusion with real data.

**Layer 2 — Knowledge Repository & RAG:** Store and manage document chunks, embeddings, and metadata in Unity Catalog-governed tables and Databricks Vector Search indexes, supporting hybrid retrieval (vector + keyword + metadata) and graph-powered reasoning via a neuro-symbolic knowledge graph.

**Layer 3 — Knowledge Graph & Reasoning:** Property graph stored in Delta Lake representing entities (assets, markets, initiatives, risks, regulations, competitors, people) and their relationships. Supports deterministic multi-hop traversal for complex executive queries, combined with LLM reasoning for natural-language graph query translation.

**Layer 4 — Agent Orchestration:** A multi-agent system with a Supervisor Agent that routes user requests to specialised agents (22 agents including Supervisor), each with defined tools, prompts, guardrails, and autonomy tier classification, implemented using Databricks Mosaic AI Agent Bricks with graph-based orchestration.

**Layer 5 — LLM Serving & Multi-Model Intelligent Routing:** Databricks Model Serving endpoints for hosted models and AI Gateway for intelligent multi-model routing (20+ models across reasoning, generation, embedding, code, and re-ranking tasks), with guardrails, rate limiting, cost governance, and task-aware model selection.

**Layer 6 — Integration & Tool Layer:** MCP-managed tool servers providing agents with access to enterprise systems (M365, board portal, CRM, market data, ESG data feeds, sentiment sources), simulation engines, slide generation engines, voice services (STT/TTS), and internal APIs.

**Layer 7 — Voice & Multi-Modal Interface:** Speech-to-text and text-to-speech services enabling voice-first interaction, integrated with the Supervisor Agent via the same security and routing layer as text interactions. Cross-device session persistence ensuring seamless context continuation.

**Layer 8 — Security & Adversarial Defence:** Continuous AI red teaming framework executing automated adversarial tests against all agents (prompt injection, classification bypass, data exfiltration, policy circumvention), with runtime adversarial input detection and CTO-facing security dashboard.

**Layer 9 — Observability, Governance & Decision Registry:** End-to-end tracing (MLflow), Lakehouse monitoring, audit logging, quality evaluation, compliance reporting, autonomous governance tiering framework, and the Board Decision Audit Trail and Decision Registry.

### 7.2 Data Ingestion & Processing Pipeline

**Source systems and ingestion patterns:**

| Source | Format | Ingestion Pattern | Frequency |
|--------|--------|-------------------|-----------|
| Board portal | PDF, DOCX, PPTX | API pull or file drop to cloud storage; Auto Loader picks up new files. | On publication (event-driven). |
| SharePoint / OneDrive | PDF, DOCX, PPTX, XLSX | Microsoft Graph API via scheduled pull. | Daily or on-change. |
| Email attachments (exec comms) | PDF, DOCX, EML | Graph API with consent-based access for opted-in executives. | Near-real-time. |
| Financial systems | Structured (CSV, Parquet, API) | Direct ingestion into Delta Lake via Databricks connectors. | Daily / hourly. |
| AEMO / regulatory publications | PDF, CSV, XML | Web scraping or API integration; scheduled pipeline. | Daily. |
| News & analyst feeds | JSON, RSS, API | Streaming or micro-batch ingestion. | Near-real-time. |
| Market data (NEM/WEM) | CSV, API | AEMO MMS / WEM data feeds into Delta Lake. | 5-minute intervals for dispatch data. |
| CRM / customer data | Structured | Lakehouse Federation or direct ETL. | Daily. |
| Operational / asset data | Structured | Historian / SCADA integration or ETL. | Hourly or sub-hourly. |

**Document processing pipeline:**

1. **Raw ingestion**: Documents land in a Unity Catalog Volume (raw zone) via Auto Loader.
2. **Extraction**: High-fidelity text and structure extraction using Databricks Document AI or equivalent. Tables, headers, lists, and page structure are preserved. PDFs with scanned content use OCR.
3. **Classification**: Each document is classified (Board-Only, ExCo, ELT, etc.) based on metadata (source system, folder path, author) and content analysis. Human review is required for ambiguous classifications.
4. **Metadata enrichment**: Document type, author, business area, effective date, superseded-by reference, and version number are extracted or assigned.
5. **Chunking**: Documents are split into semantically coherent chunks using a hierarchical strategy — section-level chunks for narrative content, table-level chunks for tabular data, and page-level chunks for appendices. Each chunk retains its parent document metadata and positional context (section title, page number).
6. **Embedding**: Chunks are embedded using a governed embedding model (e.g., Databricks-hosted BGE-large or equivalent). Embeddings are stored in Unity Catalog tables alongside chunk text and metadata.
7. **Vector index sync**: Embeddings are synced to Databricks Vector Search via Delta Sync Index for real-time retrieval.
8. **Lineage**: The full pipeline is tracked in Unity Catalog lineage — from source document to chunks to embeddings to vector index.

### 7.3 RAG Layer

**Hybrid retrieval strategy:**

The RAG layer combines three retrieval mechanisms to maximise precision and recall:

1. **Vector search (semantic)**: Databricks Vector Search with cosine similarity over document chunk embeddings. Returns semantically relevant chunks even when the query uses different terminology than the source.
2. **Keyword search (lexical)**: Full-text search over chunk text for exact term matching. Critical for proper nouns (asset names, contract references, regulatory instrument numbers), financial figures, and precise terminology.
3. **Metadata filtering**: Pre-retrieval filters on classification tier, document type, business area, date range, and document status. Ensures classification-appropriate results and temporal relevance.

**Retrieval flow:**
1. User query is received with user identity and access tier.
2. Classification filter is applied: only chunks at or below the user's access tier are eligible.
3. Query is executed simultaneously against vector search and keyword search.
4. Results are merged, de-duplicated, and re-ranked using a cross-encoder re-ranker.
5. Top-K chunks (configurable; default K=15 for Q&A, K=30 for synthesis tasks) are returned with metadata.
6. Retrieved chunks are passed to the generating LLM as context.

**Temporal and version-aware retrieval:**
- Each chunk carries an `effective_date` and `superseded_by` reference.
- By default, the retrieval layer prefers the most recent version of a document. If the user asks about a historical position, the agent includes date-qualified retrieval ("as of November 2025").
- Forecast documents carry a `forecast_vintage` attribute to distinguish between successive forecast iterations.

### 7.4 Agent Orchestration Layer

**Architecture pattern:** The platform uses a **Supervisor Agent** pattern implemented with Databricks Mosaic AI Agent Bricks. The Supervisor Agent receives all user interactions and routes them to the appropriate specialised agent(s) based on intent classification.

**Orchestration flow:**

1. User message arrives at the Supervisor Agent.
2. The Supervisor classifies the intent (e.g., document Q&A, competitive analysis, scenario request, email drafting) and identifies the target agent(s).
3. For single-agent tasks, the Supervisor delegates to the specialist agent and returns the result.
4. For multi-agent tasks (e.g., "Compare our strategy to competitors and recommend options" requires Strategic Gap + Competitive + Recommendation agents), the Supervisor orchestrates a graph-based workflow — sequential or parallel execution as appropriate.
5. All agent outputs pass through the Evaluation Agent before being returned to the user.
6. The Supervisor manages conversation context, session memory, and persona-specific behaviour.

**Agent graph orchestration:** Complex workflows are defined as directed acyclic graphs (DAGs) using a LangGraph-style framework within Agent Bricks. Each node in the graph is an agent or tool invocation. Edges define data flow and conditional routing. This enables:
- Parallel execution of independent retrieval and analysis steps.
- Conditional branching based on intermediate results (e.g., if retrieval confidence is low, invoke additional search strategies before proceeding).
- Human-in-the-loop checkpoints at defined points in the workflow.

**Shared tools and services:** All agents access a common set of tools via the MCP tool layer:
- Document retrieval (RAG)
- Structured data query (SQL over Delta Lake)
- Web search (for external intelligence, with guardrails)
- Simulation API
- Email/calendar API (M365 Graph)
- Task creation API (Jira/ServiceNow)
- Calculator/analytics tools
- Dashboard rendering

### 7.5 LLM Serving & AI Gateway

**Databricks Model Serving:**
- Primary LLM: Claude 3.5 Sonnet (or Claude 3 Opus for the most complex reasoning tasks) hosted via Databricks External Model endpoints or direct API integration.
- Embedding model: BGE-large-en-v1.5 (or equivalent) hosted on Databricks Model Serving for low-latency, high-throughput embedding generation.
- Re-ranker model: Cross-encoder model hosted on Model Serving for retrieval result re-ranking.

**AI Gateway configuration:**

| Function | Configuration |
|----------|---------------|
| Provider abstraction | Route between Claude, GPT-4o, Llama 3.1 (as fallback) based on availability, cost, and task complexity. |
| Guardrails | Input/output content filters: PII detection, profanity filter, off-topic detection, prompt injection defence. |
| Rate limiting | Per-persona and per-agent-type rate limits (see Section 6.6). |
| Token budgets | Daily token caps per persona group enforced at the gateway. |
| Usage tracking | Every request logged with: user, agent, model, token count (input/output), latency, and cost. |
| Cost governance | Automatic model downgrade if daily budget is 80% consumed (e.g., route from Opus to Sonnet). |
| Fallback routing | If primary model is unavailable (> 5s timeout), route to fallback model with user notification. |

### 7.6 Simulation Engine Integration

**Architecture:**
- Simulation workloads run on Databricks compute clusters (PySpark jobs for parallelised scenario execution).
- Simulation models are registered in Unity Catalog as versioned model artefacts (MLflow model registry).
- Input assumptions are stored in Delta Lake tables with versioning.
- Simulation results are written to Delta Lake tables for analysis, comparison, and historical reference.

**Integration with agents:**
- The Digital Twin and Market Simulation agents invoke simulation jobs via a Simulation API tool (MCP-managed).
- The agent translates natural-language scenario descriptions into structured parameter sets, validates them against the assumption schema, and submits the simulation job.
- Results are retrieved from Delta Lake and presented to the user with visualisations and explanations.

**External simulation tool integration:**
- If Alinta uses PLEXOS or other commercial simulation tools, integration will be via API or batch file exchange, with results ingested into Delta Lake for unified analysis.

### 7.7 Enterprise System Integration

| System | Integration Method | Purpose |
|--------|--------------------|---------|
| Microsoft 365 (Outlook, Teams, SharePoint) | Microsoft Graph API via MCP tool server | Email drafting, calendar access, meeting transcripts, document access. |
| Board portal | API or file sync | Board paper ingestion, minute upload. |
| CRM (Salesforce or equivalent) | Lakehouse Federation or API | Customer data for retail analysis. |
| Jira / ServiceNow | REST API via MCP tool server | Action item and task creation. |
| AEMO MMS | Data feed ingestion | NEM market data (prices, dispatch, constraints). |
| AEMO / AER / AEMC publications | Web scrape or RSS | Regulatory intelligence. |
| Financial systems (ERP) | ETL or Lakehouse Federation | Budget, actuals, forecast data. |
| SCADA / historian | ETL or streaming | Asset operational data. |
| News / analyst feeds | API ingestion | External intelligence. |

### 7.8 Observability & Telemetry

**MLflow tracing:** Every agent interaction — from user query to final response — is traced end-to-end in MLflow. Traces capture:
- User query and metadata (persona, access tier, timestamp).
- Intent classification result.
- Agent(s) invoked and their parameters.
- Retrieval queries, results, and relevance scores.
- Tool invocations and their outcomes.
- LLM prompts (sanitised), responses, and token counts.
- Evaluation Agent scores.
- Final response delivered to the user.

**Lakehouse monitoring:**
- Data pipeline health: ingestion lag, processing errors, document counts.
- Vector index freshness: time since last sync.
- Model endpoint health: latency, error rates, throughput.
- Compute utilisation: cluster usage, cost tracking.

**Alerting:**
- PagerDuty or equivalent integration for platform operations alerts.
- Slack/Teams notifications for non-critical operational events.
- Executive-facing quality alerts (e.g., sustained drop in evaluation scores) routed to the CTO.

### 7.9 Voice & Multi-Modal Interface Layer

**Speech-to-text (STT):** Incoming voice is transcribed via Azure Speech Services or Deepgram, deployed within the Australian region. STT output is passed to the Supervisor Agent as text, indistinguishable from typed input (except for a `modality: voice` metadata tag).

**Text-to-speech (TTS):** Agent responses are synthesised to speech via TTS for voice-out interactions. Voice selection is configurable per user. Responses are optimised for spoken delivery (shorter sentences, fewer tables, more narrative).

**Voice routing:** Voice interactions pass through the same Supervisor Agent, access control, and Evaluation Agent pipeline as text interactions. No separate security path.

**Cross-device session management:** Conversation state is stored server-side in Unity Catalog tables keyed by user identity and session ID. When a user switches devices, the session is resumed with full context. Rich content (charts, tables) is re-rendered for the new device form factor.

### 7.10 Knowledge Graph Engine

**Storage:** The knowledge graph is stored as two Delta Lake tables in Unity Catalog:
- `knowledge_graph.entities`: Node table with entity_id, entity_type, name, attributes (JSON), classification, source_document_ids.
- `knowledge_graph.relationships`: Edge table with relationship_id, source_entity_id, target_entity_id, relationship_type, attributes (JSON), confidence, source_document_ids.

**Entity and relationship extraction:** When new documents are ingested, an extraction pipeline (LLM-based with structured output) identifies entities and relationships. Extracted entities are matched against existing graph nodes (deduplication via fuzzy matching and entity resolution). New entities and relationships are added; existing ones are updated with additional source references.

**Query execution:** Natural-language graph queries are translated to structured graph traversal operations by a specialised LLM call (NL-to-GQL). The graph engine executes deterministic traversals and returns structured results. The LLM then narrates the results for the user.

**Access control:** Graph entities inherit the classification of their source documents. A user querying the graph only sees entities derived from documents at or below their access tier.

### 7.11 Multi-Model Intelligent Routing Engine

**Architecture:** The routing engine sits within the AI Gateway layer and classifies each incoming query/task along four dimensions:

1. **Complexity**: Simple lookup, moderate analysis, complex multi-step reasoning.
2. **Task type**: Q&A, summarisation, drafting, code/SQL generation, analysis, creative.
3. **Latency class**: Interactive (< 5s), standard (< 30s), batch (minutes acceptable).
4. **Security class**: Board-tier (may restrict to specific providers), standard.

**Model portfolio:**

| Model Role | Example Models | Use Case |
|------------|---------------|----------|
| Frontier reasoning | Claude 3 Opus / Claude 4 | Complex strategic reasoning, multi-hop analysis, recommendation generation. |
| High-quality general | Claude 3.5 Sonnet | Standard Q&A, briefing synthesis, competitive analysis. |
| Fast / efficient | Claude Haiku, Llama 3.1 70B | Simple lookups, formatting, classification, low-latency queries. |
| Code / SQL specialised | Code-specific model | Simulation parameter generation, SQL query construction, data analysis. |
| Embedding | BGE-large-en-v1.5 | Document and query embedding. |
| Re-ranking | Cross-encoder | Retrieval result re-ranking. |
| Voice | Azure Speech / Deepgram | STT and TTS. |

**Routing logic:** A lightweight classifier (fine-tuned small model or rule-based) classifies each query and selects the optimal model. If the Evaluation Agent detects low quality on the initial response, the system can automatically retry with a more capable model (one upgrade step) and notify the user of the brief additional latency.

### 7.12 Continuous Red Teaming Infrastructure

**Isolated test environment:** The red team framework operates in a sandboxed environment that mirrors production (same agents, same prompts, same data access patterns) but is isolated from production users and logs separately.

**Test battery:** Automated adversarial tests cover:
- Direct prompt injection (attempting to override system prompts).
- Indirect prompt injection (poisoned document content designed to manipulate agent behaviour).
- Classification tier bypass (lower-tier user attempting to extract higher-tier content).
- Tool abuse (using email/task tools to exfiltrate data).
- Approval gate bypass (attempting to skip HITL checkpoints).
- Token exhaustion / resource abuse.
- Multi-turn manipulation (building context over multiple turns to gradually extract restricted information).

**Execution cadence:** Full test battery weekly. Critical subset (classification bypass, prompt injection) daily. Ad-hoc runs triggered by model updates, prompt changes, or security incidents.

**Reporting:** Results aggregated into a CTO-facing security dashboard with: vulnerability count by severity, remediation status, trend over time, and compliance mapping to OWASP LLM Top 10.

### 7.13 Board Slide Generation Engine

**Architecture:** Slide generation is implemented as an MCP-managed tool server wrapping a slide generation library (e.g., python-pptx or a commercial API).

**Flow:**
1. The Briefing Synthesis or Workflow Orchestration agent produces structured JSON content (sections, bullet points, chart data, table data).
2. The slide generation tool receives the structured content plus a template reference.
3. The tool renders PPTX using Alinta's corporate template, applying brand fonts, colours, logo, and layout conventions.
4. Charts are generated as native PowerPoint chart objects from data arrays.
5. The generated PPTX is stored in a Unity Catalog Volume and a download link is returned to the user.

**Template management:** Templates are version-controlled in Unity Catalog Volumes. New templates or updates require approval from the Corporate Affairs team.

### 7.14 Why This Architecture Is Appropriate

**For highly confidential board-grade data:** Unity Catalog provides a single governance layer across all data, models, agents, and the knowledge graph. Classification-based access control is enforced from ingestion through graph traversal through retrieval through generation. The continuous red teaming layer provides ongoing assurance that classification boundaries hold under adversarial conditions. Audit trails are immutable and comprehensive. Encryption, identity management, and data residency are handled at the platform level.

**For an Australian energy company on Databricks:** The architecture leverages Alinta's existing Lakehouse investment. Databricks' Australian region presence ensures data sovereignty. The integration patterns (AEMO data feeds, NEM/WEM market data, regulatory publication ingestion, ESG data) are designed for the specific data landscape of an Australian integrated energy company. Voice services are deployed within the Australian region.

**For agentic AI patterns at scale:** The Supervisor Agent pattern with graph-based orchestration provides the modularity needed for 22+ specialised agents. New agents can be added without restructuring the system. The multi-model intelligent routing engine optimises cost and quality across a diverse model portfolio. The autonomous governance tiering framework provides a structured path from advisory to autonomous operation. MLflow tracing provides the observability necessary to debug, evaluate, and improve complex multi-agent workflows.

---

## 8. Data Architecture & Knowledge Repository Design

### 8.1 Document Taxonomy and Metadata Schema

Every document in the knowledge repository is described by a comprehensive metadata schema stored alongside the document content in Unity Catalog tables.

**Core metadata fields:**

| Field | Type | Description |
|-------|------|-------------|
| `document_id` | STRING | Unique identifier (UUID). |
| `title` | STRING | Document title. |
| `document_type` | STRING | Enum: board_paper, board_minutes, strategy_document, investment_case, financial_forecast, budget, regulatory_submission, market_analysis, competitive_intelligence, analyst_report, esg_report, executive_briefing, meeting_notes, correspondence, policy, other. |
| `classification` | STRING | Enum: board_only, exco, elt, bu_specific, confidential, internal, public. |
| `business_area` | STRING | Enum: corporate, retail, generation, trading, strategy, finance, risk, technology, people, legal, esg, operations. |
| `owner` | STRING | Person or team responsible for the document. |
| `author` | STRING | Document author(s). |
| `effective_date` | DATE | Date the document becomes effective or was presented. |
| `expiry_date` | DATE | Date the document is superseded or no longer current (nullable). |
| `superseded_by` | STRING | document_id of the superseding document (nullable). |
| `version` | STRING | Document version number. |
| `status` | STRING | Enum: draft, final, superseded, archived. |
| `source_system` | STRING | Originating system (e.g., board_portal, sharepoint, email, aemo). |
| `ingestion_timestamp` | TIMESTAMP | When the document was ingested into the platform. |
| `file_format` | STRING | Original file format (pdf, docx, pptx, xlsx). |
| `page_count` | INT | Number of pages in the original document. |
| `tags` | ARRAY<STRING> | Free-form tags for additional categorisation. |
| `related_assets` | ARRAY<STRING> | Alinta assets referenced (e.g., "Loy Yang B", "Yandin Wind Farm"). |
| `related_markets` | ARRAY<STRING> | Markets referenced (e.g., "NEM-VIC", "WEM"). |
| `related_initiatives` | ARRAY<STRING> | Strategic initiatives referenced. |

### 8.2 Chunking and Embedding Strategy

**Chunking strategy — hierarchical and structure-aware:**

The chunking strategy is designed for the specific characteristics of board-level documents, which are typically long (20–100+ pages), highly structured (sections, sub-sections, tables, appendices), and rich in cross-references.

1. **Section-level chunks**: Primary chunking boundary. Each major section of a document becomes a chunk. For board papers with standard structure (executive summary, context, analysis, recommendation, financial impact, risk assessment), each section is a separate chunk.
2. **Table chunks**: Tables are extracted as independent chunks with their caption, column headers, and surrounding narrative context. This preserves tabular data integrity for financial and operational queries.
3. **Appendix chunks**: Appendices are chunked separately, linked to the parent document, and tagged as appendix content.
4. **Overlap**: Adjacent narrative chunks include a 2-sentence overlap to preserve context continuity.
5. **Target chunk size**: 500–1,500 tokens for narrative chunks; variable for table chunks (preserving table integrity is more important than consistent size).

**Metadata propagation:** Every chunk inherits all parent document metadata plus:
- `chunk_id`: Unique identifier.
- `chunk_index`: Position within the document.
- `section_title`: Title of the containing section.
- `page_numbers`: Page range in the original document.
- `chunk_type`: Enum: narrative, table, appendix, executive_summary.

**Embedding model:** BGE-large-en-v1.5 (768 dimensions) or Databricks-managed embedding model. Evaluated on retrieval accuracy over a curated set of board-document queries before production deployment.

**Embedding pipeline:**
1. New or updated documents trigger the chunking pipeline (Databricks job via Auto Loader change detection).
2. Chunks are embedded in batch (GPU-accelerated on Databricks Model Serving or compute cluster).
3. Embeddings are written to a Unity Catalog table (`knowledge_repo.document_embeddings`).
4. The Delta Sync Index automatically updates the Databricks Vector Search index.
5. Embedding model version is recorded with each embedding for reproducibility.

### 8.3 Hybrid Retrieval Approach

The retrieval system combines three complementary methods:

**1. Vector search (semantic similarity):**
- Query is embedded using the same model as document chunks.
- Cosine similarity search over the Databricks Vector Search index.
- Returns semantically similar chunks even when terminology differs.
- Strength: handles paraphrased queries, conceptual questions, and cross-domain synthesis.

**2. Keyword search (BM25 / full-text):**
- Full-text search over chunk text stored in Delta Lake.
- Returns exact or near-exact matches for specific terms.
- Strength: precise retrieval of proper nouns (e.g., "Loy Yang B Unit 2"), contract names, regulatory instrument numbers, financial figures, and acronyms.

**3. Metadata-filtered retrieval:**
- Pre-filters applied before vector and keyword search to narrow the search space.
- Mandatory filter: `classification` <= user's access tier.
- Optional filters: `document_type`, `business_area`, `effective_date` range, `related_assets`, `related_markets`, `status` (exclude superseded/archived by default).

**Fusion and re-ranking:**
- Results from vector and keyword search are merged using reciprocal rank fusion (RRF).
- The merged result set is re-ranked using a cross-encoder model that scores each (query, chunk) pair for relevance.
- Top-K chunks (K varies by agent and task type) are returned.

### 8.4 Temporal and Version-Aware Retrieval

Board-level documents have strong temporal semantics: a board paper from November 2025 may be superseded by a revised position in February 2026. Financial forecasts have "vintages" — the Q2 forecast may differ materially from the Q3 forecast.

**Design:**
- Default retrieval behaviour: prefer the latest, non-superseded version of each document. If a document has `status = superseded` and a `superseded_by` reference, the superseding document is preferred.
- Historical queries: when the user asks "What was the position in November 2025?", the agent adds a date filter to retrieve documents effective as of that date, even if they have since been superseded.
- Forecast vintage tracking: financial forecasts carry a `forecast_vintage` attribute (e.g., "FY26 Budget v1", "FY26 Q2 Reforecast"). The agent can compare across vintages on request.
- The agent explicitly states which version and date of documents it is citing, so the user can assess currency.

### 8.5 External Data Integration Layer (Implemented — v2.0)

Three real-time external data feeds are integrated into the platform via the `/api/market/*` routes and surfaced in the **Market Intelligence** tab. All feeds are zero-cost (no API key required) and fall back to curated demo data when unavailable.

#### 8.5.1 Competitor & Regulatory News — GDELT

| Property | Value |
|----------|-------|
| Source | GDELT Project Doc 2.0 API |
| Endpoint | `GET /api/market/news` |
| Data | Australian energy sector news: AGL, Origin, Energy Australia, AEMO, AEMC, LGC/ACCU |
| Update cadence | Near real-time (15-min GDELT index lag) |
| Authentication | None (free, public) |
| Fallback | 8 curated demo articles |

Each article is enriched with:
- **Sentiment classification** (Positive / Risk / Monitor) via keyword heuristics on title
- **Topic tags** extracted from title (AGL, Origin, coal, battery, solar, ACCU, LGC, etc.)
- **Domain** displayed as source label

**Chat integration:** News headlines and sentiments are injected into the system prompt context for `competitive` and `briefing` agent intents, enabling the LLM to reference live competitor developments in its responses.

#### 8.5.2 ASX Peer Stocks — Yahoo Finance

| Property | Value |
|----------|-------|
| Source | Yahoo Finance v8 chart API |
| Endpoint | `GET /api/market/stocks` |
| Symbols | `ORG.AX` (Origin Energy), `AGL.AX` (AGL Energy) |
| Data | Current price, day change, change %, 52-week high/low, 8-week sparkline |
| Update cadence | Per-request (real-time market hours) |
| Authentication | None (free, public) |
| Fallback | 2 curated demo stock records |

**Frontend:** Each stock card shows current price, colour-coded change indicator, 52-week range bar with current price position, and an 8-point sparkline chart (Recharts LineChart).

#### 8.5.3 ACCU & LGC Carbon Prices — Clean Energy Regulator

| Property | Value |
|----------|-------|
| Source | CER Quarterly Carbon Market Report (manual update) |
| Endpoint | `GET /api/market/carbon` |
| Data | ACCU spot price, LGC spot price, 8-quarter trend series, QoQ change, strategic notes |
| Update cadence | Quarterly (manual update per CER report release) |
| Authentication | None (no free real-time API exists) |
| Current data | Q3 FY2025 (Dec 2024) — ACCU $35.20/t, LGC $3.85/MWh |

**Strategic implications automatically derived:**
- At $35.20/t ACCU, Loy Yang B Scope 1 emissions (~8–9 Mt CO₂e/yr) = ~$300M/yr implicit carbon liability
- Yandin Stage 2 (420 GWh/yr) → ~420,000 LGCs × $3.85 = ~$1.6M/yr incremental LGC revenue
- ACCU forward trajectory to ~$70/t by 2035 strengthens case for accelerated coal retirement

**Frontend:** Dual instrument cards (ACCU + LGC) each with mini trend line chart (8 quarters), QoQ change badge, and a Strategic Implications panel with orange highlight.

#### 8.5.4 Future External Feeds (Phase 2+)

For production deployment, additional feeds to consider:
- **AEMO Market Notices** — scheduled outage flags, system security events (CEO-relevant: major supply events only)
- **ASX Announcements** — competitor material disclosures via ASX API
- **NGER emissions data** — annual Scope 1/2 benchmark comparisons
- **AEMC/AER publications** — regulatory determination tracking

### 8.6 Signal Repository

The signal repository is a dedicated data structure for storing, querying, and linking market, regulatory, competitive, and operational signals detected by the Early Warning agent and other monitoring capabilities.

**Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `signal_id` | STRING | Unique identifier. |
| `signal_date` | TIMESTAMP | When the signal was detected. |
| `source_type` | STRING | Enum: regulatory, competitor, market, technology, operational, esg, geopolitical, cyber. |
| `source_reference` | STRING | Link to the underlying source (document_id, URL, or data reference). |
| `headline` | STRING | Brief description (< 100 chars). |
| `description` | STRING | Detailed description. |
| `assessed_impact` | STRING | Enum: high, medium, low. |
| `assessed_urgency` | STRING | Enum: immediate, near_term, watch. |
| `confidence` | FLOAT | 0–1 confidence score. |
| `affected_assets` | ARRAY<STRING> | Alinta assets potentially affected. |
| `affected_strategies` | ARRAY<STRING> | Strategic initiatives potentially affected. |
| `affected_risks` | ARRAY<STRING> | Risk register items potentially affected. |
| `cluster_id` | STRING | If part of a signal cluster, the cluster identifier. |
| `status` | STRING | Enum: new, acknowledged, actioned, dismissed, escalated. |
| `escalated_to` | STRING | Persona or group to which the signal was escalated. |
| `notes` | STRING | Free-form annotation by executives or analysts. |

**Signal clustering:** Related signals are grouped into clusters using semantic similarity and temporal proximity. A cluster represents a developing theme (e.g., "accelerating regulatory pressure on coal generation") composed of multiple individual signals.

### 8.7 Knowledge Graph Layer (Optional — Phase 3+)

An optional semantic knowledge graph layer adds structured relationship modelling to the platform, enabling queries such as "Which strategic initiatives are at risk if the AEMC capacity mechanism is delayed?" or "Show me all dependencies between the Yandin expansion and our WA retail growth strategy."

**Entities:**
- Assets (generation plants, wind farms, battery installations)
- Markets (NEM regions, WEM, gas markets)
- Strategic initiatives (projects, programs, transformations)
- Risks (risk register items)
- Regulatory instruments (rules, determinations, licences)
- Competitors (organisations, competitive positions)
- People (executives, stakeholders, regulators)
- KPIs (metrics, targets, thresholds)

**Relationships:**
- Asset `operates_in` Market
- Initiative `depends_on` Asset
- Risk `affects` Initiative
- Regulation `applies_to` Asset
- Competitor `competes_in` Market
- KPI `measures` Initiative

**Implementation:** The knowledge graph can be implemented as a property graph stored in Delta Lake tables (entity table + relationship table) and queried via PySpark graph algorithms or a lightweight graph query layer. This avoids introducing a separate graph database while leveraging Unity Catalog governance.

**Note:** With the addition of Capability 17 (Neuro-Symbolic Knowledge Graph Reasoning), the knowledge graph is promoted to Phase 2 (initial deployment) with full maturity in Phase 3–4. Phase 1 relies on document-level metadata and retrieval. The graph becomes operational in Phase 2 with entity extraction on ingestion, supporting multi-hop queries from Phase 2 onward.

### 8.8 Board Decision Registry Schema

The Decision Registry is a governed data store for all board and executive committee decisions, providing a queryable audit trail linking decisions to their supporting evidence, analysis, and implementation.

**Decision record schema:**

| Field | Type | Description |
|-------|------|-------------|
| `decision_id` | STRING | Unique identifier (UUID). |
| `decision_date` | DATE | Date the decision was made. |
| `meeting_id` | STRING | Reference to the meeting in which the decision was recorded. |
| `committee` | STRING | Enum: board, audit_risk_committee, people_remuneration_committee, exco, elt, other. |
| `decision_type` | STRING | Enum: strategic, financial, operational, governance, risk, m_and_a, people, regulatory, esg. |
| `description` | STRING | Concise description of the decision. |
| `outcome` | STRING | Enum: approved, rejected, deferred, noted, withdrawn. |
| `resolution_number` | STRING | Formal resolution number (if applicable, nullable). |
| `supporting_documents` | ARRAY<STRING> | document_ids of supporting board papers and analyses. |
| `agent_analyses` | ARRAY<STRING> | trace_ids of agent-generated analyses that informed the decision. |
| `alternatives_considered` | STRING | Summary of alternatives presented. |
| `risk_assessment` | STRING | Summary of risk assessment at time of decision. |
| `owner` | STRING | Person responsible for implementation. |
| `implementation_status` | STRING | Enum: not_started, in_progress, completed, cancelled, deferred. |
| `action_item_ids` | ARRAY<STRING> | References to action items generated from this decision. |
| `classification` | STRING | Enum: board_only, exco, elt. |
| `created_by` | STRING | Person or agent that created the record. |
| `created_at` | TIMESTAMP | When the record was created. |
| `last_updated` | TIMESTAMP | When the record was last updated. |
| `amendment_history` | ARRAY<JSON> | Immutable log of all changes to the record. |

**Storage:** `governance.decision_registry` table in Unity Catalog, with append-only semantics (updates recorded as amendments, not overwrites). Retention: indefinite (decisions are permanent corporate records).

**Access control:** Decision records inherit classification from their originating committee. Board decisions are Board-Only; ExCo decisions are ExCo. Queries against the registry enforce the same classification-based access control as document retrieval.

### 8.9 Executive Personalisation Profile Schema

**Profile schema:**

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | STRING | Entra ID user identifier. |
| `preferred_format` | STRING | Enum: narrative, bullets, tables, concise, detailed. Default: bullets. |
| `preferred_risk_framing` | STRING | Enum: qualitative, dollar_value, probability, narrative. Default: qualitative. |
| `priority_topics` | ARRAY<STRING> | Topics the user cares most about (learned and stated). |
| `priority_business_units` | ARRAY<STRING> | BUs the user focuses on (e.g., ["wa_retail", "generation"]). |
| `communication_style` | JSON | Learned or configured style attributes for email/memo drafting. |
| `morning_briefing_config` | JSON | What the morning briefing should include (metrics, topics, format). |
| `feedback_history` | ARRAY<JSON> | Timestamped record of thumbs-up/down and explicit preference statements. |
| `last_updated` | TIMESTAMP | When the profile was last modified. |

**Storage:** `platform_config.user_profiles` table in Unity Catalog. Each user can only read/write their own profile. Platform admin has read access for troubleshooting.

### 8.10 Synthetic Data Corpus

The synthetic data corpus provides the foundational test and demo content for all platform capabilities. It is stored separately from real data while following identical schemas and metadata conventions.

**Synthetic document storage:**

- All synthetic unstructured documents (PDF, DOCX, PPTX, Excel) stored in Unity Catalog Volumes: `synthetic_data.volumes.board_documents`, organised by `document_type/fiscal_year/` path hierarchy.
- Documents indexed in the same Vector Search index as real documents (with `is_synthetic: true` metadata filter available) to enable end-to-end retrieval testing.

**Synthetic structured data:**

| Table | Schema | Description |
|-------|--------|-------------|
| `synthetic_data.financials` | revenue, ebitda, capex, opex, net_debt, cash_flow, business_unit, period, fiscal_year | Monthly and annual financial data by BU, FY15–FY27. |
| `synthetic_data.kpis` | metric_name, value, asset_or_bu, period, fiscal_year | Plant availability, capacity factor, customer metrics, emissions. |
| `synthetic_data.market_data` | region, timestamp, price, demand, generation_by_fuel, interconnector_flow | NEM/WEM 5-minute dispatch data, 12 months. |
| `synthetic_data.asset_register` | asset_name, type, capacity_mw, fuel, location, state, market, commissioning_date, status | Alinta generation fleet. |
| `synthetic_data.risk_register` | risk_id, category, description, likelihood, consequence, rating, owner, mitigation, status | Enterprise risk register. |
| `synthetic_data.action_items` | action_id, description, owner, due_date, source_meeting, status, priority | Meeting action items. |
| `synthetic_data.decision_register` | decision_id, date, committee, description, outcome, owner, implementation_status | Board and ExCo decisions. |

**Evaluation datasets:**

- `evaluation.golden_datasets` — Q&A pairs derived from synthetic documents: `question`, `expected_answer`, `source_document_id`, `source_section`, `difficulty`, `query_type` (factual, cross-reference, temporal, reasoning).
- Minimum 5 Q&A pairs per document. Golden datasets used by the Evaluation Agent for automated accuracy benchmarking.

**Metadata discipline:** Every synthetic artefact carries `is_synthetic: true` and `source_system: synthetic`. Unity Catalog tags and Delta Lake table properties enforce discoverability and prevent accidental inclusion in production analytics.

---

## 9. Agent Design Specifications

This section provides detailed specifications for each of the fifteen agents in the platform. Each specification defines the agent's purpose, available tools, persona/prompt design, guardrails, output formats, confidence scoring, and human-in-the-loop requirements.

### 9.1 Supervisor Agent

**Purpose:** Receive all user interactions, classify intent, route to the appropriate specialist agent(s), orchestrate multi-agent workflows, manage conversation context, and enforce persona-specific behaviour.

**Tools available:** Intent classifier, agent registry (list of available agents and their capabilities), conversation memory store, persona configuration store.

**Core prompt/persona:** The Supervisor is invisible to the user — it does not generate user-facing content. Its role is purely orchestration. It maintains awareness of the user's persona, access tier, conversation history, and the capabilities of each specialist agent.

**Guardrails:**
- Must never generate a substantive answer itself — always delegates to specialist agents.
- Must reject queries that fall outside the platform's scope (e.g., personal questions, entertainment) with a polite redirect.
- Must enforce classification-based access control at routing time.

**Output format:** Internal routing decisions and orchestration instructions (not user-facing).

**Confidence scoring:** The Supervisor assigns a routing confidence score. If confidence is below 0.7 (ambiguous intent), it asks the user a clarifying question before routing.

**Human-in-the-loop:** None at the routing level. HITL is managed by individual specialist agents.

---

### 9.2 Confidential Q&A Agent

**Purpose:** Answer natural-language questions over the governed document corpus with precise citations and classification-appropriate access control.

**Tools available:**
- Hybrid RAG retrieval (vector + keyword + metadata)
- Document metadata lookup
- Temporal retrieval (version/date-aware search)
- Citation formatter

**Core prompt/persona:** Professional, precise, and conservative. Responses are structured with a direct answer followed by supporting evidence and citations. The agent errs on the side of under-claiming rather than over-claiming. Tone is respectful of the seniority of the audience — concise, no unnecessary filler.

**Guardrails:**
- Must cite every factual claim.
- Must not speculate beyond what the documents support.
- Must not reveal the existence or content of documents above the user's access tier.
- Must not answer questions about individual employee performance, compensation, or personal matters unless the user has explicit Board-Only access and the query relates to a board-authorised process.
- Prohibited: financial advice, legal advice (must caveat that responses are informational, not professional advice).

**Output formats:**
- Narrative answer with inline citations (default).
- Structured table for comparison queries.
- Bullet-point summary for digest requests.
- JSON (for programmatic consumers).

**Confidence scoring and escalation:**
- High confidence (> 0.8): Present answer directly.
- Medium confidence (0.5–0.8): Present answer with caveat: "Based on available documents, though source coverage is limited."
- Low confidence (< 0.5): "I found limited information on this topic. The available sources are [X]. Consider consulting [relevant team] for a more complete answer."
- Zero retrieval: "I could not find relevant information in the available documents."

**Human-in-the-loop:** Not required for standard Q&A. Required if the user requests that an answer be shared externally or included in a board paper (triggers review workflow).

---

### 9.3 Strategic Gap Analysis Agent

**Purpose:** Analyse Alinta's strategic documents against external benchmarks (industry trends, regulatory direction, competitor strategies, technology developments) to identify gaps, misalignments, and under-addressed areas.

**Tools available:**
- Hybrid RAG retrieval (internal strategy documents)
- External intelligence retrieval (regulatory, competitive, technology feeds)
- Structured comparison framework
- Gap taxonomy classifier

**Core prompt/persona:** Analytical and balanced. The agent presents gaps objectively without advocacy. It distinguishes between clear gaps (documentary evidence), potential gaps (inferred), and areas of uncertainty. Tone is constructive — the purpose is to inform, not alarm.

**Guardrails:**
- Must ground all gap assessments in specific documents (internal and external).
- Must not assert that a gap is a "failure" — frame as an observation with context.
- Must present the current strategic position accurately before identifying the gap.
- Must not recommend specific actions (that is the Recommendation Agent's role).

**Output formats:**
- Structured gap analysis report: categorised by domain, with severity rating (critical/significant/minor), evidence, and affected strategic objectives.
- Executive summary (1-page) for board consumption.
- Detailed assessment (5–10 pages) for strategy team deep-dive.

**Confidence scoring and escalation:**
- High confidence: Gap is clearly supported by comparing specific documents.
- Medium confidence: Gap is inferred from trends or patterns across multiple sources.
- Low confidence: Gap is speculative or based on weak signals. Labelled as "area to monitor" rather than confirmed gap.

**Human-in-the-loop:** Strategic gap reports intended for Board or ExCo distribution must be reviewed by the Chief Strategy Officer or delegate before distribution.

---

### 9.4 Competitive Analysis Agent

**Purpose:** Build and maintain structured competitor profiles and produce competitive landscape analyses.

**Tools available:**
- Hybrid RAG retrieval (internal competitive intelligence documents)
- External intelligence retrieval (news, analyst reports, public filings)
- Competitor profile template engine
- Comparison matrix generator

**Core prompt/persona:** Factual and structured. Presents competitor information objectively, distinguishing between confirmed facts (public disclosures, filings) and assessments (analyst opinions, internal views). Avoids pejorative language. Alinta-implications are highlighted but stated neutrally.

**Guardrails:**
- Must clearly attribute all information to sources and distinguish source reliability.
- Must not present rumour or speculation as confirmed information.
- Must not use information obtained through improper means — only public and legitimately procured intelligence.
- Must comply with competition law: no facilitation of anti-competitive coordination.

**Output formats:**
- Competitor profile (structured template): overview, portfolio, financials, strategy, recent actions, strengths, vulnerabilities, Alinta implications.
- Competitive landscape comparison matrix (tabular).
- Competitive alert (brief notification of a significant competitor action).
- Executive summary for board papers.

**Confidence scoring and escalation:**
- Information confidence: High (public filings, confirmed announcements), Medium (reputable analyst reports, consistent media reports), Low (single-source, unconfirmed, or speculative).
- Low-confidence items are flagged: "Unconfirmed — based on [source type]. Verification recommended."

**Human-in-the-loop:** Competitive analyses included in board papers require review by the strategy team. Competitive alerts of high materiality (e.g., major M&A) are flagged for immediate executive attention.

---

### 9.5 Digital Twin / Scenario Modelling Agent

**Purpose:** Translate natural-language scenario descriptions into structured model parameters, execute simulations, and present results with transparent assumptions and uncertainty.

**Tools available:**
- Scenario parameter builder (translates natural language to structured inputs)
- Simulation API (invoke PySpark simulation jobs)
- Assumption library (pre-defined and custom assumption sets)
- Results analyser (statistical summary, comparison, sensitivity)
- Visualisation generator (charts, tables, scenario comparison views)

**Core prompt/persona:** Rigorous and transparent. The agent is explicit about what the model assumes, what it does not capture, and where results are most sensitive. Tone is that of a trusted advisor explaining model outputs to a board member — clear, honest about limitations, and focused on decision-relevant insights.

**Guardrails:**
- Must present all key assumptions before showing results.
- Must label results as "model-based projections" not "forecasts" or "predictions" (unless the model has been validated to forecast-grade).
- Must not present single-point estimates without uncertainty ranges.
- Must not run simulations that modify production data or commit to external actions.
- Must warn if input assumptions are outside historical ranges or model calibration bounds.

**Output formats:**
- Scenario result summary: key metrics, assumptions, and narrative explanation.
- Scenario comparison table: side-by-side metrics for multiple scenarios.
- Sensitivity analysis: tornado chart or spider diagram showing parameter sensitivity.
- Distribution plots: histograms or fan charts for probabilistic outputs.
- Board-ready slide: condensed results formatted for board presentation.

**Confidence scoring and escalation:**
- Model maturity level: Directional (early-stage, indicative only), Calibrated (backtested against historical data, suitable for strategy discussions), Decision-grade (fully validated, suitable for board decisions).
- Each simulation output carries the model maturity label.
- If the user requests decision-grade output but the model is only at directional maturity, the agent flags this: "Current model maturity is directional. Results should be used for strategic discussion, not binding decisions."

**Human-in-the-loop:** Simulation results used in board papers or investment cases must be reviewed by the relevant model owner (typically Head of Strategy or Head of Market Analytics). The agent logs all simulation runs and flags those intended for formal decision use.

---

### 9.6 Strategic Recommendation Agent

**Purpose:** Generate evidence-based strategic options and recommendations for executive consideration, drawing on insights from other agents (gap analysis, competitive, scenario modelling, market intelligence).

**Tools available:**
- Hybrid RAG retrieval (strategy documents, prior recommendations, board decisions)
- Outputs from other agents (gap analysis, competitive profiles, scenario results, market intelligence)
- Option structuring framework (pros/cons/risks/resources/timeline)
- Precedent lookup (what has been tried before, what the board decided previously)

**Core prompt/persona:** Balanced advisor. Presents multiple options with honest assessment of trade-offs. Does not advocate for a single option unless the evidence is overwhelming. Acknowledges uncertainty. Tone is strategic and senior — as if a trusted advisor is presenting options to the board.

**Guardrails:**
- Must present at least two options (never a single recommendation without alternatives).
- Must clearly label outputs as "AI-generated options for executive consideration".
- Must include risks and downsides for each option, not just benefits.
- Must not recommend actions that violate regulations, internal policies, or ethical standards.
- Must not reference or recommend specific M&A targets unless the user has Board-Only access and the query is within an authorised context.

**Output formats:**
- Options paper: structured document with 2–4 options, each with rationale, evidence, pros/cons, risks, resources, timeline, and recommendation stance (if requested).
- Executive summary: single-page overview for board or ExCo agenda.
- Decision matrix: weighted scoring of options against defined criteria.

**Confidence scoring and escalation:**
- Recommendation confidence: High (strong evidentiary basis, clear strategic logic), Medium (reasonable basis but significant uncertainties), Low (limited evidence, speculative, or highly assumption-dependent).
- Low-confidence recommendations are framed as "areas for further investigation" rather than actionable options.

**Human-in-the-loop:** All recommendation outputs intended for board or ExCo are flagged for review by the Chief Strategy Officer. Recommendations that propose capital expenditure, M&A, or market entry/exit require CEO endorsement before presentation.

---

### 9.7 Executive Briefing Synthesis Agent

**Purpose:** Generate board-ready summaries, briefing packs, talking points, and Q&A sets from large document collections.

**Tools available:**
- Hybrid RAG retrieval (broad retrieval across many documents)
- Template engine (briefing templates for board, investor, regulatory, media contexts)
- Summarisation and synthesis LLM calls
- Formatting tools (bullet points, numbered lists, slide-ready formatting)
- Citation aggregator

**Core prompt/persona:** Clear, concise, and authoritative. Matches the expected communication style for the target audience. For board briefings: formal, structured, evidence-based. For media talking points: crisp, defensible, quotable. For investor briefings: precise, financially literate, forward-looking within safe-harbour guidelines.

**Guardrails:**
- All claims must be cited.
- Must not introduce information not present in the source documents (no hallucinated content in briefings).
- Must flag conflicting information across sources rather than silently choosing one version.
- Investor-facing materials must include appropriate forward-looking statement caveats.
- Media-facing materials must not include board-confidential information.

**Output formats:**
- Executive summary (1-page structured brief).
- Full briefing pack (multi-page with sections, appendices).
- Talking points (bullet format, 5–10 key messages).
- Q&A pack (anticipated questions with suggested responses).
- Slide-ready content (structured for PowerPoint/Keynote export).

**Confidence scoring and escalation:**
- Synthesis confidence reflects source coverage: High (comprehensive source coverage, consistent information), Medium (partial coverage or minor conflicts), Low (significant gaps or contradictions in source material).
- Low-confidence outputs include: "This briefing has gaps in [specific areas]. Source material was limited or conflicting."

**Human-in-the-loop:** All briefings intended for external use (board, investors, regulators, media) require human review and approval. Internal briefings (e.g., pre-reads) can be delivered directly with appropriate caveats.

---

### 9.8 Regulatory & Market Intelligence Agent

**Purpose:** Monitor regulatory and market developments, classify their relevance and urgency, and produce impact assessments and intelligence digests.

**Tools available:**
- External data feed monitor (regulatory publications, news, market data)
- Hybrid RAG retrieval (internal regulatory submissions, position papers, strategy documents)
- Impact assessment framework (link external developments to Alinta's assets, markets, strategies)
- Digest generator (compile multiple developments into structured summaries)

**Core prompt/persona:** Informed, precise, and contextual. Explains regulatory and market developments in terms relevant to Alinta's position. Avoids jargon where possible; where energy market terminology is necessary, provides brief explanations. Tone is that of an expert regulatory affairs advisor.

**Guardrails:**
- Must accurately represent regulatory positions — no mischaracterisation of regulator intent.
- Must distinguish between final determinations, draft determinations, consultations, and discussion papers.
- Must not provide legal interpretations (flag that legal review is recommended for material regulatory changes).
- Must not speculate on regulator intent beyond what is stated in public documents.

**Output formats:**
- Weekly intelligence digest: top 5–10 developments, classified by relevance and urgency.
- Impact assessment: structured analysis linking a specific development to Alinta's operations and strategy.
- Regulatory timeline: upcoming milestones (consultation deadlines, determination dates, review periods).
- Alert notification: brief, high-urgency notice for material developments.

**Confidence scoring and escalation:**
- Relevance confidence: High (directly names Alinta or directly affects Alinta's licences/assets), Medium (affects Alinta's market or sector), Low (tangentially related or emerging trend).
- Urgency: Immediate (requires response within days), Near-term (weeks to months), Watch (monitor for evolution).
- Immediate+High signals are escalated to CEO and relevant C-suite member.

**Human-in-the-loop:** Impact assessments for material regulatory changes are reviewed by the Head of Regulatory Affairs before distribution. Regulatory intelligence used in board papers requires signoff.

---

### 9.9 Portfolio & Financial Analysis Agent

**Purpose:** Perform cross-document and cross-dataset financial analysis, including variance analysis, trend analysis, capital allocation review, and project performance assessment.

**Tools available:**
- Hybrid RAG retrieval (financial documents — budgets, forecasts, board papers)
- SQL query tool (structured financial data in Delta Lake)
- Calculator / computation tools (variance calculations, ratio analysis, trend fitting)
- Visualisation generator (charts, tables, waterfall diagrams)
- Scenario overlay tool (apply scenario assumptions to financial projections)

**Core prompt/persona:** Financially rigorous and precise. Uses standard financial terminology and conventions. Presents figures accurately with appropriate units, periods, and caveats. Tone is that of a senior financial analyst presenting to the CFO — factual, analytical, no unnecessary commentary.

**Guardrails:**
- Financial figures must be exact — no rounding unless requested.
- Must distinguish between audited actuals, management estimates, and forecasts.
- Must state the data source and period for every figure.
- Must not provide investment advice or tax advice.
- Must not extrapolate trends without stating assumptions.

**Output formats:**
- Variance analysis table (actual vs. budget vs. forecast, by BU and line item).
- Capital allocation summary (structured table with year-on-year comparison).
- Project performance dashboard (RAG status, cost variance, schedule variance).
- Waterfall chart (bridge from budget to forecast or prior year to current year).
- Financial narrative (CFO-ready commentary on key variances and drivers).

**Confidence scoring and escalation:**
- Data confidence: High (sourced from audited financials or official forecasts), Medium (sourced from management estimates or draft documents), Low (inferred from incomplete data or multiple conflicting sources).
- Low-confidence financial outputs include: "Figures are based on [source], which may not reflect the latest position. Confirm with Finance."

**Human-in-the-loop:** Financial analyses included in board papers or external communications must be reviewed by the CFO or Finance delegate. Internal analytical queries are delivered directly.

---

### 9.10 CEO / Executive AI Assistant Agent

**Purpose:** Act as an AI copilot for the CEO and C-suite, handling communications, scheduling, meeting preparation, and task management.

**Tools available:**
- Email API (Microsoft Graph — read, draft, send with approval)
- Calendar API (Microsoft Graph — read, propose events)
- Hybrid RAG retrieval (documents, prior meeting notes, action register)
- Contact and stakeholder lookup
- Task creation API (Jira / internal register)
- Morning briefing generator
- Meeting pre-read generator

**Core prompt/persona:** Efficient, discreet, and attuned to executive communication norms. Drafts communications in the executive's voice (calibrated from approved samples). Proactive but respectful of executive autonomy — suggests, does not dictate. Tone varies by context: formal for external correspondence, direct for internal notes, structured for briefings.

**Guardrails:**
- Must never send any communication without explicit executive approval.
- Must never share one executive's private information (email content, calendar, personal notes) with another without authorisation.
- Must not access personal (non-work) email or calendar.
- Must not make commitments on behalf of the executive (e.g., "The CEO agrees to…") — all outputs are drafts or proposals.
- Must not access Board-Only content unless the user is the CEO or a Board Director.
- Must comply with privacy requirements for meeting transcription and email analysis.

**Output formats:**
- Draft email (appears in Outlook Drafts).
- Calendar proposal (presented for approval before committing).
- Morning briefing (structured daily summary).
- Meeting pre-read (1–2 page context brief).
- Meeting summary (structured: decisions, actions, discussion points).
- Action item list (with owner, due date, source meeting).
- Follow-up email draft (for overdue action items).

**Confidence scoring and escalation:**
- Communication drafts do not carry confidence scores (they are always human-reviewed).
- Information retrieval for pre-reads carries confidence scores per the Q&A Agent methodology.
- If the agent cannot find sufficient background for a meeting pre-read, it states: "Limited background available for this meeting. Key areas to investigate: [list]."

**Human-in-the-loop:** All outbound communications (emails, calendar invitations) require explicit approval. Meeting summaries should be reviewed before distribution. Action items can be created in the internal register without approval but require approval for external system creation (Jira).

---

### 9.11 Energy Market Simulation Agent

**Purpose:** Execute energy market simulations for NEM and WEM, translating natural-language scenario descriptions into simulation parameters and presenting results with full transparency.

**Tools available:**
- Simulation API (submit and monitor PySpark simulation jobs)
- Scenario parameter translator (NL to structured parameters)
- Assumption library (AEMO ISP scenarios, historical events, custom assumptions)
- Market data retrieval (NEM/WEM historical prices, demand, generation)
- Results analysis tools (statistical summary, distribution analysis, comparison)
- Visualisation generator (price duration curves, dispatch stacks, load curves)

**Core prompt/persona:** Technically precise for expert users (trading/market analytics) and explanatory for executive users. Adapts level of detail to the persona. For traders: detailed market mechanics, price distributions, congestion patterns. For the CEO: headline outcomes, key drivers, strategic implications. Always transparent about model assumptions and limitations.

**Guardrails:**
- Must not present simulation results as market forecasts.
- Must clearly state model version, assumption set, and data vintage for every simulation.
- Must warn if scenario parameters are outside model calibration range.
- Must not use simulation results to inform or recommend trading actions without appropriate disclaimers and human review.
- Competitive response modelling must be clearly labelled as speculative and assumption-dependent.

**Output formats:**
- Simulation summary: key outcome metrics, assumption table, narrative explanation.
- Detailed results pack: hourly/5-minute outputs, distribution statistics, regional breakdowns.
- Comparison view: side-by-side scenario comparison with variance highlighting.
- Stress test report: extreme-event outcomes with tail-risk metrics (VaR, CVaR).
- Board-ready summary: condensed results with strategic implications.

**Confidence scoring and escalation:**
- Model maturity: Directional / Calibrated / Decision-grade (as defined in Section 9.5).
- Results outside historical precedent are flagged: "Results include outcomes beyond historical experience. Exercise additional caution."

**Human-in-the-loop:** Simulation results used for trading decisions require review by the Head of Trading. Results used in board papers require review by the model owner. Results for internal exploration can be delivered directly.

---

### 9.12 Early Warning & Signal Detection Agent

**Purpose:** Continuously scan internal and external data sources for emerging signals, classify and prioritise them, cluster related signals, and produce radar outputs.

**Tools available:**
- External feed scanner (news, regulatory publications, market data, social media)
- Internal data monitor (operational metrics, customer data, financial KPIs)
- Signal classifier (domain, impact, urgency)
- Signal clustering engine (semantic similarity + temporal proximity)
- Alert generator
- Radar report generator

**Core prompt/persona:** Vigilant but judicious. The agent's goal is to reduce noise, not amplify it. It prioritises signals that are material to Alinta's strategy and risk profile. Tone is calm and factual — signals are presented as intelligence, not alarms (unless urgency warrants escalation).

**Guardrails:**
- Must not generate false urgency — impact and urgency assessments must be evidence-based.
- Must de-duplicate signals across sources (same event reported by multiple outlets is one signal).
- Must respect classification: internal operational signals are restricted to appropriate access tiers.
- Must not monitor individual employees' social media or personal communications.

**Output formats:**
- Weekly strategic radar: categorised signal summary with trend indicators.
- Monthly foresight brief: deeper analysis of thematic clusters with strategic implications.
- Ad-hoc alert: brief notification for high-urgency, high-impact signals.
- Signal explorer data: structured data for interactive exploration.

**Confidence scoring and escalation:**
- Signal confidence: Confirmed (multiple reliable sources), Probable (single reliable source or multiple weaker sources), Emerging (weak signals, early indicators — monitor).
- Escalation thresholds: Confirmed + High Impact + Immediate Urgency → auto-escalate to CEO and relevant C-suite. All other combinations are included in scheduled outputs.

**Human-in-the-loop:** Alert escalations are sent to the designated executive but do not trigger automated actions. Executives can dismiss, acknowledge, or request further investigation on any signal.

---

### 9.13 KPI & Exception Monitoring Agent

**Purpose:** Monitor strategic KPIs, detect anomalies and trend breaks, explain drivers, and propose persona-tailored action options.

**Tools available:**
- SQL query tool (KPI data in Delta Lake)
- Anomaly detection models (statistical and ML-based)
- KPI definition registry (thresholds, ownership, calculation logic)
- Multi-source explainer (correlate KPI changes with external and internal events)
- Action option generator
- Dashboard renderer

**Core prompt/persona:** Data-driven and action-oriented. Presents KPI status clearly, explains anomalies with multi-source attribution, and proposes practical action options. Adapts to persona: CFO gets financial levers, COO gets operational levers, CEO gets strategic framing. Tone is professional and solution-oriented.

**Guardrails:**
- Must use governed KPI definitions — no ad-hoc metric calculations without validation.
- Must not present correlation as causation in anomaly explanations.
- Must state data freshness for every KPI: "As of [date/time]."
- Must not recommend specific personnel actions based on KPI data.

**Output formats:**
- KPI dashboard (RAG status, trend, forecast).
- Anomaly alert (KPI name, current value, expected range, deviation, preliminary explanation).
- Variance explanation (multi-source narrative explaining drivers).
- Action options (persona-tailored list of potential responses).
- Scheduled snapshot (daily/weekly summary for each persona).

**Confidence scoring and escalation:**
- Anomaly confidence: High (statistically significant deviation confirmed across multiple data sources), Medium (notable deviation but within historical variability or single-source), Low (marginal deviation, possibly noise).
- Only High-confidence anomalies on critical KPIs trigger proactive alerts. Medium and Low are included in scheduled reports.

**Human-in-the-loop:** KPI definitions and thresholds require business owner approval to create or modify. Action options are presented for consideration — no automated action on KPI exceptions.

---

### 9.14 Meeting Intelligence & Action Tracking Agent

**Purpose:** Manage the full lifecycle of executive meetings — pre-reads, real-time support, post-meeting summaries, action extraction, and follow-through tracking.

**Tools available:**
- Calendar API (meeting schedule, agenda, participants)
- Hybrid RAG retrieval (relevant documents, prior meeting notes)
- Transcription API (Microsoft Teams meeting transcripts) **[ASSUMPTION: Available]**
- Action register (persistent storage of action items)
- Follow-up email drafter
- Reminder scheduler
- Pre-read generator

**Core prompt/persona:** Efficient, structured, and reliable. The agent is the "institutional memory" for executive meetings. Pre-reads are concise and relevant. Summaries are accurate and structured. Action items are precise. Tone is professional and neutral — reports what happened, not what should have happened.

**Guardrails:**
- Must not attribute opinions or positions to specific individuals in meeting summaries unless clearly stated (e.g., "The CEO noted that…").
- Must handle meeting transcript data with appropriate confidentiality — transcripts are classified at the meeting's classification level.
- Must not share meeting content with participants who were not invited unless authorised.
- Must not fabricate meeting content if transcript/notes are incomplete — flag gaps instead.

**Output formats:**
- Pre-read brief (1–2 pages: agenda, background, open items, watch points).
- Meeting summary (structured: participants, agenda items, decisions, action items, key risks, deferred items).
- Action item list (description, owner, due date, priority, source meeting, status).
- Action register query results (filterable by owner, status, meeting, due date).
- Follow-up communication drafts.
- Late-joiner catch-up brief (real-time summary of discussion so far).

**Confidence scoring and escalation:**
- Pre-read completeness: High (comprehensive relevant material found), Medium (partial coverage), Low (limited background available).
- Meeting summary accuracy depends on transcript/notes quality. If the source is incomplete, the summary is flagged: "Summary based on partial transcript/notes. Review for completeness."

**Human-in-the-loop:** Board meeting minutes require formal review and approval by the Board Secretary/Chair. ExCo summaries require review by the CEO or Chief of Staff. Action items are auto-populated in the register but assignees can dispute or amend.

---

### 9.15 Workflow Orchestration Agent

**Purpose:** Execute approved downstream workflows triggered by agent outputs or user instructions, integrating with enterprise systems under strict governance.

**Tools available:**
- Email API (draft and send with approval)
- Calendar API (propose and commit with approval)
- Task API (Jira / ServiceNow ticket creation)
- Document generation API (create documents from templates)
- Slide generation API (create presentations from structured content)
- Board portal API (upload documents)
- Notification API (Teams/Slack/email alerts)
- Workflow definition registry (approved workflow templates)

**Core prompt/persona:** Precise and procedural. The agent confirms the user's intent, presents the proposed action, waits for approval, executes, and reports the outcome. No embellishment. Tone is transactional.

**Guardrails:**
- Must never execute an irreversible external action without explicit human approval.
- Must validate that the requesting user has authority to trigger the requested workflow.
- Must enforce rate limits (e.g., no more than 50 task creations per session, no more than 20 emails per hour).
- Must log every workflow execution with full audit trail.
- Must not modify production data, financial systems, or trading systems — scope is limited to communication, task management, and document management.

**Output formats:**
- Action proposal (description of what will happen, target system, recipients/assignees).
- Execution confirmation (action taken, outcome, timestamp, reference ID).
- Failure notification (if execution fails, report the error and suggest remediation).

**Confidence scoring and escalation:** Not applicable — workflow execution is deterministic. The agent either executes successfully or reports an error.

**Human-in-the-loop:** All external-facing actions require approval. Internal register updates (e.g., updating action item status) can proceed without approval if the user has the appropriate role.

---

### 9.16 Evaluation & Self-Check Agent

**Purpose:** Assess the quality of every agent output before delivery to the user. Provide transparent confidence scoring, flag uncertainties, and block non-compliant outputs.

**Tools available:**
- Groundedness scorer (compare claims against retrieved sources)
- Citation verifier (check that cited documents contain the claimed information)
- Retrieval relevance scorer (assess whether retrieved documents are the best available)
- Policy compliance checker (classification rules, tone guidelines, prohibited content)
- Usefulness estimator (assess whether the output addresses the user's query)
- Completeness checker (assess whether all parts of the query are addressed)

**Core prompt/persona:** This agent operates transparently but unobtrusively. Its scores are presented as metadata alongside the main agent's output (e.g., a confidence badge). It does not alter the specialist agent's content — it annotates it. If an output fails policy compliance, the Evaluation Agent blocks delivery and returns a policy-compliant explanation.

**Guardrails:**
- Must evaluate every output — no bypass mechanism except for pre-approved low-risk outputs (e.g., simple calendar queries).
- Must not introduce additional latency beyond 2 seconds (evaluation runs concurrently with final formatting).
- Must not alter the substance of the specialist agent's output — only annotate, score, or block.
- Must log all evaluation results regardless of outcome.

**Output formats:**
- Confidence badge: displayed to the user (High / Medium / Low with brief explanation).
- Detailed evaluation report: available on request or to the platform admin (per-dimension scores, flagged issues).
- Quality dashboard data: aggregated scores over time for platform monitoring.

**Confidence scoring:** This agent *is* the confidence scoring mechanism. Its multi-dimensional scoring framework (groundedness, citation quality, retrieval relevance, policy compliance, usefulness, completeness) produces both the per-dimension scores and the composite confidence level.

**Human-in-the-loop:** Policy compliance failures are logged and surfaced to the platform admin. Sustained quality degradation (e.g., average groundedness score drops below 0.7 for a week) triggers an alert to the CTO/CDO for investigation.

---

### 9.17 Stakeholder Sentiment Intelligence Agent

**Purpose:** Monitor and analyse sentiment from investors, analysts, media, politicians, regulators, and community stakeholders toward Alinta and the energy sector.

**Tools available:**
- Media monitoring feed (news, social media, analyst commentary)
- Sentiment scoring engine (NLP-based positive/neutral/negative classification)
- Trend analyser (sentiment trajectory over time by topic and source category)
- Stakeholder entity linker (map sentiment to Alinta assets, executives, and initiatives)
- Alert generator (threshold-based sentiment shift alerts)
- Talking-point adjuster (integrates with Executive Briefing agent to update messaging)

**Core prompt/persona:** Observational and analytical. Reports what is observed without amplification or editorialising. Distinguishes between signal and noise. Tone is measured — sentiment is presented with context, not alarm.

**Guardrails:**
- Must not amplify or distort sentiment readings.
- Must weight sources by credibility (Tier-1 media > anonymous social media).
- Must distinguish Alinta-specific sentiment from sector-wide sentiment.
- Must not monitor individual employees' personal social media accounts.
- Must comply with Australian media and privacy laws in data collection.

**Output formats:**
- Sentiment dashboard (by source category, topic, and time period).
- Sentiment alert (brief notification of significant negative shift).
- Talking-point adjustment memo (proposed changes to executive messaging based on observed themes).
- Periodic sentiment report (weekly for CEO, monthly for Board).

**Confidence scoring and escalation:**
- Sentiment confidence: High (consistent signal across multiple credible sources), Medium (mixed signals or single-source), Low (weak or ambiguous signal).
- Significant negative sentiment shift on High confidence triggers immediate alert to CEO and Head of Corporate Affairs.

**Human-in-the-loop:** Sentiment reports used in board papers or investor communications require review by the Head of Corporate Affairs.

---

### 9.18 ESG & Sustainability Reporting Agent

**Purpose:** Automate ESG data collection, emissions tracking, sustainability metric monitoring, and compliance reporting for Australian and international frameworks.

**Tools available:**
- SQL query tool (emissions data, operational data in Delta Lake)
- External data retrieval (AEMO NEM emissions tracker, NGER data, CDP benchmarks)
- Emissions calculator (Scope 1/2/3 calculations per NGER methodology)
- Peer comparison engine (public ESG data for competitors)
- Report generator (structured ESG/sustainability reports)
- Scenario integration tool (feed emissions metrics into digital twin scenarios)

**Core prompt/persona:** Precise, regulatory-aware, and transparent about methodology. Presents emissions and ESG data with appropriate caveats about data completeness and methodology assumptions. Tone is factual and compliance-oriented for reporting outputs; strategic and forward-looking for board briefings.

**Guardrails:**
- Emissions calculations must follow NGER methodology and be auditable.
- Must clearly distinguish between measured, estimated, and modelled emissions data.
- Must not overstate sustainability performance or use misleading comparisons.
- Must flag data gaps and estimation uncertainties.
- Must track regulatory obligations and deadlines (NGER reporting, Safeguard Mechanism, AASB S1/S2).

**Output formats:**
- Emissions dashboard (Scope 1/2/3, by asset, by business unit, trending).
- Regulatory compliance status (Safeguard Mechanism baseline vs. actual, NGER deadlines).
- Board ESG summary (quarterly — performance, trends, peer comparison, regulatory outlook).
- Scenario-integrated ESG outputs (emissions trajectory under different strategic scenarios).

**Confidence scoring and escalation:**
- Data confidence: High (metered/measured data), Medium (estimated from activity data), Low (modelled or proxy-based).
- Compliance breach alerts (approaching or exceeding Safeguard Mechanism baselines) are escalated to CEO, CFO, and Head of Sustainability.

**Human-in-the-loop:** All ESG reports submitted to regulators (NGER, CDP) or included in board papers require review by the Head of Sustainability and CFO.

---

### 9.19 M&A Due Diligence & Deal Intelligence Agent

**Purpose:** Provide secure, isolated AI analysis for M&A transactions — target screening, document due diligence, financial risk identification, and board paper drafting.

**Tools available:**
- Isolated RAG retrieval (deal room document corpus only — no cross-contamination with general platform)
- Financial analysis tools (ratio analysis, benchmarking, trend analysis)
- Risk identification engine (contract risk, financial risk, operational risk, regulatory risk)
- Target screening tool (match strategic criteria against market data)
- Board paper generator (investment case template)

**Core prompt/persona:** Rigorously analytical, balanced, and discreet. Presents findings objectively with clear evidence. Tone is that of a trusted corporate finance advisor — thorough, cautious, and precise. The agent never advocates for or against a transaction — it presents the evidence.

**Guardrails:**
- Must operate exclusively within the isolated deal room — no access to or from the general platform knowledge base.
- Must not reference deal room content in any context outside the deal room.
- Must not retain deal room data beyond the authorised retention period.
- Must flag all material risks identified, even if they weaken the investment case.
- Must not provide valuations as definitive — always framed as "indicative" or "benchmarked."
- Legal and regulatory analysis must be caveated: "This is an AI-generated assessment. Independent legal review is required."

**Output formats:**
- Target profile (structured: overview, financials, assets, market position, strategic fit, risks).
- Due diligence risk register (categorised risks with severity and evidence).
- Financial analysis pack (key ratios, trends, benchmarks, red flags).
- Board investment case (structured template for board presentation).
- Deal status summary (for deal team updates).

**Confidence scoring and escalation:**
- Analysis confidence: High (based on comprehensive, verified source data), Medium (based on partial data or public sources only), Low (significant data gaps, reliance on estimates).
- All M&A agent outputs carry the caveat: "AI-assisted analysis for deal team consideration. Not a substitute for professional advisory."

**Human-in-the-loop:** All M&A agent outputs require review by the deal team lead before distribution. Board investment cases require CEO and CFO sign-off. No output leaves the deal room without human approval.

---

### 9.20 Continuous Red Team Agent

**Purpose:** Automatically and continuously test all platform agents against adversarial attacks to ensure security posture meets board-grade requirements.

**Tools available:**
- Adversarial test battery (300+ test cases mapped to OWASP LLM Top 10, MITRE ATLAS)
- Classification bypass tester (attempts to extract content above the test user's access tier)
- Prompt injection generator (direct and indirect injection patterns)
- Tool abuse tester (attempts data exfiltration via email/task tools)
- Multi-turn manipulation engine (builds context over multiple turns to probe boundaries)
- Security dashboard renderer

**Core prompt/persona:** This agent has no user-facing persona — it is an internal security tool. It operates adversarially, attempting to break other agents. Its reports are factual and technical, written for the security and platform engineering team.

**Guardrails:**
- Must operate in an isolated sandbox — no impact on production users.
- Must not generate actual harmful content or real data exfiltration — test payloads are synthetic.
- Must log all test activities separately from production audit trails.
- Must not be accessible to non-platform-admin users.

**Output formats:**
- Weekly security report (vulnerabilities found, severity, affected agents, remediation status).
- Daily critical scan summary (classification bypass and prompt injection results only).
- Vulnerability detail record (reproduction steps, affected component, OWASP mapping, recommended fix).
- Security trend dashboard (vulnerability count and remediation rate over time).

**Confidence scoring:** Not applicable — tests produce binary pass/fail results. Failed tests are vulnerabilities.

**Human-in-the-loop:** Critical vulnerabilities (classification bypass, data exfiltration) require immediate platform engineering response. The CTO is notified of all critical findings. Remediation is tracked until resolution.

---

### 9.21 Board Slide Generation Agent

**Purpose:** Generate branded PowerPoint board presentations from structured platform content using Alinta's corporate templates.

**Tools available:**
- Slide generation engine (python-pptx or commercial API via MCP tool server)
- Template library (Alinta corporate templates stored in Unity Catalog Volumes)
- Chart renderer (generates native PowerPoint charts from data arrays)
- Content structurer (transforms narrative output into slide-ready bullet points and talking notes)
- Brand compliance checker (validates fonts, colours, logo placement)

**Core prompt/persona:** The agent is primarily a content structurer and renderer — it transforms rich analytical output into slide-ready format. Its content decisions focus on clarity, conciseness, and visual effectiveness. It follows Alinta's corporate communication standards.

**Guardrails:**
- Must apply Alinta branding consistently — no deviation from approved templates.
- Must include source citations in speaker notes for every slide.
- Must apply classification watermarks (e.g., "BOARD-CONFIDENTIAL") based on the content classification.
- Must not generate more than 30 slides per request without user confirmation.
- Must preserve data accuracy — no rounding or simplification of financial figures unless explicitly requested.

**Output formats:**
- PPTX file (downloadable, fully editable).
- Slide preview (rendered in the platform UI for review before download).
- Speaker notes document (extracted as a separate narrative document if requested).

**Confidence scoring:** Not applicable — slide generation is deterministic. Quality is assessed by user review.

**Human-in-the-loop:** All generated board slides must be reviewed by the requesting user (and typically the Board Secretary) before inclusion in board packs.

---

## 10. UI/UX Requirements

### 10.1 Design Principles

The platform serves the most senior leaders in the organisation. The UI/UX must reflect this audience:

- **Clarity over complexity**: Every screen, every interaction must communicate clearly. No visual clutter, no ambiguous labels, no buried functionality.
- **Brevity with depth**: Default views are concise. Users can drill into detail on demand, but are never forced to wade through it.
- **Executive control**: Users must feel in control. The AI proposes; the human decides. Every AI action is reversible, every suggestion is optional, every output is reviewable.
- **Trust through transparency**: Confidence scores, source citations, and assumption disclosures are always visible — not hidden behind toggles.
- **Consistency**: Terminology, layout, colour coding (RAG status), and interaction patterns are consistent across all capabilities.

### 10.2 Conversational Interface

The primary interaction mode is a chat-based conversational interface.

**Requirements:**

- Clean, distraction-free chat panel — no sidebar clutter by default.
- Messages render rich content: formatted text, tables, charts, citation cards, confidence badges.
- Citation cards are interactive: click to view the source document, section, and page.
- Multi-turn conversation with visible context: previous messages remain visible and scrollable.
- Agent thinking is optionally visible: a "show reasoning" toggle reveals the agent's retrieval steps, tool invocations, and evaluation scores.
- Input supports: typed text, voice input (optional), drag-and-drop document upload for ad-hoc analysis.
- Quick actions: pre-defined prompts for common tasks (e.g., "Morning briefing", "Weekly radar", "Board pack summary").
- Conversation bookmarking and history: executives can save and return to important conversations.
- Persona-aware greeting: the interface adapts its welcome message and quick actions to the user's persona.

### 10.3 Executive Dashboards

Dashboards visualise outputs from the KPI, Radar, and Financial agents.

**Requirements:**

- **KPI dashboard**: Traffic-light (RAG) status for each tracked KPI, with trend sparklines and forecast miniatures. Click any KPI to open a conversational drill-down ("Why is this amber?").
- **Strategic radar dashboard**: Visual radar plot showing signal clusters by domain (regulatory, competitive, technology, market, operational, ESG). Size and colour encode impact and urgency. Click a cluster to see constituent signals and agent assessment.
- **Financial snapshot**: Key financial metrics (revenue, EBITDA, cash, net debt) with variance-to-budget indicators. Drill into any metric for variance analysis.
- **Portfolio view**: Generation assets, retail markets, and key projects with status indicators.
- Dashboards are personalised: each persona sees the KPIs, signals, and financial metrics most relevant to their role.
- Dashboards refresh automatically and indicate data freshness ("Updated 5 minutes ago").
- All dashboards are accessible via the conversational interface: "Show me the KPI dashboard" renders the dashboard within the chat, or opens it in a dedicated view.

### 10.4 Simulation UI

The simulation interface supports scenario definition, execution, and comparison.

**Requirements:**

- **Scenario builder**: Guided form or conversational interface for defining scenario parameters. Assumption library is browsable and searchable. Users can modify individual assumptions or select pre-built assumption sets.
- **Execution monitor**: Progress bar for running simulations. Estimated completion time. Ability to cancel.
- **Results viewer**: Key metrics summary, interactive charts (price duration curves, dispatch stacks, financial waterfall), and downloadable tables.
- **Scenario comparator**: Select 2–4 scenarios for side-by-side comparison. Difference highlighting on all metrics. Toggle between absolute and relative views.
- **Sensitivity explorer**: Interactive sliders for key assumptions. Charts update dynamically to show outcome sensitivity.
- **Assumption transparency**: Every results view includes a collapsible assumption panel showing all input parameters.

### 10.5 Executive Assistant UI

The executive assistant interface integrates with the executive's existing workflow tools.

**Requirements:**

- **Email composer**: Draft email preview with source-highlighted context. One-click "Send for review" or "Send" (with approval gate). Side-by-side view of the relevant document/context and the draft.
- **Calendar view**: Upcoming meetings with pre-read availability indicator (green = pre-read ready, yellow = generating, grey = no pre-read needed). Click to view pre-read.
- **Meeting summary view**: Post-meeting, structured summary appears in the conversation or a dedicated view. Decisions, actions, and risks are colour-coded.
- **Action register**: Filterable list of all tracked actions. Group by meeting, owner, status, or due date. Overdue items highlighted. One-click follow-up generation.
- **Morning briefing**: Auto-generated at configurable time (default 7:00 AM). Displayed as a structured card in the chat interface or pushed to Teams/email.

### 10.6 Mobile and Tablet

Board Directors and C-suite frequently access information on mobile devices (iPhone/iPad) during travel and between meetings.

**Requirements:**

- Responsive design: all core interfaces (chat, dashboards, pre-reads, action register) render well on tablet and mobile.
- Chat interface is the primary mobile interaction mode — dashboards are secondary.
- Touch-optimised: larger tap targets, swipe gestures for navigation.
- Offline capability is not required. **[ASSUMPTION: Executive mobile devices have reliable connectivity.]**
- Push notifications for high-priority alerts (KPI breaches, urgent signals) via the platform's notification integration (Teams or native push).
- Biometric authentication (Face ID / Touch ID) in addition to enterprise SSO.

### 10.7 Voice Interface

The voice interface enables hands-free interaction for executives on the move.

**Requirements:**

- **Voice input**: Tap-to-speak button on mobile; optional wake-word on dedicated devices. Australian English speech recognition with energy-industry vocabulary tuning.
- **Voice output**: Natural-sounding TTS synthesis of agent responses. Responses are adapted for spoken delivery — shorter sentences, less tabular data, more narrative explanation. If the response contains charts or tables, the voice output summarises the key points and directs the user to the visual display.
- **Interruption handling**: If the user speaks during TTS playback, the system stops immediately and listens.
- **Voice-to-visual handoff**: "Show me that as a chart" converts the voice response into a visual display on the same device.
- **Privacy**: Voice input is transcribed and processed server-side. Transcriptions are logged in the audit trail. Users are notified that voice interactions are recorded.
- **Offline**: Voice interface requires connectivity (no offline mode).

### 10.8 Cross-Device Experience

- Session state is server-side, keyed by user identity. Switching devices resumes the conversation seamlessly.
- Visual indicator: "Continuing from [device] at [time]" when resuming.
- Rich content (charts, tables, slide previews) adapts to the target device's form factor automatically.
- Bookmarking: any conversation point can be bookmarked for later return on any device.
- Push notifications route to all active devices; dismissing on one device dismisses on all.

### 10.9 Decision Registry & Board Governance UI

- **Decision register view**: Searchable, filterable list of all board and committee decisions. Filter by date, committee, decision type, status, owner.
- **Decision lineage view**: For any decision, display the full chain: supporting agent analyses, source documents, board paper, meeting summary, resolution, action items, and implementation status.
- **Decision timeline**: Visual timeline showing decisions and their outcomes over months/years.
- **Integration with action register**: Decisions that generate actions are linked; clicking an action navigates to the action register, and vice versa.

### 10.10 Sentiment Dashboard

- Real-time sentiment tracking across source categories (media, analyst, social, regulatory, community).
- Segmented by topic (coal fleet, renewables, retail, corporate, leadership) and entity (Alinta overall, specific assets, competitors).
- Trend charts showing sentiment trajectory over configurable time windows.
- Click-through to underlying source articles/posts.
- Alert indicator for significant negative sentiment shifts.

### 10.11 ESG & Sustainability Dashboard

- Emissions tracker: Scope 1/2/3 by asset, by business unit, trending against baselines (Safeguard Mechanism, internal targets).
- Peer comparison: Alinta vs. AGL, Origin, EnergyAustralia on key ESG metrics (public data).
- Regulatory compliance status: visual indicator of compliance/non-compliance with Safeguard Mechanism, NGER, AASB S1/S2 obligations.
- Scenario overlay: toggle to view emissions trajectory under different strategic scenarios from the digital twin.

### 10.12 Accessibility

- WCAG 2.1 AA compliance for all interfaces.
- Support for screen readers and keyboard navigation.
- Adjustable font sizes and high-contrast mode.
- Plain-language option for complex analytical outputs.
- Voice interface as an alternative to visual interaction for accessibility needs.

---

## 11. Implementation Roadmap

### 11.1 Phase 1: Foundation (Months 0–3)

**Objective:** Establish the core platform infrastructure, ingest the highest-priority document corpus, deliver baseline executive Q&A, and build the foundational security and governance framework.

**Scope:**

- **Infrastructure**: Databricks workspace configured with Unity Catalog, AI Gateway, Model Serving endpoints, and Vector Search.
- **Data ingestion**: Ingest board papers (last 2 years), current strategic plan, current financial forecasts, and key regulatory submissions. Implement document processing pipeline (extraction, classification, chunking, embedding).
- **Classification framework**: Implement document classification tiers and access control model. Map Entra ID groups to Unity Catalog access policies.
- **Core agents**: Deploy Supervisor Agent, Confidential Q&A Agent, and Evaluation Agent.
- **Executive assistant (minimal)**: Basic morning briefing generation and meeting pre-read capability for the CEO.
- **Autonomous governance tiering**: Implement the five-tier autonomy framework. Assign all Phase 1 capabilities to Tier 1 (Advisory Only) or Tier 2 (Supervised Execution). Document tier assignments in the agent registry.
- **Decision registry (foundation)**: Deploy the Board Decision Audit Trail schema and registry tables. Enable manual decision capture by the Board Secretary.
- **Continuous red teaming (baseline)**: Deploy initial red team test battery covering classification bypass and prompt injection. Run daily automated scans.
- **Synthetic data corpus**: Generate initial corpus of 50+ synthetic board documents (PDF, DOCX) and baseline structured datasets covering financials, KPIs, and asset register. Include evaluation Q&A pairs for RAG testing. Synthetic market data (NEM/WEM) and risk register generated for downstream agent testing. All synthetic artefacts stored in the `synthetic_data` schema with `is_synthetic: true` metadata.
- **Observability**: MLflow tracing for all agent interactions. Basic quality dashboard. Security dashboard for red team results.
- **UI**: Conversational chat interface (web) with citation support and confidence badges.

**Dependencies:**
- Databricks workspace provisioned with appropriate SKUs (Premium or Enterprise).
- Access to board portal for document ingestion (API or file export).
- Entra ID group mappings defined for pilot users.
- LLM endpoint (Claude) accessible via Databricks Model Serving or AI Gateway.
- Executive sponsor (CEO/CTO) commitment and pilot user group identified (5–10 users).

**Success criteria:**
- Q&A Agent correctly answers 80%+ of a curated evaluation set of board-document questions with accurate citations.
- Document classification is 95%+ accurate on a manually labelled test set.
- Response latency < 15 seconds for Q&A queries.
- Red team scans: zero critical vulnerabilities (classification bypass, prompt injection) in production agents.
- Pilot users (CEO + 2–3 C-suite) provide positive qualitative feedback.
- Full audit trail operational for all interactions.
- Governance tier framework documented and approved by CTO.

---

### 11.2 Phase 2: Intelligence Expansion (Months 3–6)

**Objective:** Expand agent capabilities across competitive, strategic, financial, regulatory, and ESG domains. Introduce the knowledge graph, board slide generation, stakeholder sentiment, executive personalisation, and multi-model routing.

**Scope:**

- **New agents**: Competitive Analysis Agent, Strategic Gap Analysis Agent, KPI & Exception Monitoring Agent, Regulatory & Market Intelligence Agent, ESG & Sustainability Reporting Agent, Stakeholder Sentiment Intelligence Agent.
- **Executive assistant expansion**: Meeting intelligence (post-meeting summaries, action extraction), email drafting, calendar integration.
- **Knowledge graph (initial)**: Deploy entity and relationship tables. Implement entity extraction from ingested documents. Support multi-hop queries for asset, initiative, and risk relationships.
- **Board slide generation**: Deploy Board Slide Generation Agent with Alinta corporate templates. Integrate with Briefing Synthesis and Workflow Orchestration.
- **Stakeholder sentiment**: Begin ingesting media and analyst feeds for sentiment tracking. Deploy sentiment dashboard.
- **Executive personalisation**: Deploy personalisation profile storage. Begin implicit preference learning from query patterns and feedback.
- **Multi-model routing (initial)**: Implement task-aware routing across 3–4 models (frontier, general, fast). Deploy routing dashboard for CTO.
- **Scheduled outputs**: Weekly regulatory digest, weekly KPI snapshot, weekly strategic radar (initial version).
- **External data integration**: Begin ingesting AEMO market data, regulatory publications, news feeds, ESG data (NGER, AEMO emissions tracker).
- **Financial analysis (basic)**: Portfolio & Financial Analysis Agent with access to structured financial data in Delta Lake.
- **Meeting Intelligence Agent**: Pre-reads, summaries, action register. Automatic decision capture feeding the Decision Registry.
- **Cross-device persistence**: Implement server-side session state enabling device switching.
- **UI expansion**: Executive dashboards (KPI, financial snapshot, sentiment, ESG). Mobile-responsive design. Decision registry view.
- **Workflow orchestration (basic)**: Action item creation in Jira/ServiceNow from meeting summaries.

**Dependencies:**
- Financial data available in Delta Lake (ETL from ERP/financial systems).
- AEMO data feed access configured.
- Microsoft Graph API integration for email/calendar (with appropriate consent and security review).
- Jira/ServiceNow API access for task creation.
- KPI definitions and thresholds agreed with business owners.
- Meeting transcription capability (Teams integration) operational.
- Alinta corporate board templates provided in PPTX format.
- Media and analyst feed subscriptions in place.
- ESG data sources (NGER, AEMO emissions tracker) accessible.
- Knowledge graph entity schema agreed with Strategy and Risk teams.

**Success criteria:**
- Competitive profiles rated as "useful" or "very useful" by Strategy team in blind evaluation.
- KPI Agent correctly detects 90%+ of simulated anomalies in a test dataset.
- Regulatory digest rated as covering 90%+ of material developments in a retrospective review.
- Meeting intelligence accurately captures 85%+ of decisions and action items from a set of test meetings.
- Knowledge graph contains 500+ entities and 1,000+ relationships with > 90% accuracy on a manually verified sample.
- Board slide generation produces usable first drafts rated > 3.5/5 by the Board Secretary.
- Multi-model routing reduces token cost by 20%+ vs. single-model baseline with < 5% quality degradation.
- Weekly active users among pilot group > 70%.
- 50%+ reduction in board pack preparation time reported by Strategy team.

---

### 11.3 Phase 3: Simulation & Foresight (Months 6–12)

**Objective:** Deliver digital twin / scenario modelling, market simulation, early-warning radar, strategic recommendation engine, executive briefing synthesis, voice interface, and M&A capability at board-grade quality.

**Scope:**

- **New agents**: Digital Twin / Scenario Modelling Agent, Energy Market Simulation Agent, Early Warning & Signal Detection Agent, Strategic Recommendation Agent, Executive Briefing Synthesis Agent, M&A Due Diligence Agent (initial deployment in isolated mode).
- **Simulation engine**: Implement or integrate market simulation models (NEM/WEM dispatch, portfolio P&L). Register models in Unity Catalog/MLflow. Scenario library with AEMO ISP scenarios and custom Alinta scenarios.
- **Signal repository**: Implement signal storage, clustering, and radar visualisation.
- **Knowledge graph maturity**: Expand graph to cover competitors, regulations, contracts, and people. Implement automated relationship extraction on new document ingestion.
- **Voice interface**: Deploy STT/TTS integration. Enable voice-first interaction on mobile. Australian English tuning for energy terminology.
- **M&A capability**: Deploy isolated deal room infrastructure with separate Unity Catalog schema. M&A agent available for activation when a deal process begins.
- **Red teaming expansion**: Full OWASP LLM Top 10 test battery. Multi-turn manipulation testing. Weekly comprehensive scans.
- **ESG maturity**: Scope 1/2/3 emissions tracking operational. Safeguard Mechanism compliance monitoring. Peer comparison from public data.
- **External data expansion**: Analyst reports, broader news monitoring, social media sentiment, parliamentary Hansard feeds.
- **Governance tier promotion**: Evaluate and promote proven Phase 1/2 capabilities from Tier 1/2 to Tier 3 (Guided Autonomy) where evaluation scores justify it.
- **UI expansion**: Simulation UI (scenario builder, comparator, sensitivity explorer). Strategic radar dashboard. Briefing generation interface. ESG dashboard. Voice controls.

**Dependencies:**
- Market simulation model development or integration (potentially with PLEXOS or equivalent).
- Historical market data loaded for model calibration and backtesting.
- Signal sources identified and ingestion pipelines built.
- Analyst report and ESG data subscriptions in place.
- Voice service provider selected and Australian-region deployment confirmed.
- M&A deal room security architecture reviewed and approved by CISO.

**Success criteria:**
- Simulation results within 15% of historical actuals on key financial metrics in backtesting.
- Early-warning radar captures 90%+ of material events in a retrospective 6-month review.
- Strategic recommendations rated as "credible" by CEO and Chief Strategy Officer in blind evaluation.
- Executive briefings save 40%+ of preparation time for board meetings.
- Voice interface achieves > 95% speech recognition accuracy for energy-industry queries.
- M&A agent successfully processes a test due diligence exercise with zero data leakage to non-deal-room users.
- ESG agent correctly calculates Scope 1 emissions within 2% of NGER-reported figures.
- Board Directors and full C-suite are active users (> 80% monthly engagement).

---

### 11.4 Phase 4: Advanced Intelligence & Optimisation (Months 12+)

**Objective:** Advance simulation sophistication, expand autonomous operation, fully mature the knowledge graph, optimise cost and performance, and deeply integrate the platform into all executive workflows.

**Scope:**

- **Advanced simulation**: Competitive response modelling, multi-market interaction (NEM + WEM + gas), portfolio optimisation under uncertainty. Decision-grade model validation.
- **Fully integrated executive assistant**: Autonomous meeting lifecycle management, proactive executive support across all interaction channels (text, voice, mobile), integrated action and decision management.
- **Advanced early warning**: Predictive signal detection (leading indicators), cross-domain correlation, and scenario-trigger automation (e.g., "If gas price rises above $X, automatically run portfolio stress test").
- **Knowledge graph maturity**: Full entity-relationship model with automated relationship extraction from new documents. NL-to-GQL query translation. Visual graph explorer in production.
- **Advanced sentiment**: Predictive sentiment modelling (anticipate sentiment shifts from planned announcements). Integrated talking-point adjustment across briefing and communications workflows.
- **Governance tier advancement**: Promote validated capabilities to Tier 4 (Delegated Authority) where appropriate — e.g., automated signal classification, routine KPI alert generation.
- **Multi-model routing maturity**: Expand model portfolio to 10+ models. Implement automatic quality-based retry routing. Achieve 30-40% cost reduction vs. single-model baseline.
- **Executive memory maturity**: Full personalisation profiles with preference-aware response generation. Style calibration for communication drafting.
- **Decision registry maturity**: Full decision lineage from agent analysis through board resolution to implementation tracking. Audit-ready reporting for regulators.
- **Cost optimisation**: Prompt caching, semantic caching, embedding index compression, personalised model routing.
- **Performance optimisation**: Retrieval precision improvement through fine-tuned re-rankers and user feedback loops.
- **Expanded integration**: Deeper CRM integration, trading system dashboards, operational historian feeds.
- **Voice maturity**: Wake-word activation, multi-language support (if required for international stakeholders), voice-to-visual handoff refinements.
- **Continuous improvement**: A/B testing of agent prompts, automated evaluation dataset expansion from production traces, model refresh cadence.

**Dependencies:**
- Sustained executive sponsorship and budget allocation.
- Availability of domain experts for simulation model validation.
- Maturity of Databricks Agent Bricks features (ongoing platform evolution).
- Regulatory clarity on AI use in critical infrastructure contexts.

**Success criteria:**
- Platform recognised as a critical executive tool: used in preparation for every board meeting.
- Measurable improvement in decision quality (assessed via annual executive survey).
- Simulation models at calibrated or decision-grade maturity for core NEM/WEM scenarios.
- Knowledge graph contains 5,000+ entities with comprehensive relationship coverage.
- Operating cost per query optimised by 30%+ vs. Phase 1 baseline.
- Zero data classification breaches in 12-month period.
- Decision registry contains all board and ExCo decisions for the preceding 12 months with full lineage.
- Governance tiering actively managed: at least 5 capabilities promoted to Tier 3+ based on evaluation evidence.

---

## 12. Risks & Mitigations

### 12.1 Hallucination and Mis-Grounding

**Risk:** LLMs may generate plausible but incorrect statements not supported by the source documents. At board level, even a single hallucinated financial figure or misattributed strategic position could erode trust and lead to poor decisions.

**Impact:** Critical.

**Mitigations:**
- Evaluation Agent assesses groundedness on every output (Section 9.16).
- Low-confidence outputs are flagged with explicit caveats.
- All factual claims must be cited — uncited claims are flagged by the Evaluation Agent.
- Regular evaluation on curated "golden" Q&A sets to track hallucination rate over time.
- Human review required for all outputs used in board papers or external communications.
- Conservative system prompts: agents are instructed to say "I don't know" rather than speculate.

---

### 12.2 Misuse or Over-Reliance on AI

**Risk:** Executives may treat AI outputs as definitive rather than advisory, reducing critical thinking. Or the platform may be used for purposes outside its intended scope.

**Impact:** High.

**Mitigations:**
- All AI outputs labelled as "AI-generated for executive consideration."
- Recommendations always present multiple options, not single directives.
- Simulation outputs carry model maturity labels (directional / calibrated / decision-grade).
- Onboarding programme for all users covering appropriate use, limitations, and responsible AI principles.
- Usage monitoring to detect unusual patterns (e.g., extreme query volumes, queries outside normal scope).

---

### 12.3 Data Classification Errors and Access Control Misconfigurations

**Risk:** A document is incorrectly classified (e.g., a Board-Only document classified as Internal), or access controls are misconfigured, resulting in unauthorised access to sensitive information.

**Impact:** Critical.

**Mitigations:**
- Classification is applied at ingestion with automated checks, but human review is required for ambiguous cases.
- Regular classification audits (quarterly) on a random sample of documents.
- Defence-in-depth: classification is enforced at retrieval, generation, and response delivery layers.
- Access control changes require dual approval and are logged.
- Penetration testing of the access control model during Phase 1 and annually thereafter.
- "Canary documents": synthetic documents at each classification tier used to verify that access controls are functioning correctly.

---

### 12.4 Simulation Model Risk

**Risk:** Simulation models produce misleading results due to flawed assumptions, inadequate calibration, or use outside their valid range. Executives act on simulation outputs without appreciating their limitations.

**Impact:** High.

**Mitigations:**
- All simulations carry model maturity labels. Only "calibrated" or "decision-grade" models are used for formal decision support.
- Backtesting against historical data is performed and published with each model version.
- Sensitivity analysis is mandatory for all scenario outputs.
- Model risk governance: model inventory, model cards, independent review (by a team separate from the model developers), and retirement schedule.
- Executive training on interpreting simulation outputs, understanding uncertainty, and recognising model limitations.

---

### 12.5 Executive Change Management and Trust

**Risk:** Executives do not adopt the platform, either due to scepticism about AI, discomfort with technology, or poor initial experiences.

**Impact:** High (undermines the entire initiative).

**Mitigations:**
- Phased rollout starting with high-value, low-risk use cases (Q&A over familiar documents) to build confidence.
- CEO as the initial champion user — if the CEO uses it, others follow.
- White-glove onboarding for Board Directors (one-on-one sessions, not group training).
- Rapid feedback loops: user feedback directly informs the next iteration (weekly sprint cycles in Phase 1).
- "Wow moments": identify specific questions or tasks where the platform dramatically outperforms the manual process, and ensure these are part of the onboarding experience.
- Transparent about limitations: proactively acknowledging what the platform cannot do builds trust more than over-promising.

---

### 12.6 Vendor and Model Lock-In

**Risk:** Deep dependency on a single LLM provider (e.g., Anthropic Claude) creates risk if the provider changes pricing, terms, or availability.

**Impact:** Medium.

**Mitigations:**
- AI Gateway provides provider abstraction. The platform is designed to support multiple LLM backends.
- Prompt engineering follows provider-agnostic patterns where possible.
- Regular evaluation of alternative models (e.g., GPT-4o, Llama 3.1) to maintain fallback readiness.
- Databricks' own model serving capabilities provide a hedge against external provider disruption.
- Embedding models and re-rankers can be swapped independently of the generative LLM.

---

### 12.7 Regulatory Scrutiny and AI in Critical Infrastructure

**Risk:** As an operator of critical infrastructure, Alinta may face regulatory scrutiny regarding AI use in executive decision-making. Regulators (AEMO, AER) or government bodies may question whether AI-augmented decisions meet governance standards.

**Impact:** Medium-High.

**Mitigations:**
- The platform is positioned as a decision-support tool, not a decision-making system. Humans make all decisions.
- Full audit trails support regulatory inquiry.
- AI governance framework aligned with Australia's voluntary AI Ethics Principles and emerging mandatory standards.
- Proactive engagement with regulators on AI use in the energy sector.
- The platform does not directly control any operational or trading systems — it is an information and analysis layer.

---

### 12.8 Data Privacy and Employee Consent

**Risk:** The executive assistant capabilities (email analysis, calendar access, meeting transcription) involve processing personal information of employees. Insufficient consent or transparency could breach the Australian Privacy Act or erode employee trust.

**Impact:** Medium-High.

**Mitigations:**
- Clear privacy impact assessment (PIA) before deploying executive assistant capabilities.
- Opt-in consent model: executive assistant features are activated only with the explicit consent of the participating executive.
- Meeting transcription requires notification to all participants.
- Data minimisation: only process data necessary for the declared purpose.
- Right of access: executives can view and delete their processed data.
- Privacy policy update to cover AI processing of workplace communications.

---

### 12.9 Knowledge Graph Accuracy and Drift

**Risk:** The knowledge graph relies on automated entity and relationship extraction from documents. Errors in extraction — incorrect relationships, missed entities, or stale relationships — could lead to misleading multi-hop query results. Executives may treat graph-derived answers as definitive without appreciating extraction uncertainty.

**Impact:** Medium-High.

**Mitigations:**
- Every graph entity and relationship carries a confidence score and source document references.
- Periodic human validation of graph accuracy on a random sample (quarterly, minimum 200 entities and relationships).
- Graph query results include the traversal path and source documents for transparency.
- Low-confidence graph paths are flagged: "This relationship is inferred from [source] with moderate confidence."
- Stale entity detection: entities not refreshed from new documents within 12 months are flagged for review.
- The graph is a supplement to RAG retrieval, not a replacement — both are used and cross-validated.

---

### 12.10 Voice Interface Security and Privacy

**Risk:** Voice interactions introduce new attack vectors (voice spoofing, eavesdropping in shared spaces) and privacy concerns (recorded speech in sensitive contexts). Executives discussing board-confidential topics via voice in non-private settings could expose sensitive information.

**Impact:** Medium.

**Mitigations:**
- Voice authentication layered on top of device authentication (biometric + enterprise SSO).
- Voice sessions are transcribed and logged — users are notified of this at session start.
- Guidance for executives: "Voice interaction is not recommended for Board-Only classified topics in non-private settings."
- The voice interface enforces the same classification controls as text — no security bypass.
- Voice recordings are not stored beyond transcription; only the text transcript is retained.

---

### 12.11 M&A Data Isolation Failure

**Risk:** If the M&A deal room's data isolation fails — either through a technical misconfiguration or an agent hallucinating deal room content into a general platform response — the consequences include insider trading risk, breach of confidentiality agreements, and potential legal liability.

**Impact:** Critical (but low likelihood given architectural controls).

**Mitigations:**
- M&A deal rooms use a physically separate Unity Catalog schema with no cross-schema access grants.
- Red team testing specifically targets deal room isolation (can a non-deal-room user extract deal content?).
- The M&A agent operates with a separate system prompt that includes hard isolation instructions.
- Deal room access is audited in real-time; anomalous access patterns trigger immediate alerts.
- Annual penetration test of deal room isolation by an independent security team.

---

### 12.12 Sentiment Intelligence Misinterpretation

**Risk:** Sentiment analysis may misclassify neutral or positive coverage as negative (or vice versa), or executives may over-react to sentiment readings that are noise rather than signal. Sentiment dashboards could create a culture of reactivity rather than strategic thinking.

**Impact:** Medium.

**Mitigations:**
- Sentiment scores are presented with source attribution — executives can click through to the underlying content.
- Sentiment is trended over time, not presented as point-in-time readings (reduces noise).
- Source credibility weighting reduces the influence of low-quality sources.
- The platform distinguishes between Alinta-specific and sector-wide sentiment.
- Onboarding includes guidance on interpreting sentiment intelligence — trend matters more than individual readings.

---

### 12.13 Autonomous Governance Tier Creep

**Risk:** Over time, pressure to increase efficiency may lead to premature promotion of capabilities to higher autonomy tiers without adequate evaluation evidence, creating governance risk.

**Impact:** Medium.

**Mitigations:**
- Tier promotion requires documented evidence: 90 consecutive days of evaluation scores above threshold, zero policy compliance failures, and executive sponsor sign-off.
- The CTO reviews all tier promotions.
- Any policy compliance failure or security incident triggers automatic tier demotion.
- Quarterly governance review of all tier assignments by the CTO and CRO.
- Tier 5 (Fully Autonomous) is reserved for non-consequential, well-validated operations (e.g., document classification, pipeline execution) — never for content generation or external actions.

---

## 13. Open Questions & Assumptions

### 13.1 Open Questions

| ID | Question | Impact Area | Required By |
|----|----------|-------------|-------------|
| OQ-1 | Which cloud provider and region will host the Databricks workspace? Azure Australia East is assumed but not confirmed. | Infrastructure, data residency | Phase 1 kickoff |
| OQ-2 | What is the approved LLM provider mix? Is Claude the primary model, and which fallbacks are acceptable? | LLM serving, cost, AI Gateway | Phase 1 kickoff |
| OQ-3 | What is the scope of Microsoft 365 integration? Full Graph API access (email, calendar, Teams transcripts) or limited? | Executive assistant, meeting intelligence | Phase 1 (basic), Phase 2 (full) |
| OQ-4 | What existing market simulation tools does Alinta use (PLEXOS, Prophet, internal)? Build new vs. integrate? | Simulation engine, Phase 3 scoping | Phase 2 planning |
| OQ-5 | What is the data residency policy for LLM inference? Is external API processing (e.g., Anthropic cloud) acceptable with contractual safeguards, or must all inference occur within Alinta-controlled environments? | Security, architecture | Phase 1 kickoff |
| OQ-6 | What is the board portal platform? What APIs does it expose? | Document ingestion, workflow orchestration | Phase 1 |
| OQ-7 | What CRM does Alinta use? Salesforce, Dynamics, or other? | Customer data integration | Phase 2 |
| OQ-8 | What is the appetite for real-time meeting transcription? Are there privacy or IR concerns? | Meeting intelligence | Phase 2 |
| OQ-9 | What is the budget envelope for the platform (capital and operating)? What compute tiers are available? | All phases, cost governance | Phase 1 kickoff |
| OQ-10 | What existing AI governance framework does Alinta have? Does a new framework need to be developed? | Governance, risk, compliance | Phase 1 |
| OQ-11 | What are the AEMO/AER expectations (if any) regarding AI use in energy company decision-making? | Regulatory risk | Ongoing |
| OQ-12 | What external data subscriptions does Alinta currently hold (analyst reports, news, ESG data)? | External intelligence, Phase 2/3 | Phase 1 |
| OQ-13 | What is Alinta's preferred voice service provider for STT/TTS? Are Azure Speech Services acceptable, or is a specific provider required? | Voice interface, data residency | Phase 3 |
| OQ-14 | Does Alinta have an existing board governance tool (e.g., Diligent, BoardEffect) that the Decision Registry should integrate with or replace? | Decision Registry | Phase 1 |
| OQ-15 | What social media monitoring tools or feeds does Alinta currently use? Can these be integrated into the sentiment intelligence pipeline? | Sentiment Intelligence | Phase 2 |
| OQ-16 | What is the frequency and scope of M&A activity? Is the M&A agent needed for continuous readiness or periodic activation? | M&A Agent, infrastructure sizing | Phase 3 |
| OQ-17 | What ESG reporting frameworks is Alinta currently committed to (NGER, CDP, GRI, TCFD, AASB S1/S2)? Which are mandatory vs. voluntary? | ESG Agent | Phase 2 |
| OQ-18 | Is there an existing red team or penetration testing programme for AI systems? Can it be leveraged, or does the platform need its own? | Red Teaming | Phase 1 |

### 13.2 Assumptions

| ID | Assumption | Impact if Incorrect |
|----|-----------|---------------------|
| A-1 | Alinta operates Azure Active Directory (Entra ID) for identity management. | Access control model needs redesign for alternative IdP. |
| A-2 | Alinta uses Microsoft 365 (Outlook, Teams, SharePoint) as its core productivity suite. | Executive assistant and meeting intelligence integration patterns change. |
| A-3 | The Databricks workspace is or will be deployed in an Australian region (Azure Australia East). | Data residency requirements may not be met; architecture redesign required. |
| A-4 | Board papers and key strategy documents are available in digital format (PDF/DOCX) and can be exported from the board portal. | Manual digitisation pipeline needed if documents are only in physical or non-exportable format. |
| A-5 | Financial data (budgets, actuals, forecasts) is or will be available in Delta Lake tables. | Additional ETL development required; financial analysis capability delayed. |
| A-6 | Tone/style calibration for the executive assistant will be based on a sample of past communications, provided with executive consent. | Generic communication style if calibration data is unavailable. |
| A-7 | Real-time transcription integration with Microsoft Teams is available or will be implemented. | Meeting intelligence limited to post-meeting notes/manual input. |
| A-8 | Alinta has existing market simulation models that can be integrated or whose logic can be replicated. | Simulation capability requires greenfield model development; Phase 3 timeline extends. |
| A-9 | Executive mobile devices have reliable internet connectivity. | Offline capability would need to be added. |
| A-10 | Alinta will provide or procure access to regulatory publication feeds and external data subscriptions. | External intelligence capabilities are limited to publicly accessible data only. |
| A-11 | The platform will serve approximately 30–50 active users (Board + C-suite + ELT + support staff). | Capacity planning and cost model change for larger user base. |
| A-12 | Alinta's risk appetite permits the use of external LLM APIs (with appropriate contractual safeguards) for non-Board-Only content. | All inference must be self-hosted, significantly increasing compute costs. |
| A-13 | Azure Speech Services (or equivalent STT/TTS provider) can be deployed within an Australian region for voice interface data residency compliance. | Voice interface deployment may be delayed pending provider availability in-region. |
| A-14 | Alinta's corporate board presentation templates are available in PPTX format and can be provided for integration into the slide generation engine. | Slide generation will use generic professional templates until Alinta templates are available. |
| A-15 | Alinta's M&A activity is periodic rather than continuous. The M&A deal room infrastructure is provisioned on-demand when a deal process is initiated. | If continuous M&A readiness is required, persistent deal room infrastructure must be maintained. |
| A-16 | Alinta reports under NGER and the Safeguard Mechanism. AASB S1/S2 mandatory climate reporting will apply from FY2026 or FY2027. | ESG agent scope and timeline adjust based on actual reporting obligations. |
| A-17 | Media monitoring and social media sentiment data can be sourced from commercial providers (e.g., Meltwater, Brandwatch) or public APIs. | If no commercial feed is available, sentiment intelligence is limited to news RSS and public social media APIs. |
| A-18 | The platform will manage approximately 20+ AI models across the intelligent routing portfolio within 12 months of launch. | If fewer models are available, routing optimisation benefits are reduced but the architecture still functions. |
| A-19 | Synthetic data uses fabricated but plausible Alinta Energy asset names (Loy Yang B, Yandin Wind Farm, Newman Power Station, Wagerup Power Station, etc.) and market contexts. No real Alinta data is used in the synthetic corpus. All financial figures, KPIs, and market data are entirely fictional. | If Alinta requests that real asset names not be used in synthetic content, generic placeholder names can be substituted. |

---

## 14. Evaluation, Governance, and Controls

### 14.1 Evaluation Framework

**Offline evaluation (pre-deployment and periodic):**

- **Curated evaluation datasets**: For each agent, maintain a "golden" dataset of representative queries with known-correct answers (for Q&A), expected gap categories (for strategic gap), expected competitive profiles (for competitive analysis), and so on.
- **Automated scoring**: Run the agent against the evaluation dataset and score using:
  - Retrieval precision and recall (measured against labelled relevant documents).
  - Answer correctness (judged by LLM-as-judge with human calibration).
  - Groundedness (fraction of claims supported by retrieved sources).
  - Hallucination rate (fraction of responses containing unsupported claims).
  - Citation accuracy (fraction of citations that correctly reference the claimed content).
  - Policy compliance rate.
- **Evaluation cadence**: After every model change, prompt change, or major data update. At minimum monthly.

**Online evaluation (production):**

- **Evaluation Agent scoring**: Every production output is scored in real-time (Section 9.16).
- **User feedback**: Thumbs-up/down and optional free-text feedback on every response. Aggregated weekly.
- **A/B testing**: When testing prompt variants or model changes, route a fraction of traffic to the new variant and compare evaluation scores.

**Human review:**

- Monthly review of a random sample of agent outputs (50 per agent per month) by domain experts.
- Quarterly review of evaluation dataset quality and coverage — update datasets to reflect evolving document corpus and query patterns.
- Annual "red team" exercise: adversarial testing of the platform by an independent team to identify failure modes.

### 14.2 AI Gateway Policies

| Policy | Configuration |
|--------|---------------|
| **Input guardrails** | PII detection and masking in logs (not in processing). Prompt injection detection. Off-topic query rejection. |
| **Output guardrails** | Profanity filter. Harmful content detection. Classification-breach detection (output references content above user's tier). |
| **Rate limits** | Per-persona and per-agent-type limits (Section 6.6). |
| **Token budgets** | Daily caps per persona group. Budget alerts at 80%. Auto-downgrade model tier at 90%. Hard stop at 100%. |
| **Provider routing** | Primary: Claude 3.5 Sonnet. Complex reasoning: Claude 3 Opus. Fallback: GPT-4o. Cost-optimised simple queries: Llama 3.1 (self-hosted). |
| **Safe defaults** | If no routing rule matches, use the primary model with maximum guardrails enabled. |
| **Logging** | All requests and responses logged (sanitised for PII in logs) to Delta Lake for audit, monitoring, and evaluation. |

### 14.3 Model Inventory and Governance

**Model inventory:** Every model deployed on the platform is registered in Unity Catalog / MLflow Model Registry with:

- Model name and version.
- Model type (generative LLM, embedding, re-ranker, anomaly detection, simulation).
- Provider and hosting details.
- Model card: purpose, training data summary, known limitations, evaluation results, responsible AI assessment.
- Approval record: who approved deployment and when.
- Dependencies: what agents and pipelines depend on this model.

**Approval workflow:**
- New model deployment requires approval from the platform technical lead and the CTO/CDO.
- Model version updates require approval from the platform technical lead.
- Evaluation results must be reviewed before approval.

**Retirement policy:**
- Models not used in 90 days are flagged for review.
- Deprecated models are retained for 12 months (for audit and reproducibility) before archival.
- Model retirement requires a migration plan for dependent agents.

### 14.4 Audit and Compliance

**Logging:**
- Every user interaction (query, feedback, approval, workflow trigger) is logged with: timestamp, user identity, session ID, agent(s) involved, retrieval results, model(s) used, token counts, evaluation scores, and final response.
- Logs are immutable (append-only Delta Lake tables with deletion protection).
- Log retention: 7 years (aligned with standard corporate record retention).

**Audit support:**
- Internal audit can query the log tables directly (with appropriate access) or request standardised audit reports.
- Reports available: user access summary, classification-tier access patterns, query volume by persona, evaluation score trends, model usage and cost, workflow execution log.

**Compliance reporting:**
- Quarterly compliance report for the Audit & Risk Committee covering: access control reviews, classification accuracy, evaluation scores, incident log (if any), and cost governance.
- Annual AI governance report for the Board covering: platform performance, risk assessment, model inventory, ethical AI compliance, and forward roadmap.

### 14.5 Autonomous Governance Tiering Framework

**Purpose:** Provide a structured, transparent framework for managing the autonomy level of each platform capability — from fully human-supervised to fully autonomous — with governance controls calibrated to each tier.

**Tier definitions:**

| Tier | Name | Governance Controls | Review Cadence |
|------|------|--------------------:|---------------|
| 1 — Advisory Only | Agent provides information. Human decides and acts. | Standard evaluation scoring. Audit trail. | Quarterly. |
| 2 — Supervised Execution | Agent proposes action. Human approves each instance. | Per-instance approval logging. Rejection rate monitoring. | Monthly. |
| 3 — Guided Autonomy | Agent executes pre-approved categories within guardrails. | Guardrail compliance monitoring. Exception logging. Periodic sample review. | Monthly. |
| 4 — Delegated Authority | Agent acts autonomously within mandate. Escalates edge cases. | Continuous monitoring. Statistical quality sampling. Quarterly human review of a random sample (50+ outputs). | Monthly + quarterly deep review. |
| 5 — Fully Autonomous | Agent operates independently. Audit review only. | Automated quality monitoring. Annual independent audit. Reserved for low-risk, non-consequential operations. | Quarterly + annual audit. |

**Tier assignment process:**
1. Initial assignment by the platform technical lead, based on capability risk assessment.
2. Approval by the CTO and the relevant business sponsor.
3. Documentation in the agent registry (Unity Catalog table: `platform_config.agent_registry`).

**Tier promotion criteria:**
- Evaluation scores above the defined threshold for 90 consecutive days.
- Zero policy compliance failures in the evaluation period.
- Red team testing passed at the target tier level.
- Executive sponsor sign-off.
- CTO approval.

**Tier demotion triggers:**
- Any policy compliance failure → immediate demotion to Tier 1.
- Security incident involving the capability → immediate demotion to Tier 1.
- Sustained evaluation score degradation (below threshold for 14 consecutive days) → demotion by one tier.

**Transparency:** The autonomy tier of each capability is visible to users in the platform UI and documented in the governance dashboard. Board members can query: "What autonomy level does each platform capability operate at?"

### 14.6 Continuous Red Teaming Governance

**Scope:** All agents, tools, and integration points are in scope for adversarial testing.

**Test framework:** Tests are mapped to OWASP LLM Top 10, MITRE ATLAS, and the NIST AI Risk Management Framework.

**Cadence:**
- Daily: Critical scan (classification bypass, prompt injection) — automated.
- Weekly: Full battery (all OWASP LLM Top 10 categories) — automated.
- Quarterly: Extended adversarial testing including multi-turn manipulation and tool abuse scenarios.
- Annually: Independent penetration test by an external security firm.

**Remediation SLAs:**
- Critical vulnerabilities (classification bypass, data exfiltration): remediation within 24 hours. Affected capability demoted to Tier 1 until resolved.
- High vulnerabilities: remediation within 7 days.
- Medium vulnerabilities: remediation within 30 days.
- Low vulnerabilities: tracked and addressed in next platform release.

**Reporting:** Weekly security report to CTO. Quarterly security summary for Audit & Risk Committee. Annual security assessment for the Board.

### 14.7 Decision Registry Governance

- Decision records are governed corporate records. Once finalised (by the Board Secretary for board decisions, by the CEO's Chief of Staff for ExCo decisions), they are immutable.
- Corrections are recorded as amendments (timestamped, attributed, appended to the amendment history).
- The Decision Registry is accessible to internal audit and can be produced for regulatory inquiry.
- Quarterly review of decision registry completeness by the Board Secretary.
- Annual reconciliation of decision registry against formal board minutes.

---

## 15. Executive Foresight and Alerting

### 15.1 Early-Warning Radar Concept

The executive radar is a structured intelligence product that aggregates and prioritises signals from diverse sources into a consumable format for the Board and C-suite. It operates as a continuous background process, not a reactive query.

**Conceptual model:** Think of a weather radar for strategic intelligence. The radar scans the environment continuously. Most of the time, it shows clear skies — routine activity, expected developments, noise. When a meaningful signal appears — a regulatory shift, a competitor move, a market dislocation, an operational anomaly — it shows up as a blip on the radar, sized and coloured by impact and urgency.

The radar reduces the cognitive burden on executives. Instead of reading hundreds of articles, reports, and emails, they review a curated, prioritised, and contextualised intelligence product.

### 15.2 Signal Categories and Sources

| Category | Example Signals | Sources |
|----------|----------------|---------|
| **Regulatory** | New AEMC rule change, AER draft determination, AEMO ISP update, state policy change. | AEMO, AER, AEMC, ESB, state regulators, Hansard, government media releases. |
| **Competitive** | Competitor generation project announcement, M&A activity, retail offer launch, executive change. | ASX announcements, media, analyst reports, competitor websites. |
| **Market** | Unusual price movements, demand shifts, fuel price changes, interconnector constraints. | AEMO MMS, gas market data, commodity indices. |
| **Technology** | Battery cost milestone, new solar efficiency record, hydrogen breakthrough, grid-forming inverter deployment. | Industry publications, research databases, patent filings. |
| **Operational** | Asset performance anomaly, safety incident trend, supply chain disruption. | Internal SCADA, operational databases, supplier communications. |
| **Customer** | Churn acceleration, NPS decline, complaint volume increase, competitor switching patterns. | CRM, complaint management, market research. |
| **ESG / Climate** | New emissions policy, climate litigation, ESG rating change, extreme weather forecast. | Government publications, legal databases, ESG data providers, BOM. |
| **Geopolitical** | Trade policy change, international energy policy, supply chain geopolitical risk. | News media, geopolitical intelligence services. |
| **Cyber** | Sector-specific threat advisory, vulnerability disclosure, peer incident. | ACSC, industry ISAC, threat intelligence feeds. |

### 15.3 Prioritisation and Alert Thresholds

**Prioritisation framework:**

Each signal is scored on two dimensions:
- **Impact** (1–5): How significantly could this affect Alinta's strategy, financial performance, risk profile, or operations?
- **Urgency** (1–5): How quickly does this require awareness or action?

**Composite priority = Impact x Urgency**, yielding a score of 1–25.

| Priority Band | Score | Response |
|---------------|-------|----------|
| **Critical** | 20–25 | Immediate alert to CEO and relevant C-suite. Same-day impact assessment. |
| **High** | 12–19 | Included in next scheduled radar. Flagged for executive attention. |
| **Medium** | 6–11 | Included in weekly radar and monthly foresight brief. |
| **Low** | 1–5 | Logged for trend analysis. Included in quarterly review only if part of a cluster. |

### 15.4 Alert Fatigue Controls

- **Clustering**: Related signals are grouped. A cluster of 10 news articles about the same competitor announcement becomes one signal with a "corroboration score."
- **De-duplication**: Same event from multiple sources is counted once.
- **Decay**: Signals that have been active for more than 30 days without escalation or new corroboration are automatically downgraded.
- **Personalisation**: Each persona's radar shows only signals relevant to their domain. The CEO sees all domains; the CFO sees financial, market, and regulatory; the COO sees operational and safety.
- **Volume caps**: No more than 10 signals per weekly radar (across all categories). If more qualify, the agent prioritises ruthlessly and footnotes the overflow.
- **Feedback loop**: If an executive consistently dismisses a category of signal, the agent adjusts the threshold for that category upward.

### 15.5 Foresight Outputs

| Output | Audience | Frequency | Content |
|--------|----------|-----------|---------|
| **Weekly Strategic Radar** | ExCo | Weekly (Monday AM) | Top 5–10 signals, classified by domain and priority. Brief assessment and "so what" for Alinta. |
| **Monthly Foresight Brief** | Board, ExCo | Monthly | Deeper analysis of thematic clusters. Trend identification. 3–6 month outlook. Strategic implications. |
| **Quarterly Strategic Scan** | Board | Quarterly (pre-Board meeting) | Comprehensive environmental scan. Year-ahead outlook. Updated competitive landscape. Technology trajectory assessment. |
| **Ad-Hoc Critical Alert** | CEO + relevant C-suite | As needed | Immediate notification of critical signal. Brief context and preliminary impact assessment. |

---

## 16. Simulation Governance and Decision Assurance

### 16.1 Simulation Model Lifecycle

**Model selection and development:**
- Simulation models are selected based on the strategic question being addressed. For NEM/WEM dispatch modelling, a production-cost model or agent-based dispatch simulator is required. For portfolio financial analysis, a Monte Carlo or scenario-tree model is appropriate. For competitive response, game-theoretic or agent-based models apply.
- Each model is documented with: purpose, scope, methodology, assumptions, calibration approach, known limitations, and validation results.
- Models are registered in the MLflow Model Registry within Unity Catalog.

**Validation and calibration:**
- All simulation models undergo backtesting against historical data before production deployment.
- Calibration metrics are defined per model (e.g., MAPE on wholesale prices, accuracy of dispatch order, correlation of portfolio P&L).
- Validation results are documented in the model card and reviewed by an independent technical reviewer (separate from the model developer).
- Re-calibration is triggered when: (a) new historical data is available, (b) market structure changes materially, or (c) backtesting accuracy falls below the defined threshold.

**Versioning:**
- Every model version is immutable and auditable.
- Production simulations record the model version used.
- Historical simulation results can be reproduced using the recorded model version and input data version.

### 16.2 Communicating Uncertainty and Sensitivity

**Principles:**
- No simulation result is presented as a single number. All results include uncertainty ranges (confidence intervals, percentile distributions, or scenario spreads).
- Sensitivity analysis is provided for every simulation: "The three parameters this result is most sensitive to are [X, Y, Z]. A 10% change in X shifts the outcome by [amount]."
- Robustness assessment: "This result is robust/fragile across the tested scenario range. Under [N]% of scenarios, the outcome remains within [range]."

**Visual conventions:**
- Fan charts or box plots for distributional results.
- Tornado diagrams for sensitivity analysis.
- Traffic-light indicators for robustness (green = robust across scenarios, amber = sensitive to key assumptions, red = fragile).

**Language conventions:**
- Simulation outputs use language calibrated to their maturity level:
  - Directional: "The model suggests that…", "Indicative analysis points to…"
  - Calibrated: "Based on calibrated modelling, the expected range is…"
  - Decision-grade: "Validated modelling indicates…", "The model projects with [X]% confidence that…"

### 16.3 Labelling of Simulation Outputs

Every simulation output carries a standardised label:

| Label | Meaning | Appropriate Use |
|-------|---------|-----------------|
| **Directional Insight** | Model is in development or not yet calibrated against historical data. Results indicate direction but not magnitude. | Internal exploration, hypothesis generation, early-stage strategy discussion. |
| **Calibrated Analysis** | Model has been backtested and calibrated. Results are quantitatively meaningful within stated assumptions. | Strategy papers, ExCo discussion, investment case development. |
| **Decision-Grade** | Model has undergone independent validation, comprehensive backtesting, and stress testing. Results are suitable for formal decision support. | Board papers, capital allocation decisions, regulatory submissions. |

Labelling is determined by the model's validation status (recorded in the model card), not by the user or the agent. The agent cannot upgrade a model's label.

### 16.4 Human Review and Approval

| Use Case | Required Reviewer | Approval Required? |
|----------|-------------------|--------------------|
| Internal exploration (ad-hoc "what if" queries) | None | No |
| Strategy team working analysis | Model owner or delegate | Review recommended |
| ExCo presentation | Head of Strategy or Head of Market Analytics | Yes |
| Board paper inclusion | CEO + model owner | Yes |
| Investment case quantification | CFO + model owner | Yes |
| Regulatory submission support | Head of Regulatory Affairs + model owner | Yes |
| Trading or hedging strategy input | Head of Trading + CRO | Yes |

### 16.5 Simulation Audit Trail

Every simulation execution produces an immutable audit record containing:
- Simulation ID and timestamp.
- Requesting user and purpose.
- Model name and version.
- Input parameter set (full).
- Data sources and versions used.
- Compute resources consumed and duration.
- Output summary metrics.
- Model maturity label at time of execution.
- Whether results were subsequently used in a formal document (if tracked).

Audit records are stored in a dedicated Delta Lake table (`governance.simulation_audit_log`) and retained for 7 years.

---

*End of Product Requirements Document.*

---

**Document history:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | April 2026 | AI-Generated (Solutions Architecture) | Initial comprehensive PRD. |

