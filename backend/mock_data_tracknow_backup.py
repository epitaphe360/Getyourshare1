# Mock data for Tracknow.io clone
from datetime import datetime, timedelta
import random

# Mock Users
MOCK_USERS = [
    {
        "id": "user_1",
        "email": "admin@tracknow.io",
        "password": "admin123",  # In real app, this would be hashed
        "role": "manager",
        "first_name": "Admin",
        "last_name": "Manager",
        "phone": "+33612345678",
        "country": "FR",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Admin",
        "created_at": "2024-01-01T00:00:00Z",
    },
    {
        "id": "user_2",
        "email": "advertiser@example.com",
        "password": "adv123",
        "role": "advertiser",
        "first_name": "John",
        "last_name": "Advertiser",
        "phone": "+33698765432",
        "country": "FR",
        "company_name": "TechCorp",
        "created_at": "2024-01-15T00:00:00Z",
    },
    {
        "id": "user_3",
        "email": "affiliate@example.com",
        "password": "aff123",
        "role": "affiliate",
        "first_name": "Marie",
        "last_name": "Affiliate",
        "phone": "+33687654321",
        "country": "FR",
        "created_at": "2024-02-01T00:00:00Z",
    },
]

# Mock Advertisers
MOCK_ADVERTISERS = [
    {
        "id": "adv_1",
        "company_name": "TechCorp",
        "email": "contact@techcorp.com",
        "status": "approved",
        "country": "FR",
        "website": "https://techcorp.com",
        "phone": "+33123456789",
        "address": "123 Tech Street, Paris",
        "tax_id": "FR12345678901",
        "balance": 15000.00,
        "total_spent": 45000.00,
        "campaigns_count": 5,
        "created_at": "2024-01-15T10:30:00Z",
    },
    {
        "id": "adv_2",
        "company_name": "Fashion Boutique",
        "email": "hello@fashionboutique.com",
        "status": "pending",
        "country": "FR",
        "website": "https://fashionboutique.com",
        "phone": "+33198765432",
        "address": "456 Mode Avenue, Lyon",
        "tax_id": "FR98765432109",
        "balance": 0.00,
        "total_spent": 0.00,
        "campaigns_count": 0,
        "created_at": "2024-03-10T14:20:00Z",
    },
    {
        "id": "adv_3",
        "company_name": "Sports Gear",
        "email": "info@sportsgear.com",
        "status": "approved",
        "country": "US",
        "website": "https://sportsgear.com",
        "phone": "+1234567890",
        "address": "789 Sport Blvd, New York",
        "tax_id": "US12345678",
        "balance": 25000.00,
        "total_spent": 78000.00,
        "campaigns_count": 8,
        "created_at": "2023-11-20T09:15:00Z",
    },
]

# Mock Campaigns
MOCK_CAMPAIGNS = [
    {
        "id": "camp_1",
        "name": "Summer Sale 2024",
        "advertiser_id": "adv_1",
        "advertiser_name": "TechCorp",
        "status": "active",
        "commission_type": "percentage",
        "commission_value": 15.0,
        "category": "Technology",
        "description": "Promote our summer tech deals",
        "start_date": "2024-06-01T00:00:00Z",
        "end_date": "2024-08-31T23:59:59Z",
        "clicks": 15420,
        "conversions": 342,
        "revenue": 45600.00,
        "created_at": "2024-05-15T10:00:00Z",
    },
    {
        "id": "camp_2",
        "name": "Spring Fashion Collection",
        "advertiser_id": "adv_3",
        "advertiser_name": "Sports Gear",
        "status": "active",
        "commission_type": "fixed",
        "commission_value": 10.0,
        "category": "Fashion",
        "description": "New spring collection launch",
        "start_date": "2024-03-01T00:00:00Z",
        "end_date": "2024-05-31T23:59:59Z",
        "clicks": 8950,
        "conversions": 189,
        "revenue": 28900.00,
        "created_at": "2024-02-10T14:30:00Z",
    },
    {
        "id": "camp_3",
        "name": "Black Friday Deals",
        "advertiser_id": "adv_1",
        "advertiser_name": "TechCorp",
        "status": "paused",
        "commission_type": "percentage",
        "commission_value": 20.0,
        "category": "Technology",
        "description": "Biggest deals of the year",
        "start_date": "2023-11-24T00:00:00Z",
        "end_date": "2023-11-27T23:59:59Z",
        "clicks": 45230,
        "conversions": 1250,
        "revenue": 189000.00,
        "created_at": "2023-11-01T09:00:00Z",
    },
]

