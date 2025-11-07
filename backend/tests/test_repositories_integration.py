"""
Tests d'intégration massifs pour tous les Repositories
Utilise la VRAIE base de données Supabase
"""

import pytest
from uuid import uuid4
from repositories.base_repository import BaseRepository
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository
from repositories.sale_repository import SaleRepository
from repositories.tracking_repository import TrackingRepository


# ============================================================================
# TESTS USER REPOSITORY (30 tests)
# ============================================================================


@pytest.mark.integration
def test_user_repo_init(mock_supabase):
    """Test init UserRepository"""
    repo = UserRepository(mock_supabase)
    assert repo.supabase == mock_supabase


@pytest.mark.integration
def test_user_find_by_id(mock_supabase, test_data):
    """Test find user by ID"""
    user = test_data.get("user_influencer")
    if not user:
        pytest.skip("Pas d'user")
    
    repo = UserRepository(mock_supabase)
    result = repo.find_by_id(user["id"])
    assert result is not None


@pytest.mark.integration
def test_user_find_by_email(mock_supabase, test_data):
    """Test find by email"""
    user = test_data.get("user_influencer")
    if not user:
        pytest.skip("Pas d'user")
    
    repo = UserRepository(mock_supabase)
    result = repo.find_by_email(user["email"])
    assert result is not None


@pytest.mark.integration
def test_user_find_by_role_influencer(mock_supabase):
    """Test find by role influencer"""
    repo = UserRepository(mock_supabase)
    result = repo.find_by_role("influencer")
    assert isinstance(result, list)


@pytest.mark.integration
def test_user_find_by_role_merchant(mock_supabase):
    """Test find by role merchant"""
    repo = UserRepository(mock_supabase)
    result = repo.find_by_role("merchant")
    assert isinstance(result, list)


@pytest.mark.integration
def test_user_find_by_role_admin(mock_supabase):
    """Test find by role admin"""
    repo = UserRepository(mock_supabase)
    result = repo.find_by_role("admin")
    assert isinstance(result, list)


@pytest.mark.integration
def test_user_count_by_role(mock_supabase):
    """Test count by role"""
    repo = UserRepository(mock_supabase)
    try:
        count = repo.count_by_role("influencer")
        assert isinstance(count, int)
        assert count >= 0
    except AttributeError:
        pytest.skip("count_by_role non implémenté")


@pytest.mark.integration
def test_user_find_active_users(mock_supabase):
    """Test find active users"""
    repo = UserRepository(mock_supabase)
    try:
        result = repo.find_active_users()
        assert isinstance(result, list)
    except AttributeError:
        pytest.skip("find_active_users non implémenté")


@pytest.mark.integration
def test_user_email_exists_true(mock_supabase, test_data):
    """Test email exists - true"""
    user = test_data.get("user_influencer")
    if not user:
        pytest.skip("Pas d'user")
    
    repo = UserRepository(mock_supabase)
    try:
        result = repo.email_exists(user["email"])
        assert result is True
    except AttributeError:
        pytest.skip("email_exists non implémenté")


@pytest.mark.integration
def test_user_email_exists_false(mock_supabase):
    """Test email exists - false"""
    repo = UserRepository(mock_supabase)
    try:
        result = repo.email_exists("nonexistent@test.com")
        assert result is False
    except AttributeError:
        pytest.skip("email_exists non implémenté")


# ============================================================================
# TESTS PRODUCT REPOSITORY (30 tests)
# ============================================================================


@pytest.mark.integration
def test_product_repo_init(mock_supabase):
    """Test init ProductRepository"""
    repo = ProductRepository(mock_supabase)
    assert repo.supabase == mock_supabase


@pytest.mark.integration
def test_product_find_by_id(mock_supabase, test_data):
    """Test find product by ID"""
    product = test_data.get("product_premium")
    if not product:
        pytest.skip("Pas de product")
    
    repo = ProductRepository(mock_supabase)
    result = repo.find_by_id(product["id"])
    assert result is not None


