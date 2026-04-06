import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# ── Configuration ──────────────────────────────────────────────
MARKETS = ["China", "Japan", "South Korea", "Australia", 
           "Singapore", "Hong Kong", "Thailand", "India"]

CHANNELS = ["Boutique", "E-Commerce", "Wholesale", 
            "Travel Retail", "Private Client"]

CATEGORIES = ["High Jewellery", "Watches", "Fine Jewellery", 
              "Accessories", "Fragrances"]

PRODUCTS = {
    "High Jewellery":  ["Trinity Collection", "Panthère Bracelet", 
                        "Juste un Clou Necklace", "LOVE Bracelet HJ"],
    "Watches":         ["Santos de Cartier", "Tank Must", 
                        "Ballon Bleu", "Panthère Watch", "Rotonde"],
    "Fine Jewellery":  ["Cartier d'Amour", "Clash de Cartier", 
                        "Cactus de Cartier", "Trinity Ring"],
    "Accessories":     ["C de Cartier Bag", "Panthere Sunglasses", 
                        "Cartier Wallet", "Love Bracelet Classic"],
    "Fragrances":      ["La Panthère", "Baiser Volé", 
                        "Les Heures de Parfum", "Carat"]
}

SEGMENTS = ["VIP (>$50K)", "Premium ($10K-$50K)", 
            "Aspirational ($1K-$10K)", "Entry (<$1K)"]

# ── 1. Sales Data ──────────────────────────────────────────────
def generate_sales_data():
    records = []
    start_date = datetime(2022, 1, 1)
    
    for _ in range(3600):  # 3 years of daily transactions
        date = start_date + timedelta(days=random.randint(0, 1094))
        market = random.choice(MARKETS)
        channel = random.choice(CHANNELS)
        category = random.choice(CATEGORIES)
        product = random.choice(PRODUCTS[category])
        
        # Realistic price ranges by category (USD)
        price_ranges = {
            "High Jewellery":  (45000, 850000),
            "Watches":         (4500,  85000),
            "Fine Jewellery":  (1200,  45000),
            "Accessories":     (350,   3500),
            "Fragrances":      (120,   480)
        }
        
        base_price = random.uniform(*price_ranges[category])
        
        # Market multipliers (purchasing power / brand premium)
        market_mult = {
            "China": 1.15, "Japan": 1.08, "South Korea": 1.12,
            "Australia": 0.98, "Singapore": 1.18,
            "Hong Kong": 1.22, "Thailand": 0.92, "India": 0.88
        }
        
        revenue = base_price * market_mult[market] * random.uniform(0.88, 1.12)
        units   = random.randint(1, 3) if category != "High Jewellery" else 1
        cogs    = revenue * random.uniform(0.28, 0.38)
        
        # Seasonal uplift (CNY, Christmas, Valentine's)
        month = date.month
        seasonal = 1.0
        if month in [1, 2]:   seasonal = 1.35   # CNY
        elif month == 12:     seasonal = 1.28   # Christmas
        elif month == 2:      seasonal = 1.18   # Valentine's
        elif month in [6, 7]: seasonal = 0.88   # Low season
        
        records.append({
            "date":           date.strftime("%Y-%m-%d"),
            "year":           date.year,
            "month":          date.month,
            "quarter":        f"Q{(date.month-1)//3+1}",
            "market":         market,
            "channel":        channel,
            "category":       category,
            "product":        product,
            "units_sold":     units,
            "revenue_usd":    round(revenue * seasonal * units, 2),
            "cogs_usd":       round(cogs * units, 2),
            "gross_profit":   round((revenue - cogs) * seasonal * units, 2),
            "gross_margin":   round(((revenue - cogs) / revenue) * 100, 1),
            "segment":        random.choice(SEGMENTS),
            "is_repeat_client": random.random() > 0.45,
            "nps_score":      random.randint(6, 10),
        })
    
    df = pd.DataFrame(records)
    df.to_csv("data/sales_data.csv", index=False)
    print(f"✅ Sales data: {len(df)} records")
    return df

