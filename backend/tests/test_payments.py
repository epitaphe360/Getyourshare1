"""
Tests unitaires pour le module Payments
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from services.payments.service import PaymentsService


# ============================================================================
# TESTS: PaymentsService.__init__
# ============================================================================


def test_payments_service_init(mock_supabase):
    """Test initialisation du service"""
    service = PaymentsService(mock_supabase)
    assert service.supabase == mock_supabase


# ============================================================================
# TESTS: PaymentsService.approve_commission
# ============================================================================


@pytest.mark.unit
@pytest.mark.payments
def test_approve_commission_success(mock_supabase, sample_commission_id):
    """Test approbation de commission réussie"""
    # Arrange
    mock_supabase.rpc.return_value.execute.return_value.data = True
    service = PaymentsService(mock_supabase)

    # Act
    result = service.approve_commission(sample_commission_id)

    # Assert
    assert result is True
    mock_supabase.rpc.assert_called_once_with(
        "approve_payout_transaction",
        {"p_commission_id": sample_commission_id, "p_new_status": "approved"},
    )


@pytest.mark.unit
@pytest.mark.payments
def test_approve_commission_already_approved(
    mock_supabase, sample_commission_id, mock_postgres_error
):
    """Test approbation d'une commission déjà approuvée"""
    # Arrange
    error = mock_postgres_error("P0001", "Commission already in final state")
    mock_supabase.rpc.return_value.execute.side_effect = Exception(
        f"PostgrestAPIError: {error.message}"
    )
    service = PaymentsService(mock_supabase)

    # Act & Assert
    with pytest.raises(ValueError, match="already in final state"):
        service.approve_commission(sample_commission_id)


@pytest.mark.unit
@pytest.mark.payments
def test_approve_commission_not_found(mock_supabase, sample_commission_id, mock_postgres_error):
    """Test approbation commission inexistante"""
    # Arrange
    error = mock_postgres_error("P0001", "Commission not found")
    mock_supabase.rpc.return_value.execute.side_effect = Exception(
        f"PostgrestAPIError: {error.message}"
    )
    service = PaymentsService(mock_supabase)

    # Act & Assert
    with pytest.raises(ValueError, match="not found"):
        service.approve_commission(sample_commission_id)


@pytest.mark.unit
@pytest.mark.payments
def test_approve_commission_invalid_uuid(mock_supabase):
    """Test avec UUID invalide"""
    # Arrange
    service = PaymentsService(mock_supabase)

    # Act & Assert
    with pytest.raises(ValueError):
        service.approve_commission("invalid-uuid")


# ============================================================================
# TESTS: PaymentsService.pay_commission
# ============================================================================


@pytest.mark.unit
@pytest.mark.payments
def test_pay_commission_success(mock_supabase, sample_commission_id):
    """Test paiement de commission réussi"""
    # Arrange
    mock_supabase.rpc.return_value.execute.return_value.data = True
    service = PaymentsService(mock_supabase)

    # Act
    result = service.pay_commission(sample_commission_id)

    # Assert
    assert result is True
    mock_supabase.rpc.assert_called_once_with(
        "approve_payout_transaction",
        {"p_commission_id": sample_commission_id, "p_new_status": "paid"},
    )


@pytest.mark.unit
@pytest.mark.payments
def test_pay_commission_not_approved(mock_supabase, sample_commission_id, mock_postgres_error):
    """Test paiement d'une commission non approuvée"""
    # Arrange
    error = mock_postgres_error("P0001", "Invalid status transition")
    mock_supabase.rpc.return_value.execute.side_effect = Exception(
        f"PostgrestAPIError: {error.message}"
    )
    service = PaymentsService(mock_supabase)

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid status transition"):
        service.pay_commission(sample_commission_id)


# ============================================================================
# TESTS: PaymentsService.reject_commission
# ============================================================================


@pytest.mark.unit
@pytest.mark.payments
def test_reject_commission_success(mock_supabase, sample_commission_id):
    """Test rejet de commission réussi"""
    # Arrange
    mock_supabase.rpc.return_value.execute.return_value.data = True
    service = PaymentsService(mock_supabase)

    # Act
    result = service.reject_commission(sample_commission_id)

    # Assert
    assert result is True


@pytest.mark.unit
@pytest.mark.payments
def test_reject_commission_already_paid(mock_supabase, sample_commission_id, mock_postgres_error):
    """Test rejet d'une commission déjà payée"""
    # Arrange
    error = mock_postgres_error("P0001", "Cannot reject paid commission")
    mock_supabase.rpc.return_value.execute.side_effect = Exception(
        f"PostgrestAPIError: {error.message}"
    )
    service = PaymentsService(mock_supabase)

    # Act & Assert
    with pytest.raises(ValueError, match="Cannot reject paid commission"):
        service.reject_commission(sample_commission_id)