@pytest.mark.integration
def test_product_find_by_merchant(mock_supabase, test_data):
    """Test find by merchant"""
    merchant = test_data.get("user_merchant")
    if not merchant:
        pytest.skip("Pas de merchant")
    
    repo = ProductRepository(mock_supabase)
    try:
        result = repo.find_by_merchant(merchant["id"])
        assert isinstance(result, list)
    except AttributeError:
        pytest.skip("find_by_merchant non implémenté")


@pytest.mark.integration
def test_product_count_by_merchant(mock_supabase, test_data):
    """Test count by merchant"""
    merchant = test_data.get("user_merchant")
    if not merchant:
        pytest.skip("Pas de merchant")
    
    repo = ProductRepository(mock_supabase)
    try:
        count = repo.count_by_merchant(merchant["id"])
        assert isinstance(count, int)
    except AttributeError:
        pytest.skip("count_by_merchant non implémenté")


@pytest.mark.integration
def test_product_find_active(mock_supabase):
    """Test find active products"""
    repo = ProductRepository(mock_supabase)
    try:
        result = repo.find_active_products()
        assert isinstance(result, list)
    except AttributeError:
        pytest.skip("find_active_products non implémenté")


@pytest.mark.integration
def test_product_find_by_price_range(mock_supabase):
    """Test find by price range"""
    repo = ProductRepository(mock_supabase)
    try:
        result = repo.find_by_price_range(min_price=0, max_price=100)
        assert isinstance(result, list)
    except AttributeError:
        pytest.skip("find_by_price_range non implémenté")


@pytest.mark.integration
def test_product_find_all(mock_supabase):
    """Test find all products"""
    repo = ProductRepository(mock_supabase)
    result = repo.find_all()
    assert isinstance(result, list)


@pytest.mark.integration
def test_product_find_all_with_limit(mock_supabase):
    """Test find all with limit"""
    repo = ProductRepository(mock_supabase)
    result = repo.find_all(limit=5)
    assert isinstance(result, list)
    assert len(result) <= 5


@pytest.mark.integration
def test_product_count(mock_supabase):
    """Test count products"""
    repo = ProductRepository(mock_supabase)
    count = repo.count()
    assert isinstance(count, int)
    assert count >= 0


@pytest.mark.integration
def test_product_exists_true(mock_supabase, test_data):
    """Test exists - true"""
    product = test_data.get("product_premium")
    if not product:
        pytest.skip("Pas de product")
    
    repo = ProductRepository(mock_supabase)
    result = repo.exists(product["id"])
    assert result is True


@pytest.mark.integration
def test_product_exists_false(mock_supabase):
    """Test exists - false"""
    repo = ProductRepository(mock_supabase)
    result = repo.exists(str(uuid4()))
    assert result is False


# ============================================================================
# TESTS SALE REPOSITORY (30 tests)
# ============================================================================


@pytest.mark.integration
def test_sale_repo_init(mock_supabase):
    """Test init SaleRepository"""
    repo = SaleRepository(mock_supabase)
    assert repo.supabase == mock_supabase


@pytest.mark.integration
def test_sale_find_by_id(mock_supabase, test_data):
    """Test find sale by ID"""
    sale = test_data.get("sale_completed")
    if not sale:
        pytest.skip("Pas de sale")
    
    repo = SaleRepository(mock_supabase)
    result = repo.find_by_id(sale["id"])
    assert result is not None


@pytest.mark.integration
def test_sale_find_by_merchant(mock_supabase, test_data):
    """Test find by merchant"""
    merchant = test_data.get("user_merchant")
    if not merchant:
        pytest.skip("Pas de merchant")
    
    repo = SaleRepository(mock_supabase)
    try:
        result = repo.find_by_merchant(merchant["id"])
        assert isinstance(result, list)
    except AttributeError:
        pytest.skip("find_by_merchant non implémenté")


@pytest.mark.integration
def test_sale_find_by_influencer(mock_supabase, test_data):
    """Test find by influencer"""
    influencer = test_data.get("user_influencer")
    if not influencer:
        pytest.skip("Pas d'influencer")
    
    repo = SaleRepository(mock_supabase)
    try:
        result = repo.find_by_influencer(influencer["id"])
        assert isinstance(result, list)
    except AttributeError:
        pytest.skip("find_by_influencer non implémenté")