# Mock Affiliates
MOCK_AFFILIATES = [
    {
        "id": "aff_1",
        "first_name": "Marie",
        "last_name": "Dupont",
        "email": "marie.dupont@example.com",
        "status": "approved",
        "country": "FR",
        "phone": "+33687654321",
        "website": "https://marietech.blog",
        "traffic_source": "Blog",
        "balance": 2450.00,
        "total_earned": 12300.00,
        "clicks": 5670,
        "conversions": 89,
        "created_at": "2024-01-10T11:20:00Z",
    },
    {
        "id": "aff_2",
        "first_name": "Pierre",
        "last_name": "Martin",
        "email": "pierre.martin@example.com",
        "status": "approved",
        "country": "FR",
        "phone": "+33612345098",
        "website": "https://techdeals.fr",
        "traffic_source": "Website",
        "balance": 5670.00,
        "total_earned": 34500.00,
        "clicks": 12450,
        "conversions": 234,
        "created_at": "2023-09-15T09:30:00Z",
    },
    {
        "id": "aff_3",
        "first_name": "Sophie",
        "last_name": "Laurent",
        "email": "sophie.laurent@example.com",
        "status": "pending",
        "country": "FR",
        "phone": "+33698712345",
        "website": "https://sophiestyle.com",
        "traffic_source": "Instagram",
        "balance": 0.00,
        "total_earned": 0.00,
        "clicks": 0,
        "conversions": 0,
        "created_at": "2024-03-20T16:45:00Z",
    },
    {
        "id": "aff_4",
        "first_name": "Lucas",
        "last_name": "Bernard",
        "email": "lucas.bernard@example.com",
        "status": "approved",
        "country": "FR",
        "phone": "+33645123789",
        "website": "https://dealsandmore.fr",
        "traffic_source": "Facebook",
        "balance": 890.00,
        "total_earned": 5600.00,
        "clicks": 3200,
        "conversions": 45,
        "created_at": "2023-12-05T10:15:00Z",
    },
]

# Mock Conversions
MOCK_CONVERSIONS = []
for i in range(50):
    date = datetime.now() - timedelta(days=random.randint(0, 30))
    MOCK_CONVERSIONS.append(
        {
            "id": f"conv_{i+1}",
            "campaign_id": random.choice(["camp_1", "camp_2", "camp_3"]),
            "affiliate_id": random.choice(["aff_1", "aff_2", "aff_4"]),
            "order_id": f"ORD{1000+i}",
            "amount": round(random.uniform(50, 500), 2),
            "commission": round(random.uniform(5, 75), 2),
            "status": random.choice(["approved", "pending", "rejected"]),
            "created_at": date.isoformat(),
        }
    )

# Mock Clicks
MOCK_CLICKS = []
for i in range(100):
    date = datetime.now() - timedelta(days=random.randint(0, 7))
    MOCK_CLICKS.append(
        {
            "id": f"click_{i+1}",
            "campaign_id": random.choice(["camp_1", "camp_2", "camp_3"]),
            "affiliate_id": random.choice(["aff_1", "aff_2", "aff_4"]),
            "ip": f"192.168.{random.randint(0,255)}.{random.randint(0,255)}",
            "country": random.choice(["FR", "US", "GB", "DE"]),
            "device": random.choice(["Desktop", "Mobile", "Tablet"]),
            "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
            "created_at": date.isoformat(),
        }
    )

# Mock Payouts
MOCK_PAYOUTS = [
    {
        "id": "pay_1",
        "affiliate_id": "aff_1",
        "affiliate_name": "Marie Dupont",
        "amount": 1200.00,
        "method": "Bank Transfer",
        "status": "approved",
        "requested_at": "2024-03-01T10:00:00Z",
        "processed_at": "2024-03-03T14:30:00Z",
    },
    {
        "id": "pay_2",
        "affiliate_id": "aff_2",
        "affiliate_name": "Pierre Martin",
        "amount": 2500.00,
        "method": "PayPal",
        "status": "pending",
        "requested_at": "2024-03-15T09:20:00Z",
        "processed_at": None,
    },
    {
        "id": "pay_3",
        "affiliate_id": "aff_4",
        "affiliate_name": "Lucas Bernard",
        "amount": 450.00,
        "method": "Bank Transfer",
        "status": "approved",
        "requested_at": "2024-02-28T16:45:00Z",
        "processed_at": "2024-03-01T11:20:00Z",
    },
]

# Mock Coupons
MOCK_COUPONS = [
    {
        "id": "coup_1",
        "code": "SUMMER2024",
        "campaign_id": "camp_1",
        "discount_type": "percentage",
        "discount_value": 20,
        "usage_count": 145,
        "usage_limit": 500,
        "status": "active",
        "expires_at": "2024-08-31T23:59:59Z",
    },
    {
        "id": "coup_2",
        "code": "WELCOME10",
        "campaign_id": "camp_2",
        "discount_type": "fixed",
        "discount_value": 10,
        "usage_count": 89,
        "usage_limit": 1000,
        "status": "active",
        "expires_at": "2024-12-31T23:59:59Z",
    },
]

# Mock Dashboard Stats
MOCK_DASHBOARD_STATS = {
    "total_clicks": 45670,
    "total_conversions": 1245,
    "total_revenue": 189500.00,
    "total_commission": 28425.00,
    "active_campaigns": 12,
    "active_affiliates": 156,
    "pending_payouts": 5,
    "conversion_rate": 2.73,
    "average_order_value": 152.21,
}

# Mock Settings
MOCK_SETTINGS = {
    "company": {
        "name": "Tracknow Platform",
        "email": "contact@tracknow.io",
        "address": "123 Business Street, Paris, France",
        "tax_id": "FR12345678901",
        "currency": "EUR",
        "currency_symbol": "€",
        "timezone": "Europe/Paris",
    },
    "affiliate": {
        "min_withdrawal": 50.00,
        "auto_approval": False,
        "email_verification_required": True,
        "payment_mode": "on_demand",
    },
    "mlm": {
        "enabled": True,
        "levels": [
            {"level": 1, "percentage": 10},
            {"level": 2, "percentage": 5},
            {"level": 3, "percentage": 2.5},
        ],
    },
}