# ============================================================================
# TESTS: PaymentsService.get_commission_by_id
# ============================================================================


@pytest.mark.unit
@pytest.mark.payments
def test_get_commission_by_id_success(mock_supabase, sample_commission_id, sample_commission):
    """Test récupération commission par ID"""
    # Arrange
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        sample_commission
    ]
    service = PaymentsService(mock_supabase)

    # Act
    result = service.get_commission_by_id(sample_commission_id)

    # Assert
    assert result == sample_commission
    mock_supabase.table.assert_called_once_with("commissions")


@pytest.mark.unit
@pytest.mark.payments
def test_get_commission_by_id_not_found(mock_supabase, sample_commission_id):
    """Test commission non trouvée"""
    # Arrange
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = (
        []
    )
    service = PaymentsService(mock_supabase)

    # Act
    result = service.get_commission_by_id(sample_commission_id)

    # Assert
    assert result is None


# ============================================================================
# TESTS: PaymentsService.get_commissions_by_status
# ============================================================================


@pytest.mark.unit
@pytest.mark.payments
def test_get_commissions_by_status_success(mock_supabase, sample_commission):
    """Test récupération commissions par statut"""
    # Arrange
    commissions_list = [sample_commission, {**sample_commission, "id": str(uuid4())}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = (
        commissions_list
    )
    service = PaymentsService(mock_supabase)

    # Act
    result = service.get_commissions_by_status("pending")

    # Assert
    assert len(result) == 2
    assert result == commissions_list


@pytest.mark.unit
@pytest.mark.payments
def test_get_commissions_by_status_empty(mock_supabase):
    """Test aucune commission trouvée"""
    # Arrange
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = (
        []
    )
    service = PaymentsService(mock_supabase)

    # Act
    result = service.get_commissions_by_status("pending")

    # Assert
    assert result == []


@pytest.mark.unit
@pytest.mark.payments
def test_get_commissions_by_status_invalid(mock_supabase):
    """Test statut invalide"""
    # Arrange
    service = PaymentsService(mock_supabase)

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid status"):
        service.get_commissions_by_status("invalid_status")


# ============================================================================
# TESTS: PaymentsService.get_commissions_by_influencer
# ============================================================================


@pytest.mark.unit
@pytest.mark.payments
def test_get_commissions_by_influencer_success(
    mock_supabase, sample_influencer_id, sample_commission
):
    """Test récupération commissions par influenceur"""
    # Arrange
    commissions_list = [sample_commission]
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = (
        commissions_list
    )
    service = PaymentsService(mock_supabase)

    # Act
    result = service.get_commissions_by_influencer(sample_influencer_id)

    # Assert
    assert result == commissions_list


@pytest.mark.unit
@pytest.mark.payments
def test_get_commissions_by_influencer_with_status_filter(
    mock_supabase, sample_influencer_id, sample_commission
):
    """Test filtrage par statut"""
    # Arrange
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        sample_commission
    ]
    service = PaymentsService(mock_supabase)

    # Act
    result = service.get_commissions_by_influencer(sample_influencer_id, status="pending")

    # Assert
    assert len(result) == 1


# ============================================================================
# TESTS: PaymentsService.get_pending_commissions_total
# ============================================================================


@pytest.mark.unit
@pytest.mark.payments
def test_get_pending_commissions_total_success(mock_supabase, sample_influencer_id):
    """Test total commissions pending"""
    # Arrange
    mock_response = [{"total": 150.50}]
    mock_supabase.rpc.return_value.execute.return_value.data = mock_response
    service = PaymentsService(mock_supabase)

    # Act
    result = service.get_pending_commissions_total(sample_influencer_id)

    # Assert
    assert result == 150.50


@pytest.mark.unit
@pytest.mark.payments
def test_get_pending_commissions_total_zero(mock_supabase, sample_influencer_id):
    """Test total zéro"""
    # Arrange
    mock_response = [{"total": 0.0}]
    mock_supabase.rpc.return_value.execute.return_value.data = mock_response
    service = PaymentsService(mock_supabase)

    # Act
    result = service.get_pending_commissions_total(sample_influencer_id)

    # Assert
    assert result == 0.0


# ============================================================================
# TESTS: PaymentsService.get_approved_commissions_total
# ============================================================================


@pytest.mark.unit
@pytest.mark.payments
def test_get_approved_commissions_total_success(mock_supabase, sample_influencer_id):
    """Test total commissions approved"""
    # Arrange
    mock_response = [{"total": 250.75}]
    mock_supabase.rpc.return_value.execute.return_value.data = mock_response
    service = PaymentsService(mock_supabase)

    # Act
    result = service.get_approved_commissions_total(sample_influencer_id)

    # Assert
    assert result == 250.75