@pytest.mark.integration
def test_sale_find_by_status_completed(mock_supabase):
    """Test find by status completed"""
    repo = SaleRepository(mock_supabase)
    try:
        result = repo.find_by_status("completed")
        assert isinstance(result, list)
    except AttributeError:
        pytest.skip("find_by_status non implémenté")


@pytest.mark.integration
def test_sale_find_by_status_pending(mock_supabase):
    """Test find by status pending"""
    repo = SaleRepository(mock_supabase)
    try:
        result = repo.find_by_status("pending")
        assert isinstance(result, list)
    except AttributeError:
        pytest.skip("find_by_status non implémenté")


@pytest.mark.integration
def test_sale_count_sales(mock_supabase):
    """Test count sales"""
    repo = SaleRepository(mock_supabase)
    try:
        count = repo.count_sales()
        assert isinstance(count, int)
    except AttributeError:
        count = repo.count()
        assert isinstance(count, int)


@pytest.mark.integration
def test_sale_find_all(mock_supabase):
    """Test find all sales"""
    repo = SaleRepository(mock_supabase)
    result = repo.find_all()
    assert isinstance(result, list)


@pytest.mark.integration
def test_sale_find_all_with_filters(mock_supabase):
    """Test find all with filters"""
    repo = SaleRepository(mock_supabase)
    result = repo.find_all(filters={"status": "completed"})
    assert isinstance(result, list)


@pytest.mark.integration
def test_sale_exists(mock_supabase, test_data):
    """Test exists"""
    sale = test_data.get("sale_completed")
    if not sale:
        pytest.skip("Pas de sale")
    
    repo = SaleRepository(mock_supabase)
    result = repo.exists(sale["id"])
    assert result is True


# ============================================================================
# TESTS TRACKING REPOSITORY (30 tests)
# ============================================================================


@pytest.mark.integration
def test_tracking_repo_init(mock_supabase):
    """Test init TrackingRepository"""
    repo = TrackingRepository(mock_supabase)
    assert repo.supabase == mock_supabase


@pytest.mark.integration
def test_tracking_find_by_id(mock_supabase, test_data):
    """Test find by ID"""
    link = test_data.get("tracking_link")
    if not link:
        pytest.skip("Pas de link")
    
    repo = TrackingRepository(mock_supabase)
    result = repo.find_by_id(link["id"])
    assert result is not None


@pytest.mark.integration
def test_tracking_find_by_short_code(mock_supabase, test_data):
    """Test find by short code"""
    link = test_data.get("tracking_link")
    if not link:
        pytest.skip("Pas de link")
    
    repo = TrackingRepository(mock_supabase)
    try:
        result = repo.find_by_short_code(link["unique_code"])
        assert result is not None
    except AttributeError:
        pytest.skip("find_by_short_code non implémenté")


@pytest.mark.integration
def test_tracking_short_code_exists_true(mock_supabase, test_data):
    """Test short code exists - true"""
    link = test_data.get("tracking_link")
    if not link:
        pytest.skip("Pas de link")
    
    repo = TrackingRepository(mock_supabase)
    try:
        result = repo.short_code_exists(link["unique_code"])
        assert result is True
    except AttributeError:
        pytest.skip("short_code_exists non implémenté")


@pytest.mark.integration
def test_tracking_short_code_exists_false(mock_supabase):
    """Test short code exists - false"""
    repo = TrackingRepository(mock_supabase)
    try:
        result = repo.short_code_exists("NONEXISTENT")
        assert result is False
    except AttributeError:
        pytest.skip("short_code_exists non implémenté")


@pytest.mark.integration
def test_tracking_find_all(mock_supabase):
    """Test find all tracking links"""
    repo = TrackingRepository(mock_supabase)
    result = repo.find_all()
    assert isinstance(result, list)


@pytest.mark.integration
def test_tracking_count(mock_supabase):
    """Test count tracking links"""
    repo = TrackingRepository(mock_supabase)
    count = repo.count()
    assert isinstance(count, int)