# ── 2. CRM / Client Data ───────────────────────────────────────
def generate_crm_data():
    first_names = ["Wei", "Yuki", "Ji-ho", "Priya", "Mei-Ling",
                   "Haruto", "Soo-Jin", "Ananya", "Xiao", "Sakura",
                   "Min-jun", "Ravi", "Hui", "Kenji", "Da-eun"]
    last_names  = ["Chen", "Tanaka", "Kim", "Sharma", "Wong",
                   "Yamamoto", "Park", "Patel", "Liu", "Nakamura",
                   "Lee", "Gupta", "Zhang", "Suzuki", "Choi"]
    
    clients = []
    for i in range(500):
        market       = random.choice(MARKETS)
        segment      = random.choice(SEGMENTS)
        clv_ranges   = {
            "VIP (>$50K)":           (50000, 850000),
            "Premium ($10K-$50K)":   (10000, 50000),
            "Aspirational ($1K-$10K)":(1000, 10000),
            "Entry (<$1K)":          (200,   1000)
        }
        clv          = random.uniform(*clv_ranges[segment])
        join_date    = datetime(2019, 1, 1) + timedelta(days=random.randint(0, 1800))
        last_purchase= join_date + timedelta(days=random.randint(30, 730))
        
        clients.append({
            "client_id":       f"CRT-{market[:2].upper()}-{i+1000:04d}",
            "name":            f"{random.choice(first_names)} {random.choice(last_names)}",
            "market":          market,
            "segment":         segment,
            "preferred_channel": random.choice(CHANNELS),
            "preferred_category": random.choice(CATEGORIES),
            "lifetime_value_usd": round(clv, 2),
            "total_transactions":  random.randint(1, 24),
            "avg_order_value":     round(clv / random.randint(1, 24), 2),
            "join_date":           join_date.strftime("%Y-%m-%d"),
            "last_purchase_date":  last_purchase.strftime("%Y-%m-%d"),
            "days_since_purchase": (datetime.now() - last_purchase).days,
            "churn_risk":          random.choice(["Low", "Medium", "High"]),
            "satisfaction_score":  round(random.uniform(6.5, 10.0), 1),
            "boutique_visits_ytd": random.randint(0, 12),
            "digital_engagement":  random.choice(["High", "Medium", "Low"]),
            "owns_watch":          random.random() > 0.5,
            "owns_jewellery":      random.random() > 0.4,
            "vip_events_attended": random.randint(0, 8),
            "personal_stylist":    random.random() > 0.65,
            "notes":               generate_client_note(segment, market),
        })
    
    df = pd.DataFrame(clients)
    df.to_csv("data/crm_data.csv", index=False)
    print(f"✅ CRM data: {len(df)} clients")
    return df

def generate_client_note(segment, market):
    notes = {
        "VIP (>$50K)": [
            "Prefers private viewings for High Jewellery launches. Interested in bespoke commissions.",
            "Attends all VIP trunk shows. Has strong interest in limited edition Panthère pieces.",
            "Long-standing relationship since 2015. Anniversary purchases in June annually.",
        ],
        "Premium ($10K-$50K)": [
            "Growing client - escalated from Aspirational in 2023. Watch collector.",
            "Referred two new clients in Q1 2024. Interested in Santos family.",
            "Prefers e-commerce with in-boutique final fitting.",
        ],
        "Aspirational ($1K-$10K)": [
            "First-time buyer via digital campaign. Gifting motivation.",
            "Regular fragrance buyer upgrading to fine jewellery.",
        ],
        "Entry (<$1K)": [
            "Fragrance and accessories. Strong digital engagement.",
            "Tourist buyer - Singapore boutique.",
        ]
    }
    return random.choice(notes.get(segment, ["Regular client."]))

# ── 3. Marketing Budget Data ───────────────────────────────────
def generate_marketing_data():
    records = []
    campaigns = [
        "CNY Campaign 2024", "Love Day Collection", "High Jewellery Launch",
        "Santos Digital Push", "Panthère APAC Tour", "Holiday Season 2023",
        "Boutique Renovation Launch", "Influencer Partnership Q2",
        "VIP Client Events", "Clash Campaign APAC", "Tank Must Relaunch",
        "Sustainability Initiative"
    ]
    media_types = ["Digital", "OOH", "Print", "Events", "PR", "Influencer", "CRM"]
    
    for market in MARKETS:
        for campaign in random.sample(campaigns, k=random.randint(4, 8)):
            for media in random.sample(media_types, k=random.randint(2, 5)):
                budget       = random.uniform(50000, 2500000)
                variance_pct = random.uniform(-0.18, 0.22)
                actual       = budget * (1 + variance_pct)
                impressions  = random.randint(50000, 8000000)
                conversions  = int(impressions * random.uniform(0.001, 0.045))
                revenue_attr = conversions * random.uniform(800, 15000)
                
                records.append({
                    "campaign":          campaign,
                    "market":            market,
                    "media_type":        media,
                    "budget_usd":        round(budget, 2),
                    "actual_usd":        round(actual, 2),
                    "variance_usd":      round(actual - budget, 2),
                    "variance_pct":      round(variance_pct * 100, 1),
                    "impressions":       impressions,
                    "conversions":       conversions,
                    "revenue_attributed":round(revenue_attr, 2),
                    "roi":               round((revenue_attr - actual) / actual * 100, 1),
                    "cpm":               round(actual / impressions * 1000, 2),
                    "status":            random.choice(["Completed", "Active", "Planned"]),
                    "quarter":           random.choice(["Q1 2024","Q2 2024","Q3 2024","Q4 2023"]),
                })
    
    df = pd.DataFrame(records)
    df.to_csv("data/marketing_data.csv", index=False)
    print(f"✅ Marketing data: {len(df)} campaign records")
    return df