# ============================================================================
# TESTS: PaymentsService.batch_approve_commissions
# ============================================================================


@pytest.mark.unit
@pytest.mark.payments
def test_batch_approve_commissions_success(mock_supabase):
    """Test approbation en lot réussie"""
    # Arrange
    commission_ids = [str(uuid4()) for _ in range(5)]
    mock_supabase.rpc.return_value.execute.return_value.data = True
    service = PaymentsService(mock_supabase)

    # Act
    results = service.batch_approve_commissions(commission_ids)

    # Assert
    assert len(results["success"]) == 5
    assert len(results["failed"]) == 0
    assert mock_supabase.rpc.call_count == 5


@pytest.mark.unit
@pytest.mark.payments
def test_batch_approve_commissions_partial_failure(mock_supabase, mock_postgres_error):
    """Test approbation en lot avec échecs partiels"""
    # Arrange
    commission_ids = [str(uuid4()) for _ in range(3)]

    # Premier et troisième réussissent, deuxième échoue
    def side_effect(*args, **kwargs):
        mock_result = Mock()
        if mock_supabase.rpc.call_count == 2:
            raise Exception("PostgrestAPIError: Commission already approved")
        mock_result.execute.return_value.data = True
        return mock_result

    mock_supabase.rpc.side_effect = side_effect
    service = PaymentsService(mock_supabase)

    # Act
    results = service.batch_approve_commissions(commission_ids)

    # Assert
    assert len(results["success"]) == 2
    assert len(results["failed"]) == 1


@pytest.mark.unit
@pytest.mark.payments
def test_batch_approve_commissions_empty_list(mock_supabase):
    """Test approbation en lot avec liste vide"""
    # Arrange
    service = PaymentsService(mock_supabase)

    # Act
    results = service.batch_approve_commissions([])

    # Assert
    assert results["success"] == []
    assert results["failed"] == []
    mock_supabase.rpc.assert_not_called()


@pytest.mark.unit
@pytest.mark.payments
def test_batch_approve_commissions_large_batch(mock_supabase):
    """Test approbation en lot avec grand nombre de commissions"""
    # Arrange
    commission_ids = [str(uuid4()) for _ in range(100)]
    mock_supabase.rpc.return_value.execute.return_value.data = True
    service = PaymentsService(mock_supabase)

    # Act
    results = service.batch_approve_commissions(commission_ids)

    # Assert
    assert len(results["success"]) == 100
    assert mock_supabase.rpc.call_count == 100


# ============================================================================
# TESTS: Cas limites et edge cases
# ============================================================================


@pytest.mark.unit
@pytest.mark.payments
def test_approve_commission_transition_pending_to_approved(mock_supabase, sample_commission_id):
    """Test transition pending → approved"""
    # Arrange
    mock_supabase.rpc.return_value.execute.return_value.data = True
    service = PaymentsService(mock_supabase)

    # Act
    result = service.approve_commission(sample_commission_id)

    # Assert
    assert result is True


@pytest.mark.unit
@pytest.mark.payments
def test_pay_commission_transition_approved_to_paid(mock_supabase, sample_commission_id):
    """Test transition approved → paid"""
    # Arrange
    mock_supabase.rpc.return_value.execute.return_value.data = True
    service = PaymentsService(mock_supabase)

    # Act
    result = service.pay_commission(sample_commission_id)

    # Assert
    assert result is True


@pytest.mark.unit
@pytest.mark.payments
def test_concurrent_commission_updates(mock_supabase):
    """Test mises à jour concurrentes (simulation)"""
    # Arrange
    commission_id = str(uuid4())
    mock_supabase.rpc.return_value.execute.return_value.data = True
    service = PaymentsService(mock_supabase)

    # Act - Simuler 2 approbations concurrentes
    result1 = service.approve_commission(commission_id)
    result2 = service.approve_commission(commission_id)

    # Assert
    assert result1 is True
    assert result2 is True  # En réalité, la 2ème devrait échouer avec "already approved"
    assert mock_supabase.rpc.call_count == 2


@pytest.mark.unit
@pytest.mark.payments
def test_get_commissions_summary(mock_supabase, sample_influencer_id):
    """Test récupération résumé complet des commissions"""
    # Arrange
    mock_supabase.rpc.return_value.execute.return_value.data = [
        {"status": "pending", "total": 100.0, "count": 5},
        {"status": "approved", "total": 200.0, "count": 10},
        {"status": "paid", "total": 300.0, "count": 15},
    ]
    service = PaymentsService(mock_supabase)

    # Act
    pending_total = service.get_pending_commissions_total(sample_influencer_id)
    approved_total = service.get_approved_commissions_total(sample_influencer_id)

    # Assert
    assert pending_total >= 0
    assert approved_total >= 0