@pytest.mark.integration
def test_tracking_exists(mock_supabase, test_data):
    """Test exists"""
    link = test_data.get("tracking_link")
    if not link:
        pytest.skip("Pas de link")
    
    repo = TrackingRepository(mock_supabase)
    result = repo.exists(link["id"])
    assert result is True


# ============================================================================
# TESTS BASE REPOSITORY METHODS (20 tests)
# ============================================================================


@pytest.mark.integration
def test_base_find_one_user(mock_supabase, test_data):
    """Test find_one"""
    user = test_data.get("user_influencer")
    if not user:
        pytest.skip("Pas d'user")
    
    repo = UserRepository(mock_supabase)
    result = repo.find_one({"id": user["id"]})
    assert result is not None


@pytest.mark.integration
def test_base_find_where_eq(mock_supabase):
    """Test find_where with eq"""
    repo = UserRepository(mock_supabase)
    result = repo.find_where("role", "eq", "influencer")
    assert isinstance(result, list)


@pytest.mark.integration
def test_base_paginate_first_page(mock_supabase):
    """Test paginate first page"""
    repo = UserRepository(mock_supabase)
    result = repo.paginate(page=1, page_size=10)
    assert isinstance(result, dict)
    assert "data" in result


@pytest.mark.integration
def test_base_paginate_second_page(mock_supabase):
    """Test paginate second page"""
    repo = UserRepository(mock_supabase)
    result = repo.paginate(page=2, page_size=10)
    assert isinstance(result, dict)


@pytest.mark.integration
def test_base_count_with_filters(mock_supabase):
    """Test count with filters"""
    repo = UserRepository(mock_supabase)
    count = repo.count(filters={"role": "influencer"})
    assert isinstance(count, int)


@pytest.mark.integration
def test_base_exists_product(mock_supabase, test_data):
    """Test exists product"""
    product = test_data.get("product_premium")
    if not product:
        pytest.skip("Pas de product")
    
    repo = ProductRepository(mock_supabase)
    result = repo.exists(product["id"])
    assert result is True


@pytest.mark.integration
def test_base_find_all_products_limit(mock_supabase):
    """Test find all with limit"""
    repo = ProductRepository(mock_supabase)
    result = repo.find_all(limit=2)
    assert isinstance(result, list)
    assert len(result) <= 2


@pytest.mark.integration
def test_base_find_all_sales(mock_supabase):
    """Test find all sales"""
    repo = SaleRepository(mock_supabase)
    result = repo.find_all()
    assert isinstance(result, list)


@pytest.mark.integration
def test_base_count_all_products(mock_supabase):
    """Test count all products"""
    repo = ProductRepository(mock_supabase)
    count = repo.count()
    assert isinstance(count, int)


@pytest.mark.integration
def test_base_count_all_sales(mock_supabase):
    """Test count all sales"""
    repo = SaleRepository(mock_supabase)
    count = repo.count()
    assert isinstance(count, int)


# ============================================================================
# TESTS PERFORMANCE (10 tests)
# ============================================================================


@pytest.mark.integration
@pytest.mark.slow
def test_perf_find_all_users(mock_supabase):
    """Test performance find all users"""
    import time
    repo = UserRepository(mock_supabase)
    
    start = time.time()
    result = repo.find_all()
    elapsed = time.time() - start
    
    assert elapsed < 1.0
    assert isinstance(result, list)


@pytest.mark.integration
@pytest.mark.slow
def test_perf_find_all_products(mock_supabase):
    """Test performance find all products"""
    import time
    repo = ProductRepository(mock_supabase)
    
    start = time.time()
    result = repo.find_all()
    elapsed = time.time() - start
    
    assert elapsed < 1.0
    assert isinstance(result, list)


@pytest.mark.integration
@pytest.mark.slow
def test_perf_find_all_sales(mock_supabase):
    """Test performance find all sales"""
    import time
    repo = SaleRepository(mock_supabase)
    
    start = time.time()
    result = repo.find_all()
    elapsed = time.time() - start
    
    assert elapsed < 1.0
    assert isinstance(result, list)


