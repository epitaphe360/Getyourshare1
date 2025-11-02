"""
ENDPOINTS COMPLETS - À ajouter à server_complete.py
Tous les endpoints manquants pour tous les dashboards
"""

# LISTE DES ENDPOINTS À AJOUTER:

ENDPOINTS_MANQUANTS = """

# ============================================
# ANALYTICS ENDPOINTS
# ============================================
@app.get("/api/analytics/overview")
@app.get("/api/analytics/admin/revenue-chart")
@app.get("/api/analytics/admin/categories")
@app.get("/api/analytics/admin/platform-metrics")
@app.get("/api/analytics/merchant/sales-chart")
@app.get("/api/analytics/merchant/performance")
@app.get("/api/analytics/influencer/earnings-chart")

# ============================================
# MERCHANTS ENDPOINTS
# ============================================
@app.get("/api/merchants")
@app.get("/api/merchant/profile")
@app.get("/api/merchant/payment-config")
@app.put("/api/merchant/payment-config")
@app.get("/api/merchant/invoices")
@app.get("/api/merchant/affiliation-requests/stats")

# ============================================
# INFLUENCERS ENDPOINTS
# ============================================
@app.get("/api/influencers")
@app.get("/api/influencers/stats")
@app.get("/api/influencers/search")
@app.get("/api/influencers/directory")
@app.get("/api/influencer/profile")
@app.get("/api/influencer/tracking-links")
@app.get("/api/influencer/affiliation-requests")
@app.get("/api/influencer/payment-status")
@app.put("/api/influencer/payment-method")

# ============================================
# PRODUCTS ENDPOINTS
# ============================================
@app.get("/api/products")
@app.post("/api/products")
@app.get("/api/products/my-products")

# ============================================
# MARKETPLACE ENDPOINTS
# ============================================
@app.get("/api/marketplace/products")
@app.get("/api/marketplace/categories")
@app.get("/api/marketplace/featured")
@app.get("/api/marketplace/deals-of-day")

# ============================================
# COMMERCIALS ENDPOINTS
# ============================================
@app.get("/api/commercials/directory")

# ============================================
# AFFILIATION ENDPOINTS
# ============================================
@app.get("/api/affiliate/my-links")
@app.get("/api/affiliate/publications")
@app.get("/api/affiliates")
@app.post("/api/affiliation/request")
@app.post("/api/affiliation-requests/request")
@app.get("/api/affiliation-requests/merchant/pending")

# ============================================
# COMPANY & TEAM ENDPOINTS
# ============================================
@app.get("/api/company/links/my-company-links")
@app.post("/api/company/links/generate")
@app.post("/api/company/links/assign")
@app.delete("/api/company/links/{linkId}")
@app.get("/api/team/members")
@app.get("/api/team/stats")
@app.post("/api/team/invite")

# ============================================
# SUBSCRIPTIONS ENDPOINTS
# ============================================
@app.get("/api/subscriptions/plans")
@app.get("/api/subscriptions/my-subscription")
@app.get("/api/subscriptions/usage")
@app.post("/api/subscriptions/cancel")
@app.get("/api/subscription-plans")

# ============================================
# PAYMENTS & PAYOUTS ENDPOINTS
# ============================================
@app.post("/api/payouts/request")
@app.get("/api/payouts")
@app.get("/api/payments")
@app.post("/api/payments")
@app.get("/api/mobile-payments-ma/providers")
@app.post("/api/mobile-payments-ma/payout")

# ============================================
# MESSAGES ENDPOINTS
# ============================================
@app.get("/api/messages/conversations")
@app.post("/api/messages/send")

# ============================================
# SOCIAL MEDIA ENDPOINTS
# ============================================
@app.get("/api/social-media/connections")
@app.get("/api/social-media/dashboard")
@app.get("/api/social-media/stats/history")
@app.get("/api/social-media/posts/top")
@app.post("/api/social-media/sync")
@app.post("/api/social-media/connect/instagram")
@app.post("/api/social-media/connect/tiktok")
@app.post("/api/social-media/connect/facebook")

# ============================================
# ADMIN SOCIAL ENDPOINTS
# ============================================
@app.get("/api/admin/social/posts")
@app.get("/api/admin/social/templates")
@app.get("/api/admin/social/analytics")
@app.post("/api/admin/social/posts")
@app.delete("/api/admin/social/posts/{postId}")

# ============================================
# ADMIN INVOICES ENDPOINTS
# ============================================
@app.post("/api/admin/invoices/generate")
@app.post("/api/admin/invoices/send-reminders")

# ============================================
# ADMIN GATEWAYS ENDPOINTS
# ============================================
@app.get("/api/admin/gateways/stats")
@app.get("/api/admin/transactions")

# ============================================
# TIKTOK SHOP ENDPOINTS
# ============================================
@app.get("/api/tiktok-shop/analytics")
@app.post("/api/tiktok-shop/sync-product")

# ============================================
# CONTENT STUDIO ENDPOINTS
# ============================================
@app.get("/api/content-studio/templates")
@app.post("/api/content-studio/generate-image")

# ============================================
# SALES & COMMISSIONS ENDPOINTS
# ============================================
@app.get("/api/sales")
@app.get("/api/sales/stats")
@app.post("/api/sales")
@app.get("/api/commissions")
@app.post("/api/commissions")

# ============================================
# PERFORMANCE ENDPOINTS
# ============================================
@app.get("/api/clicks")
@app.get("/api/leads")
@app.get("/api/conversions")

# ============================================
# COUPONS & ADVERTISERS ENDPOINTS
# ============================================
@app.get("/api/coupons")
@app.get("/api/advertisers")

# ============================================
# DASHBOARD STATS ENDPOINT
# ============================================
@app.get("/api/dashboard/stats")

# ============================================
# SETTINGS ENDPOINTS
# ============================================
@app.get("/api/settings")
@app.put("/api/settings/company")
@app.post("/api/settings/affiliate")
@app.post("/api/settings/mlm")
@app.post("/api/settings/permissions")
@app.post("/api/settings/registration")
@app.post("/api/settings/smtp")
@app.post("/api/settings/smtp/test")
@app.post("/api/settings/whitelabel")

# ============================================
# BOT ENDPOINTS
# ============================================
@app.get("/api/bot/suggestions")
@app.get("/api/bot/conversations")
@app.post("/api/bot/chat")

# ============================================
# CONTACT ENDPOINT
# ============================================
@app.post("/api/contact/submit")

"""

print(ENDPOINTS_MANQUANTS)