# ── 4. Demand & Supply Data ────────────────────────────────────
def generate_supply_data():
    records = []
    for category in CATEGORIES:
        for product in PRODUCTS[category]:
            for market in MARKETS:
                for month_offset in range(18):  # 18 months
                    date    = datetime(2023, 7, 1) + timedelta(days=30 * month_offset)
                    
                    base_demand = {
                        "High Jewellery": random.randint(2, 15),
                        "Watches":        random.randint(15, 120),
                        "Fine Jewellery": random.randint(25, 200),
                        "Accessories":    random.randint(40, 350),
                        "Fragrances":     random.randint(80, 600)
                    }[category]
                    
                    seasonal_factor = 1.0
                    if date.month in [1, 2]: seasonal_factor = 1.4
                    elif date.month == 12:   seasonal_factor = 1.3
                    elif date.month in [6, 7]: seasonal_factor = 0.85
                    
                    forecast_demand = int(base_demand * seasonal_factor)
                    actual_demand   = int(forecast_demand * random.uniform(0.80, 1.25))
                    stock_available = int(forecast_demand * random.uniform(0.75, 1.35))
                    lead_time_days  = random.randint(14, 120)
                    
                    records.append({
                        "date":              date.strftime("%Y-%m-%d"),
                        "month_year":        date.strftime("%b %Y"),
                        "category":          category,
                        "product":           product,
                        "market":            market,
                        "forecast_demand":   forecast_demand,
                        "actual_demand":     actual_demand,
                        "stock_available":   stock_available,
                        "stock_cover_weeks": round(stock_available / max(actual_demand/4, 1), 1),
                        "reorder_point":     int(base_demand * 0.3),
                        "lead_time_days":    lead_time_days,
                        "stockout_risk":     "High" if stock_available < forecast_demand * 0.5
                                             else "Medium" if stock_available < forecast_demand * 0.8
                                             else "Low",
                        "overstock_risk":    "High" if stock_available > forecast_demand * 1.4
                                             else "Medium" if stock_available > forecast_demand * 1.2
                                             else "Low",
                        "unit_cost_usd":     round(random.uniform(
                                                 200 if category == "Fragrances" else 1500,
                                                 150000 if category == "High Jewellery" else 30000
                                             ), 2),
                    })
    
    df = pd.DataFrame(records)
    df.to_csv("data/supply_data.csv", index=False)
    print(f"✅ Supply data: {len(df)} records")
    return df

# ── 5. KPI / Executive Summary Data ───────────────────────────
def generate_kpi_data():
    kpis = {
        "total_revenue_ytd_usd":     142_800_000,
        "revenue_target_ytd_usd":    135_000_000,
        "revenue_vs_target_pct":     5.8,
        "gross_margin_pct":          68.4,
        "total_clients_apac":        48_320,
        "new_clients_ytd":           6_840,
        "vip_clients":               1_240,
        "client_retention_rate":     0.847,
        "avg_transaction_value_usd": 12_450,
        "nps_score":                 72,
        "top_market":                "China",
        "top_channel":               "Boutique",
        "top_category":              "Watches",
        "marketing_roi_pct":         284,
        "inventory_health_pct":      91.2,
        "on_time_delivery_pct":      94.7,
        "digital_revenue_share_pct": 23.8,
        "travel_retail_growth_pct":  18.4,
    }
    with open("data/kpis.json", "w", encoding="utf-8") as f:
        json.dump(kpis, f, indent=2)
    print("✅ KPI data generated")
    return kpis