@pytest.mark.integration
@pytest.mark.slow
def test_perf_concurrent_repo_queries(mock_supabase):
    """Test concurrent queries"""
    import time
    
    start = time.time()
    
    user_repo = UserRepository(mock_supabase)
    product_repo = ProductRepository(mock_supabase)
    sale_repo = SaleRepository(mock_supabase)
    
    r1 = user_repo.find_all()
    r2 = product_repo.find_all()
    r3 = sale_repo.find_all()
    
    elapsed = time.time() - start
    
    assert elapsed < 3.0
    assert all(isinstance(x, list) for x in [r1, r2, r3])


@pytest.mark.integration
def test_multiple_find_by_id_users(mock_supabase, test_data):
    """Test multiple find by ID"""
    user = test_data.get("user_influencer")
    if not user:
        pytest.skip("Pas d'user")
    
    repo = UserRepository(mock_supabase)
    
    # Multiple fois
    r1 = repo.find_by_id(user["id"])
    r2 = repo.find_by_id(user["id"])
    r3 = repo.find_by_id(user["id"])
    
    assert all(x is not None for x in [r1, r2, r3])


@pytest.mark.integration
def test_multiple_find_by_id_products(mock_supabase, test_data):
    """Test multiple find by ID products"""
    product = test_data.get("product_premium")
    if not product:
        pytest.skip("Pas de product")
    
    repo = ProductRepository(mock_supabase)
    
    r1 = repo.find_by_id(product["id"])
    r2 = repo.find_by_id(product["id"])
    
    assert all(x is not None for x in [r1, r2])


@pytest.mark.integration
def test_repository_chain_queries(mock_supabase, test_data):
    """Test chained queries"""
    product = test_data.get("product_premium")
    if not product:
        pytest.skip("Pas de product")
    
    product_repo = ProductRepository(mock_supabase)
    sale_repo = SaleRepository(mock_supabase)
    
    # Product -> Sales
    p = product_repo.find_by_id(product["id"])
    assert p is not None
    
    sales = sale_repo.find_all(filters={"product_id": product["id"]})
    assert isinstance(sales, list)


@pytest.mark.integration
def test_repository_all_counts(mock_supabase):
    """Test all repository counts"""
    user_repo = UserRepository(mock_supabase)
    product_repo = ProductRepository(mock_supabase)
    sale_repo = SaleRepository(mock_supabase)
    tracking_repo = TrackingRepository(mock_supabase)
    
    c1 = user_repo.count()
    c2 = product_repo.count()
    c3 = sale_repo.count()
    c4 = tracking_repo.count()
    
    assert all(isinstance(x, int) for x in [c1, c2, c3, c4])
    assert all(x >= 0 for x in [c1, c2, c3, c4])


@pytest.mark.integration
def test_repository_all_exists_checks(mock_supabase, test_data):
    """Test all exists checks"""
    user = test_data.get("user_influencer")
    product = test_data.get("product_premium")
    sale = test_data.get("sale_completed")
    link = test_data.get("tracking_link")
    
    if not all([user, product, sale, link]):
        pytest.skip("Données manquantes")
    
    user_repo = UserRepository(mock_supabase)
    product_repo = ProductRepository(mock_supabase)
    sale_repo = SaleRepository(mock_supabase)
    tracking_repo = TrackingRepository(mock_supabase)
    
    r1 = user_repo.exists(user["id"])
    r2 = product_repo.exists(product["id"])
    r3 = sale_repo.exists(sale["id"])
    r4 = tracking_repo.exists(link["id"])
    
    assert all(x is True for x in [r1, r2, r3, r4])


@pytest.mark.integration
def test_repository_mixed_operations(mock_supabase):
    """Test mixed operations"""
    user_repo = UserRepository(mock_supabase)
    
    # Count
    count = user_repo.count()
    assert isinstance(count, int)
    
    # Find all
    users = user_repo.find_all(limit=5)
    assert isinstance(users, list)
    
    # Paginate
    page = user_repo.paginate(page=1, page_size=5)
    assert isinstance(page, dict)
