"""
Tests unitaires pour le module Sales
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from services.sales.service import SalesService


# ============================================================================
# TESTS: SalesService.__init__
# ============================================================================


def test_sales_service_init(mock_supabase):
    """Test initialisation du service"""
    service = SalesService(mock_supabase)
    assert service.supabase == mock_supabase


# ============================================================================
# TESTS: SalesService.create_sale
# ============================================================================


@pytest.mark.unit
@pytest.mark.sales
def test_create_sale_success(mock_supabase, sample_sale_request, sample_sale):
    """Test création de vente réussie"""
    # Arrange
    mock_supabase.rpc.return_value.execute.return_value.data = sample_sale
    service = SalesService(mock_supabase)

    # Act
    result = service.create_sale(**sample_sale_request)

    # Assert
    assert result == sample_sale
    mock_supabase.rpc.assert_called_once()
    call_args = mock_supabase.rpc.call_args
    assert call_args[0][0] == "create_sale_transaction"
    assert "p_link_id" in call_args[1]
    assert "p_amount" in call_args[1]


@pytest.mark.unit
@pytest.mark.sales
def test_create_sale_invalid_link(mock_supabase, sample_sale_request, mock_postgres_error):
    """Test création avec lien invalide"""
    # Arrange
    error = mock_postgres_error("P0001", "Invalid trackable link")
    mock_supabase.rpc.return_value.execute.side_effect = Exception(
        f"PostgrestAPIError: {error.message}"
    )
    service = SalesService(mock_supabase)

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid trackable link"):
        service.create_sale(**sample_sale_request)


@pytest.mark.unit
@pytest.mark.sales
def test_create_sale_negative_amount(mock_supabase, sample_sale_request):
    """Test création avec montant négatif"""
    # Arrange
    service = SalesService(mock_supabase)
    sample_sale_request["amount"] = -10.0

    # Act & Assert
    with pytest.raises(ValueError, match="Amount must be positive"):
        service.create_sale(**sample_sale_request)


@pytest.mark.unit
@pytest.mark.sales
def test_create_sale_missing_link_id(mock_supabase, sample_sale_request):
    """Test création sans link_id"""
    # Arrange
    service = SalesService(mock_supabase)
    del sample_sale_request["link_id"]

    # Act & Assert
    with pytest.raises(TypeError):
        service.create_sale(**sample_sale_request)


@pytest.mark.unit
@pytest.mark.sales
def test_create_sale_database_error(mock_supabase, sample_sale_request):
    """Test gestion erreur base de données"""
    # Arrange
    mock_supabase.rpc.return_value.execute.side_effect = Exception("Database connection error")
    service = SalesService(mock_supabase)

    # Act & Assert
    with pytest.raises(Exception, match="Database connection error"):
        service.create_sale(**sample_sale_request)


# ============================================================================
# TESTS: SalesService.get_sale_by_id
# ============================================================================


@pytest.mark.unit
@pytest.mark.sales
def test_get_sale_by_id_success(mock_supabase, sample_sale_id, sample_sale):
    """Test récupération vente par ID"""
    # Arrange
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        sample_sale
    ]
    service = SalesService(mock_supabase)

    # Act
    result = service.get_sale_by_id(sample_sale_id)

    # Assert
    assert result == sample_sale
    mock_supabase.table.assert_called_once_with("sales")


@pytest.mark.unit
@pytest.mark.sales
def test_get_sale_by_id_not_found(mock_supabase, sample_sale_id):
    """Test vente non trouvée"""
    # Arrange
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = (
        []
    )
    service = SalesService(mock_supabase)

    # Act
    result = service.get_sale_by_id(sample_sale_id)

    # Assert
    assert result is None


@pytest.mark.unit
@pytest.mark.sales
def test_get_sale_by_id_invalid_uuid(mock_supabase):
    """Test avec UUID invalide"""
    # Arrange
    service = SalesService(mock_supabase)

    # Act & Assert
    with pytest.raises(ValueError):
        service.get_sale_by_id("invalid-uuid")


# ============================================================================
# TESTS: SalesService.get_sales_by_influencer
# ============================================================================


@pytest.mark.unit
@pytest.mark.sales
def test_get_sales_by_influencer_success(mock_supabase, sample_influencer_id, sample_sale):
    """Test récupération ventes par influenceur"""
    # Arrange
    sales_list = [sample_sale, {**sample_sale, "id": str(uuid4())}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = (
        sales_list
    )
    service = SalesService(mock_supabase)

    # Act
    result = service.get_sales_by_influencer(sample_influencer_id, limit=10, offset=0)

    # Assert
    assert len(result) == 2
    assert result == sales_list


@pytest.mark.unit
@pytest.mark.sales
def test_get_sales_by_influencer_with_status_filter(
    mock_supabase, sample_influencer_id, sample_sale
):
    """Test filtrage par statut"""
    # Arrange
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        sample_sale
    ]
    service = SalesService(mock_supabase)

    # Act
    result = service.get_sales_by_influencer(sample_influencer_id, status="completed")

    # Assert
    assert len(result) == 1


@pytest.mark.unit
@pytest.mark.sales
def test_get_sales_by_influencer_empty_result(mock_supabase, sample_influencer_id):
    """Test aucune vente trouvée"""
    # Arrange
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = (
        []
    )
    service = SalesService(mock_supabase)

    # Act
    result = service.get_sales_by_influencer(sample_influencer_id)

    # Assert
    assert result == []


# ============================================================================
# TESTS: SalesService.get_sales_by_merchant
# ============================================================================


@pytest.mark.unit
@pytest.mark.sales
def test_get_sales_by_merchant_success(mock_supabase, sample_merchant_id, sample_sale):
    """Test récupération ventes par merchant"""
    # Arrange
    sales_list = [sample_sale]
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = (
        sales_list
    )
    service = SalesService(mock_supabase)

    # Act
    result = service.get_sales_by_merchant(sample_merchant_id)

    # Assert
    assert result == sales_list


@pytest.mark.unit
@pytest.mark.sales
def test_get_sales_by_merchant_pagination(mock_supabase, sample_merchant_id, sample_sale):
    """Test pagination des résultats"""
    # Arrange
    mock_query = (
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value
    )
    mock_query.limit.return_value.offset.return_value.execute.return_value.data = [sample_sale]
    service = SalesService(mock_supabase)

    # Act
    result = service.get_sales_by_merchant(sample_merchant_id, limit=5, offset=10)

    # Assert
    mock_query.limit.assert_called_once_with(5)
    mock_query.limit.return_value.offset.assert_called_once_with(10)


# ============================================================================
# TESTS: SalesService.update_sale_status
# ============================================================================


@pytest.mark.unit
@pytest.mark.sales
def test_update_sale_status_success(mock_supabase, sample_sale_id, sample_sale):
    """Test mise à jour statut vente"""
    # Arrange
    updated_sale = {**sample_sale, "status": "refunded"}
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
        updated_sale
    ]
    service = SalesService(mock_supabase)

    # Act
    result = service.update_sale_status(sample_sale_id, "refunded")

    # Assert
    assert result["status"] == "refunded"
    mock_supabase.table.assert_called_once_with("sales")


@pytest.mark.unit
@pytest.mark.sales
def test_update_sale_status_invalid_status(mock_supabase, sample_sale_id):
    """Test statut invalide"""
    # Arrange
    service = SalesService(mock_supabase)

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid status"):
        service.update_sale_status(sample_sale_id, "invalid_status")


@pytest.mark.unit
@pytest.mark.sales
def test_update_sale_status_not_found(mock_supabase, sample_sale_id):
    """Test vente non trouvée lors de la mise à jour"""
    # Arrange
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = (
        []
    )
    service = SalesService(mock_supabase)

    # Act
    result = service.update_sale_status(sample_sale_id, "refunded")

    # Assert
    assert result is None


# ============================================================================
# TESTS: Cas limites et edge cases
# ============================================================================


@pytest.mark.unit
@pytest.mark.sales
def test_create_sale_with_all_optional_params(mock_supabase, sample_sale_request, sample_sale):
    """Test création avec tous les paramètres optionnels"""
    # Arrange
    mock_supabase.rpc.return_value.execute.return_value.data = sample_sale
    service = SalesService(mock_supabase)

    full_request = {
        **sample_sale_request,
        "tracking_id": "TRACK-123",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0",
    }

    # Act
    result = service.create_sale(**full_request)

    # Assert
    assert result == sample_sale


@pytest.mark.unit
@pytest.mark.sales
def test_get_sales_by_influencer_large_dataset(mock_supabase, sample_influencer_id, sample_sale):
    """Test performance avec grand nombre de résultats"""
    # Arrange
    large_dataset = [{**sample_sale, "id": str(uuid4())} for _ in range(100)]
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = (
        large_dataset
    )
    service = SalesService(mock_supabase)

    # Act
    result = service.get_sales_by_influencer(sample_influencer_id, limit=100)

    # Assert
    assert len(result) == 100


@pytest.mark.unit
@pytest.mark.sales
def test_concurrent_sale_creation(mock_supabase, sample_sale_request, sample_sale):
    """Test création simultanée de ventes (simulation)"""
    # Arrange
    mock_supabase.rpc.return_value.execute.return_value.data = sample_sale
    service = SalesService(mock_supabase)

    # Act - Simuler 3 créations concurrentes
    results = []
    for _ in range(3):
        result = service.create_sale(**sample_sale_request)
        results.append(result)

    # Assert
    assert len(results) == 3
    assert mock_supabase.rpc.call_count == 3