# ── 6. RAG Knowledge Base Documents ───────────────────────────
def generate_rag_documents():
    documents = [
        {
            "id": "DOC-001",
            "title": "Cartier APAC Sales Strategy 2024",
            "category": "Strategy",
            "content": """
Cartier APAC Sales Strategy 2024 — Executive Summary

The APAC region represents 42% of global Cartier revenue with a target of USD 580M for FY2024. 
Key growth pillars include: (1) China recovery post-COVID with renewed domestic tourism driving boutique traffic 
up 28% YoY; (2) Watches category leading with 34% revenue share, anchored by Santos de Cartier 
and Ballon Bleu families; (3) Digital channel scaling to 24% of total revenue through WeChat Mini-Programs 
in China and LINE integration in Japan/Thailand.

Channel Strategy: Boutique remains the primary channel at 52% revenue share. 
Travel Retail recovered strongly with Changi (Singapore), Incheon (Korea) and HKG as top-performing 
duty-free locations. Private Client channel shows highest gross margin at 74.2%.

Market Priorities: China (Tier-1 focus), Japan (steady-state), South Korea (emerging VIP growth), 
Singapore (hub for Southeast Asia), Australia (entry luxury segment acceleration).

CRM Objective: Increase repeat client rate from 54% to 65% by Q4 2024 through personalised 
outreach, VIP events, and a redesigned loyalty experience framework.
            """.strip()
        },
        {
            "id": "DOC-002",
            "title": "High Jewellery Launch Protocol - APAC",
            "category": "Operations",
            "content": """
High Jewellery Collections — APAC Launch & Client Engagement Protocol

Pre-Launch (T-90 days): Personal stylist briefings across all boutiques. VIP client list curated by 
Market Directors — minimum CLV threshold USD 150,000 for private preview invitations.

Private Viewing Events: Held in flagship boutiques (Shanghai IFC, Tokyo Ginza, Seoul Lotte, 
Sydney MLC, Singapore ION). Format: intimate gatherings of 8-12 clients maximum. 
Champagne service, bespoke presentation by certified Gemologist. No hard selling — 
relationship deepening objective.

Digital Amplification: Post-event content shared via private WhatsApp/WeChat with attending 
clients (consent required). No public social posts for 48 hours after private viewing.

Pricing Authority: High Jewellery pricing set at HQ level. Market Directors may apply 
maximum 3% service adjustment for bespoke modifications. No discounting permitted.

Post-Launch KPIs: Conversion rate target >35% of private viewing attendees. 
Average order value >USD 85,000. Client satisfaction score >9.2/10.
            """.strip()
        },
        {
            "id": "DOC-003",
            "title": "Client Segmentation & CRM Guidelines",
            "category": "CRM",
            "content": """
Cartier APAC Client Segmentation Framework

Tier 1 — Maison VIP (CLV > USD 50,000):
- Dedicated Personal Stylist assigned
- Priority access to all new collections pre-launch
- Annual bespoke gifting budget: USD 2,500 per client
- Invitation to global Cartier events (Watches & Wonders, HJ Launch Paris)
- Target contact frequency: minimum monthly touchpoint

Tier 2 — Premium (CLV USD 10,000–50,000):
- Shared stylist model (1 stylist per 15 clients)
- New season preview invitations (boutique events)
- Digital-first engagement with boutique anchor moments
- Target contact frequency: bi-monthly

Tier 3 — Aspirational (CLV USD 1,000–10,000):
- Digital-led CRM (email, WeChat, LINE, KakaoTalk)
- Targeted product recommendations based on purchase history
- Upgrade pathway strategy: 18-month conversion target to Tier 2

Tier 4 — Entry (<USD 1,000):
- Fragrance and accessories entry point
- Digital acquisition and nurture campaigns
- Brand education content prioritised

Churn Prevention: Clients with >180 days since last purchase flagged for re-engagement. 
Personalised outreach initiated by assigned stylist within 5 business days of flag.

Data Privacy: All client data processed under PDPA (Singapore), PIPL (China), 
APPI (Japan), PIPA (Korea). Consent audit conducted quarterly.
            """.strip()
        },
        {
            "id": "DOC-004",
            "title": "Supply Chain & Inventory Policy APAC",
            "category": "Supply Chain",
            "content": """
APAC Supply Chain Management — Inventory & Distribution Policy

Central Hub: Singapore Distribution Centre (SDC) serves as regional hub for Southeast Asia and Australia.
North Asia (China, HK, Taiwan, Korea, Japan) supplied directly from European Manufacturing via 
dedicated air freight lanes.

Stock Cover Targets by Category:
- High Jewellery: 8-12 weeks cover (bespoke lead time 16-24 weeks)
- Watches: 10-14 weeks cover (high velocity items 6-8 weeks)
- Fine Jewellery: 8-10 weeks cover
- Accessories: 6-8 weeks cover
- Fragrances: 4-6 weeks cover (regional co-manufacturing in Singapore)

Reorder Triggers: Automated alert when stock cover falls below minimum threshold. 
Market Directors notified within 24 hours. Emergency replenishment available for VIP client orders.

Seasonal Planning: CNY + 60 days pre-build. Christmas + 90 days pre-build. 
Valentine's Day demand spike managed through boutique allocation (not open stock).

Stockout Protocol: Client waitlist managed by boutique. Personal notification when stock arrives. 
Maximum waitlist commitment: 45 days. Beyond 45 days — bespoke order process initiated.

KPI Targets: On-time delivery >95%. Inventory accuracy >99.5%. Stockout rate <2% of SKUs.
            """.strip()
        },
        {
            "id": "DOC-005",
            "title": "Digital & E-Commerce Strategy APAC 2024",
            "category": "Digital",
            "content": """
Digital Commerce & Omnichannel Strategy — Cartier APAC 2024

Platform Architecture: 
China: WeChat Mini-Program (primary), Tmall Luxury Pavilion (secondary), JD Luxury.
Japan: cartier.com/ja (rebuilt 2023), LINE integration for CRM communications.
Korea: cartier.com/ko, KakaoTalk Channel for client messaging.
Southeast Asia & Australia: cartier.com (global), WhatsApp Business for VIP clients.

Revenue Targets by Digital Channel:
- China Digital (WeChat + Tmall): USD 28M target (+22% YoY)
- Japan Digital: USD 8.4M (+15% YoY)
- Korea Digital: USD 6.2M (+19% YoY)
- SEA + Australia Digital: USD 4.8M (+31% YoY)

Client Journey Principles: Digital is discovery and inspiration — conversion anchored in boutique 
or private client experience. Click-and-collect available in all flagship boutiques.
Virtual try-on pilot (AR) launching Q3 2024 in China and Korea.

Content Strategy: 60% heritage storytelling, 25% product-led, 15% client lifestyle.
Influencer: Selective tier-1 partnerships only (>5M authentic followers, verified luxury alignment).
No mass UGC campaigns — brand consistency paramount.

Data & Analytics: CDP (Customer Data Platform) implementation underway (go-live Q4 2024).
Unifying online + offline client touchpoints across all APAC markets.
            """.strip()
        },
        {
            "id": "DOC-006",
            "title": "GenAI Implementation Roadmap — Internal",
            "category": "Technology",
            "content": """
Cartier APAC — Internal GenAI Implementation Roadmap (Confidential)

Phase 1 (Current — Q2 2024): Foundation
- RAG-powered internal knowledge assistant for boutique staff
- Sales performance analytics with AI-generated commentary
- Client churn prediction model (pilot: Singapore, Australia)

Phase 2 (Q3–Q4 2024): Scale
- Personalised client communication drafting (stylist co-pilot)
- Demand forecasting ML model APAC-wide deployment
- Marketing campaign ROI attribution model

Phase 3 (2025): Enterprise AI
- Real-time inventory optimisation engine
- Omnichannel client journey orchestration
- Predictive VIP client upgrade pathways
- Automated compliance and data governance monitoring

Governance Principles:
1. Human-in-the-loop for all client-facing AI outputs
2. Data never shared with external LLM providers without anonymisation
3. All AI outputs auditable and explainable
4. Guardrails in place for brand-safe communications
5. Quarterly AI ethics review by APAC leadership team

Model Selection: OpenAI GPT-4 for language tasks (Azure private endpoint).
Custom fine-tuned models for product recommendation (in roadmap).
Vector database: Azure AI Search with semantic ranking.
MLOps: Azure ML with custom monitoring dashboards.
            """.strip()
        },
    ]
    
    with open("data/rag_documents.json", "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)
    print(f"✅ RAG knowledge base: {len(documents)} documents")
    return documents

# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    print("\n🔴 Generating Cartier APAC synthetic data...\n")
    generate_sales_data()
    generate_crm_data()
    generate_marketing_data()
    generate_supply_data()
    generate_kpi_data()
    generate_rag_documents()
    print("\n✅ All datasets generated successfully.\n")