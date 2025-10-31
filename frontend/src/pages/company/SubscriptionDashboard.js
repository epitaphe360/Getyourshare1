import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  LinearProgress,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import PeopleIcon from '@mui/icons-material/People';
import LanguageIcon from '@mui/icons-material/Language';
import UpgradeIcon from '@mui/icons-material/Upgrade';
import CancelIcon from '@mui/icons-material/Cancel';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';

/**
 * Dashboard d'abonnement - Gestion de l'abonnement entreprise
 *
 * Fonctionnalités:
 * - Vue d'ensemble de l'abonnement actuel
 * - Utilisation vs limites (membres, domaines)
 * - Upgrade/downgrade de plan
 * - Annulation d'abonnement
 * - Historique de facturation
 */

const SubscriptionDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState(null);
  const [usage, setUsage] = useState(null);
  const [error, setError] = useState(null);
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);

  useEffect(() => {
    fetchSubscriptionData();
  }, []);

  const fetchSubscriptionData = async () => {
    try {
      const [subResponse, usageResponse] = await Promise.all([
        api.get('/api/subscriptions/my-subscription'),
        api.get('/api/subscriptions/usage')
      ]);

      setSubscription(subResponse.data);
      setUsage(usageResponse.data);
    } catch (err) {
      console.error('Error fetching subscription:', err);
      setError('Erreur lors du chargement de l\'abonnement');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = () => {
    navigate('/pricing');
  };

  const handleCancelSubscription = async () => {
    try {
      await api.post('/api/subscriptions/cancel', {
        immediate: false
      });

      alert('Abonnement annulé. Votre accès restera actif jusqu\'à la fin de la période en cours.');
      setCancelDialogOpen(false);
      fetchSubscriptionData();
    } catch (err) {
      console.error('Error canceling subscription:', err);
      alert('Erreur lors de l\'annulation');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'trialing':
        return 'info';
      case 'past_due':
        return 'warning';
      case 'canceled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'active':
        return 'Actif';
      case 'trialing':
        return 'Période d\'essai';
      case 'past_due':
        return 'Paiement en retard';
      case 'canceled':
        return 'Annulé';
      default:
        return status;
    }
  };

  const calculatePercentage = (used, limit) => {
    if (limit === null) return 0; // Illimité
    return (used / limit) * 100;
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error || !subscription) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">
          {error || 'Aucun abonnement actif'}
        </Alert>
        <Button
          variant="contained"
          onClick={() => navigate('/pricing')}
          sx={{ mt: 2 }}
        >
          Choisir un plan
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Mon abonnement
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Gérez votre abonnement et suivez votre utilisation
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Plan Details Card */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 3 }}>
                <Box>
                  <Typography variant="h5" gutterBottom fontWeight="bold">
                    Plan {subscription.plan_name}
                  </Typography>
                  <Chip
                    label={getStatusLabel(subscription.status)}
                    color={getStatusColor(subscription.status)}
                    sx={{ mr: 1 }}
                  />
                  {subscription.plan_type === 'enterprise' && (
                    <Chip label="Entreprise" color="primary" variant="outlined" />
                  )}
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="body2" color="text.secondary">
                    Prochaine facturation
                  </Typography>
                  <Typography variant="h6" fontWeight="bold">
                    {new Date(subscription.current_period_end).toLocaleDateString('fr-FR')}
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ my: 3 }} />

              {/* Limits */}
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Utilisation
              </Typography>

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <PeopleIcon sx={{ mr: 1 }} color="primary" />
                    <Typography variant="body1">Membres d'équipe</Typography>
                  </Box>
                  <Typography variant="body1" fontWeight="bold">
                    {subscription.current_team_members} / {subscription.plan_max_team_members || '∞'}
                  </Typography>
                </Box>
                {subscription.plan_max_team_members && (
                  <LinearProgress
                    variant="determinate"
                    value={calculatePercentage(subscription.current_team_members, subscription.plan_max_team_members)}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                )}
                {!subscription.can_add_team_member && subscription.plan_max_team_members && (
                  <Alert severity="warning" sx={{ mt: 1 }}>
                    Limite de membres atteinte. Passez à un plan supérieur pour ajouter plus de membres.
                  </Alert>
                )}
              </Box>

              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <LanguageIcon sx={{ mr: 1 }} color="primary" />
                    <Typography variant="body1">Domaines autorisés</Typography>
                  </Box>
                  <Typography variant="body1" fontWeight="bold">
                    {subscription.current_domains} / {subscription.plan_max_domains || '∞'}
                  </Typography>
                </Box>
                {subscription.plan_max_domains && (
                  <LinearProgress
                    variant="determinate"
                    value={calculatePercentage(subscription.current_domains, subscription.plan_max_domains)}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                )}
                {!subscription.can_add_domain && subscription.plan_max_domains && (
                  <Alert severity="warning" sx={{ mt: 1 }}>
                    Limite de domaines atteinte. Passez à un plan supérieur pour ajouter plus de domaines.
                  </Alert>
                )}
              </Box>

              <Divider sx={{ my: 3 }} />

              {/* Actions */}
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  startIcon={<UpgradeIcon />}
                  onClick={handleUpgrade}
                >
                  Changer de plan
                </Button>
                {subscription.status === 'active' && (
                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={<CancelIcon />}
                    onClick={() => setCancelDialogOpen(true)}
                  >
                    Annuler l'abonnement
                  </Button>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={4}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Plan actuel
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {subscription.plan_name}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {subscription.plan_type === 'enterprise' ? 'Entreprise' : 'Marketplace'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Membres disponibles
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color="primary">
                    {subscription.plan_max_team_members === null
                      ? '∞'
                      : subscription.plan_max_team_members - subscription.current_team_members}
                  </Typography>
                  {subscription.can_add_team_member ? (
                    <Chip
                      icon={<CheckCircleIcon />}
                      label="Vous pouvez ajouter"
                      color="success"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  ) : (
                    <Chip
                      icon={<WarningIcon />}
                      label="Limite atteinte"
                      color="warning"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Domaines disponibles
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color="primary">
                    {subscription.plan_max_domains === null
                      ? '∞'
                      : subscription.plan_max_domains - subscription.current_domains}
                  </Typography>
                  {subscription.can_add_domain ? (
                    <Chip
                      icon={<CheckCircleIcon />}
                      label="Vous pouvez ajouter"
                      color="success"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  ) : (
                    <Chip
                      icon={<WarningIcon />}
                      label="Limite atteinte"
                      color="warning"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Features List */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Fonctionnalités incluses
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Génération de liens d'affiliation"
                    secondary="Créez et gérez des liens pour vos produits"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Attribution de liens aux membres"
                    secondary="Assignez des liens à vos commerciaux et influenceurs"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Suivi des performances"
                    secondary="Tableaux de bord et statistiques détaillées"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Gestion d'équipe"
                    secondary={`Jusqu'à ${subscription.plan_max_team_members || 'un nombre illimité de'} membres`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Domaines personnalisés"
                    secondary={`${subscription.plan_max_domains || 'Nombre illimité de'} domaine(s) vérifiés`}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Cancel Dialog */}
      <Dialog open={cancelDialogOpen} onClose={() => setCancelDialogOpen(false)}>
        <DialogTitle>Annuler l'abonnement</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            Êtes-vous sûr de vouloir annuler votre abonnement ?
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            Votre accès restera actif jusqu'au {new Date(subscription.current_period_end).toLocaleDateString('fr-FR')}.
            Vous ne serez plus facturé après cette date.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelDialogOpen(false)}>
            Garder mon abonnement
          </Button>
          <Button onClick={handleCancelSubscription} color="error" variant="contained">
            Confirmer l'annulation
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default SubscriptionDashboard;
