import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import BusinessIcon from '@mui/icons-material/Business';
import PersonIcon from '@mui/icons-material/Person';
import StarIcon from '@mui/icons-material/Star';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import paymentService from '../services/paymentService';
import { useToast } from '../context/ToastContext';

/**
 * Page des tarifs - 4 plans d'abonnement conformes aux spécifications
 *
 * PLANS ENTREPRISE:
 * - Small: 199 MAD/mois (2 membres, 1 domaine)
 * - Medium: 499 MAD/mois (10 membres, 2 domaines) - POPULAIRE
 * - Large: 799 MAD/mois (30 membres, domaines illimités)
 *
 * PLAN MARKETPLACE:
 * - Marketplace: 99 MAD/mois (indépendants)
 */

const PricingV3 = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [annualBilling, setAnnualBilling] = useState(false);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [processingPayment, setProcessingPayment] = useState(false);

  useEffect(() => {
    fetchPlans();
    fetchCurrentSubscription();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await api.get('/api/subscriptions/plans');
      // S'assurer que response.data est bien un tableau
      const plansData = Array.isArray(response.data) ? response.data : (response.data.plans || []);
      setPlans(plansData);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching plans:', err);
      setError('Erreur lors du chargement des plans');
      setPlans([]); // S'assurer que plans reste un tableau même en cas d'erreur
      setLoading(false);
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const response = await api.get('/api/subscriptions/my-subscription');
      setCurrentSubscription(response.data);
    } catch (err) {
      // User may not have a subscription yet
      console.log('No current subscription');
    }
  };

  const handleSubscribe = async (planId) => {
    if (processingPayment) return;
    
    try {
      setProcessingPayment(true);
      
      // Trouver le plan sélectionné
      const selectedPlan = plans.find(p => p.id === planId);
      if (!selectedPlan) {
        toast.error('Plan non trouvé');
        return;
      }
      
      // Calculer le montant (annuel ou mensuel)
      const amount = annualBilling ? selectedPlan.price * 10 : selectedPlan.price;
      
      toast.info('Redirection vers la page de paiement sécurisée...');
      
      // Initialiser le paiement via notre service
      await paymentService.initiateSubscriptionPayment({
        plan_id: planId,
        plan_name: selectedPlan.name,
        amount: amount,
        billing_cycle: annualBilling ? 'annual' : 'monthly'
      }, 'cmi'); // CMI par défaut pour le Maroc, ou 'stripe' pour international
      
      // La redirection vers la page de paiement est gérée automatiquement par le service
      
    } catch (err) {
      console.error('Error initiating subscription:', err);
      toast.error(err.message || 'Erreur lors de l\'initialisation du paiement');
      setProcessingPayment(false);
    }
  };

  const calculatePrice = (monthlyPrice) => {
    if (annualBilling) {
      // 2 mois gratuits si paiement annuel (10 mois au lieu de 12)
      return (monthlyPrice * 10).toFixed(2);
    }
    return monthlyPrice.toFixed(2);
  };

  const isCurrentPlan = (planId) => {
    return currentSubscription?.plan_id === planId;
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  // Séparer les plans entreprise et marketplace
  const enterprisePlans = Array.isArray(plans) ? plans.filter(p => p.type === 'enterprise').sort((a, b) => a.price_mad - b.price_mad) : [];
  const marketplacePlans = Array.isArray(plans) ? plans.filter(p => p.type === 'marketplace') : [];

  return (
    <Box sx={{ bgcolor: '#f8f9fa', minHeight: '100vh', py: 6 }}>
      <Container maxWidth="lg">
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="h3" component="h1" gutterBottom fontWeight="700" color="primary">
            Tarifs Share Your Sales
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4, maxWidth: 700, mx: 'auto' }}>
            Choisissez la formule adaptée à vos besoins. Tous les plans incluent 14 jours d'essai gratuit.
          </Typography>

          {/* Toggle Annual/Monthly */}
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography
              fontWeight={!annualBilling ? 600 : 400}
              color={!annualBilling ? 'primary' : 'text.secondary'}
            >
              Facturation mensuelle
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={annualBilling}
                  onChange={(e) => setAnnualBilling(e.target.checked)}
                  color="primary"
                />
              }
              label=""
            />
            <Typography
              fontWeight={annualBilling ? 600 : 400}
              color={annualBilling ? 'primary' : 'text.secondary'}
            >
              Facturation annuelle
            </Typography>
          </Box>
          {annualBilling && (
            <Chip
              icon={<StarIcon />}
              label="Économisez 2 mois (16% de réduction)"
              color="success"
              size="medium"
              sx={{ fontWeight: 600 }}
            />
          )}
        </Box>

        {/* Enterprise Plans */}
        <Box sx={{ mb: 10 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 4 }}>
            <BusinessIcon sx={{ mr: 1.5, fontSize: 36, color: 'primary.main' }} />
            <Typography variant="h4" component="h2" fontWeight="700" color="primary.dark">
              Plans Entreprise
            </Typography>
          </Box>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 5, textAlign: 'center', maxWidth: 800, mx: 'auto' }}>
            Pour les entreprises qui souhaitent créer et gérer une équipe de commerciaux et d'influenceurs.
            Générez des liens d'affiliation et suivez les performances de chaque membre.
          </Typography>

          <Grid container spacing={3} justifyContent="center">
            {enterprisePlans.map((plan, index) => {
              const isPopular = plan.code === 'enterprise_medium';

              return (
                <Grid item xs={12} sm={6} md={4} key={plan.id}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      position: 'relative',
                      border: isPopular ? 3 : 1,
                      borderColor: isPopular ? 'primary.main' : 'divider',
                      boxShadow: isPopular ? 8 : 2,
                      transition: 'all 0.3s ease',
                      transform: isPopular ? 'scale(1.05)' : 'scale(1)',
                      '&:hover': {
                        transform: isPopular ? 'scale(1.07)' : 'scale(1.03)',
                        boxShadow: 10
                      }
                    }}
                  >
                    {isPopular && (
                      <Box
                        sx={{
                          position: 'absolute',
                          top: -12,
                          left: '50%',
                          transform: 'translateX(-50%)',
                          zIndex: 1
                        }}
                      >
                        <Chip
                          icon={<StarIcon />}
                          label="Le plus populaire"
                          color="primary"
                          sx={{ fontWeight: 700, px: 1 }}
                        />
                      </Box>
                    )}

                    <CardContent sx={{ flexGrow: 1, pt: isPopular ? 5 : 3, px: 3 }}>
                      <Typography variant="h5" component="h3" gutterBottom fontWeight="700" align="center">
                        {plan.name}
                      </Typography>

                      <Box sx={{ my: 3, textAlign: 'center' }}>
                        <Typography variant="h2" component="div" fontWeight="700" color="primary.main">
                          {calculatePrice(plan.price_mad)}
                          <Typography component="span" variant="h5" color="text.secondary" fontWeight={400}>
                            {' '}MAD
                          </Typography>
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {annualBilling ? 'facturé annuellement' : 'par mois'}
                        </Typography>
                        {annualBilling && (
                          <Typography variant="caption" color="success.main" fontWeight={600}>
                            (soit {(plan.price_mad * 10 / 12).toFixed(2)} MAD/mois)
                          </Typography>
                        )}
                      </Box>

                      <Divider sx={{ my: 2 }} />

                      <List dense sx={{ mb: 2 }}>
                        <ListItem sx={{ px: 0 }}>
                          <ListItemIcon sx={{ minWidth: 36 }}>
                            <CheckCircleIcon color="success" />
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Typography variant="body2" fontWeight={600}>
                                {plan.max_team_members} membres d'équipe
                              </Typography>
                            }
                          />
                        </ListItem>

                        <ListItem sx={{ px: 0 }}>
                          <ListItemIcon sx={{ minWidth: 36 }}>
                            <CheckCircleIcon color="success" />
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Typography variant="body2" fontWeight={600}>
                                {plan.max_domains === null
                                  ? 'Domaines illimités'
                                  : `${plan.max_domains} domaine${plan.max_domains > 1 ? 's' : ''}`}
                              </Typography>
                            }
                          />
                        </ListItem>

                        {plan.features && plan.features.map((feature, idx) => (
                          <ListItem key={idx} sx={{ px: 0 }}>
                            <ListItemIcon sx={{ minWidth: 36 }}>
                              <CheckCircleIcon color="success" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText
                              primary={<Typography variant="body2">{feature}</Typography>}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>

                    <CardActions sx={{ p: 3, pt: 0 }}>
                      {isCurrentPlan(plan.id) ? (
                        <Button
                          fullWidth
                          variant="outlined"
                          size="large"
                          disabled
                        >
                          Plan actuel
                        </Button>
                      ) : (
                        <Button
                          fullWidth
                          variant={isPopular ? 'contained' : 'outlined'}
                          size="large"
                          onClick={() => handleSubscribe(plan.id)}
                          sx={{ fontWeight: 600 }}
                        >
                          {currentSubscription ? 'Changer de plan' : 'Commencer l\'essai gratuit'}
                        </Button>
                      )}
                    </CardActions>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </Box>

        {/* Marketplace Plan */}
        {marketplacePlans.length > 0 && (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 4 }}>
              <PersonIcon sx={{ mr: 1.5, fontSize: 36, color: 'secondary.main' }} />
              <Typography variant="h4" component="h2" fontWeight="700" color="secondary.dark">
                Plan Marketplace
              </Typography>
            </Box>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 5, textAlign: 'center', maxWidth: 800, mx: 'auto' }}>
              Pour les commerciaux et influenceurs indépendants. Accédez au marketplace, créez votre profil,
              et recevez des demandes de collaboration d'entreprises.
            </Typography>

            <Grid container spacing={3} justifyContent="center">
              {marketplacePlans.map((plan) => (
                <Grid item xs={12} sm={8} md={5} key={plan.id}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      border: 2,
                      borderColor: 'secondary.main',
                      boxShadow: 6,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'scale(1.03)',
                        boxShadow: 10
                      }
                    }}
                  >
                    <CardContent sx={{ flexGrow: 1, p: 4 }}>
                      <Typography variant="h5" component="h3" gutterBottom fontWeight="700" align="center">
                        {plan.name}
                      </Typography>

                      <Box sx={{ my: 3, textAlign: 'center' }}>
                        <Typography variant="h2" component="div" fontWeight="700" color="secondary.main">
                          {calculatePrice(plan.price_mad)}
                          <Typography component="span" variant="h5" color="text.secondary" fontWeight={400}>
                            {' '}MAD
                          </Typography>
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {annualBilling ? 'facturé annuellement' : 'par mois'}
                        </Typography>
                        {annualBilling && (
                          <Typography variant="caption" color="success.main" fontWeight={600}>
                            (soit {(plan.price_mad * 10 / 12).toFixed(2)} MAD/mois)
                          </Typography>
                        )}
                      </Box>

                      <Divider sx={{ my: 2 }} />

                      <List dense sx={{ mb: 2 }}>
                        {plan.features && plan.features.map((feature, idx) => (
                          <ListItem key={idx} sx={{ px: 0 }}>
                            <ListItemIcon sx={{ minWidth: 36 }}>
                              <CheckCircleIcon color="success" />
                            </ListItemIcon>
                            <ListItemText
                              primary={<Typography variant="body2" fontWeight={500}>{feature}</Typography>}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>

                    <CardActions sx={{ p: 4, pt: 0 }}>
                      {isCurrentPlan(plan.id) ? (
                        <Button
                          fullWidth
                          variant="outlined"
                          size="large"
                          disabled
                        >
                          Plan actuel
                        </Button>
                      ) : (
                        <Button
                          fullWidth
                          variant="contained"
                          color="secondary"
                          size="large"
                          onClick={() => handleSubscribe(plan.id)}
                          sx={{ fontWeight: 600 }}
                        >
                          {currentSubscription ? 'Changer de plan' : 'Commencer l\'essai gratuit'}
                        </Button>
                      )}
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* FAQ Section */}
        <Box sx={{ mt: 10, bgcolor: 'white', borderRadius: 3, p: 5 }}>
          <Typography variant="h4" gutterBottom fontWeight="700" align="center" sx={{ mb: 5 }}>
            Questions fréquentes
          </Typography>

          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Puis-je changer de plan à tout moment ?
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Oui, vous pouvez upgrader ou downgrader votre plan à tout moment.
                Les changements prennent effet immédiatement avec un calcul au prorata.
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Comment fonctionne l'essai gratuit ?
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Tous les plans bénéficient de 14 jours d'essai gratuit sans engagement.
                Aucune carte bancaire n'est demandée pendant la période d'essai.
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Puis-je annuler mon abonnement ?
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Oui, vous pouvez annuler à tout moment depuis votre tableau de bord.
                Votre accès reste actif jusqu'à la fin de votre période de facturation.
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Quels moyens de paiement acceptez-vous ?
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Nous acceptons les cartes bancaires (Visa, Mastercard, Amex)
                via notre partenaire de paiement sécurisé Stripe.
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Que se passe-t-il si je dépasse les limites de mon plan ?
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Vous serez averti lorsque vous approchez des limites.
                Vous pourrez alors upgrader votre plan pour continuer à ajouter des membres ou des domaines.
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Le support est-il inclus ?
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Oui, tous les plans incluent un support par email.
                Les plans Medium et Large bénéficient d'un support prioritaire.
              </Typography>
            </Grid>
          </Grid>

          <Box sx={{ textAlign: 'center', mt: 5 }}>
            <Typography variant="body1" color="text.secondary" gutterBottom>
              Vous avez d'autres questions ?
            </Typography>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/contact')}
              sx={{ mt: 2 }}
            >
              Contactez-nous
            </Button>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default PricingV3;
