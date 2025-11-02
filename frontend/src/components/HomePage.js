import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  CardMedia,
  Avatar,
  Chip,
  Stack,
  Paper,
  alpha,
  useTheme,
  Divider,
  Rating
} from '@mui/material';
import { 
  TrendingUp, 
  People, 
  ShoppingBag, 
  Star,
  ArrowForward,
  Verified,
  AttachMoney,
  Speed,
  Security,
  PlayArrow,
  East,
  LocalOffer,
  Campaign,
  Rocket
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/products')
      .then(res => res.json())
      .then(data => {
        setProducts(data.slice(0, 6));
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading products:', err);
        setLoading(false);
      });
  }, []);

  const stats = [
    { icon: <ShoppingBag />, value: '10K+', label: 'Produits', color: '#667eea' },
    { icon: <People />, value: '5K+', label: 'Influenceurs', color: '#f093fb' },
    { icon: <AttachMoney />, value: '€2M+', label: 'Revenus générés', color: '#4facfe' },
    { icon: <Star />, value: '4.9/5', label: 'Satisfaction', color: '#43e97b' }
  ];

  const features = [
    {
      icon: <Speed />,
      title: 'Rapide et Efficace',
      description: 'Configuration en 5 minutes, premiers revenus dès la première semaine',
      color: '#667eea'
    },
    {
      icon: <Security />,
      title: 'Sécurisé et Fiable',
      description: 'Paiements sécurisés, protection des données, support 24/7',
      color: '#f093fb'
    },
    {
      icon: <TrendingUp />,
      title: 'Analytics Avancés',
      description: 'Tableaux de bord en temps réel, insights détaillés, optimisation IA',
      color: '#4facfe'
    },
    {
      icon: <Verified />,
      title: 'Influenceurs Vérifiés',
      description: 'Profils authentiques, audiences réelles, performances garanties',
      color: '#43e97b'
    }
  ];

  const testimonials = [
    {
      name: 'Sophie Martin',
      role: 'Influenceuse Mode • 250K abonnés',
      avatar: 'SM',
      rating: 5,
      comment: 'ShareYourSales a transformé ma façon de monétiser mon contenu. Interface intuitive, paiements rapides!'
    },
    {
      name: 'Thomas Dubois',
      role: 'E-commerce Manager',
      avatar: 'TD',
      rating: 5,
      comment: 'ROI incroyable! Nos ventes ont augmenté de 300% grâce aux collaborations avec des influenceurs qualifiés.'
    },
    {
      name: 'Marie Lambert',
      role: 'Créatrice de contenu',
      avatar: 'ML',
      rating: 5,
      comment: 'Plateforme professionnelle avec des marques de qualité. Je recommande à tous les créateurs!'
    }
  ];

  const topInfluencers = [
    {
      name: 'Sarah Johnson',
      followers: '500K',
      avatar: 'SJ',
      niche: 'Tech & Lifestyle',
      sales: '€45K',
      growth: '+125%'
    },
    {
      name: 'Marc Dubois',
      followers: '350K',
      avatar: 'MD',
      niche: 'Mode & Beauty',
      sales: '€38K',
      growth: '+98%'
    },
    {
      name: 'Emma Wilson',
      followers: '420K',
      avatar: 'EW',
      niche: 'Fitness',
      sales: '€52K',
      growth: '+156%'
    }
  ];

  return (
    <Box sx={{ bgcolor: 'background.default' }}>
      {/* Hero Section - Premium Design */}
      <Box
        sx={{
          position: 'relative',
          background: `linear-gradient(135deg, ${alpha('#667eea', 0.95)} 0%, ${alpha('#764ba2', 0.95)} 100%)`,
          color: 'white',
          py: { xs: 8, md: 15 },
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%)',
          }
        }}
      >
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <Grid container spacing={6} alignItems="center">
            <Grid item xs={12} md={7}>
              <Chip 
                icon={<Star />}
                label="Plateforme #1 en France" 
                sx={{ 
                  bgcolor: alpha('#fff', 0.2), 
                  color: 'white',
                  fontWeight: 600,
                  mb: 3,
                  backdropFilter: 'blur(10px)'
                }}
              />
              <Typography 
                variant="h1" 
                sx={{ 
                  fontSize: { xs: '2.5rem', md: '3.5rem' },
                  fontWeight: 800,
                  mb: 3,
                  lineHeight: 1.2,
                  textShadow: '0 2px 20px rgba(0,0,0,0.1)'
                }}
              >
                Transformez votre Influence en Revenus
              </Typography>
              <Typography 
                variant="h5" 
                sx={{ 
                  mb: 4, 
                  opacity: 0.95,
                  fontWeight: 400,
                  lineHeight: 1.6
                }}
              >
                La plateforme d'affiliation nouvelle génération qui connecte marques et créateurs de contenu pour des collaborations authentiques et rentables
              </Typography>
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <Button 
                  variant="contained" 
                  size="large"
                  endIcon={<East />}
                  onClick={() => navigate('/register')}
                  sx={{ 
                    bgcolor: 'white', 
                    color: 'primary.main',
                    py: 2,
                    px: 4,
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
                    '&:hover': { 
                      bgcolor: 'grey.100',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 12px 48px rgba(0,0,0,0.3)'
                    },
                    transition: 'all 0.3s'
                  }}
                >
                  Commencer Gratuitement
                </Button>
                <Button 
                  variant="outlined" 
                  size="large"
                  startIcon={<PlayArrow />}
                  sx={{ 
                    borderColor: 'white', 
                    color: 'white',
                    py: 2,
                    px: 4,
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    borderWidth: 2,
                    '&:hover': { 
                      borderColor: 'white',
                      borderWidth: 2,
                      bgcolor: alpha('#fff', 0.1),
                      transform: 'translateY(-2px)'
                    },
                    transition: 'all 0.3s'
                  }}
                >
                  Voir la Démo
                </Button>
              </Stack>
              <Stack direction="row" spacing={4} sx={{ mt: 4 }}>
                <Box>
                  <Typography variant="h4" fontWeight="bold">10K+</Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Utilisateurs actifs</Typography>
                </Box>
                <Box>
                  <Typography variant="h4" fontWeight="bold">€2M+</Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Revenus générés</Typography>
                </Box>
                <Box>
                  <Typography variant="h4" fontWeight="bold">4.9/5</Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Note moyenne</Typography>
                </Box>
              </Stack>
            </Grid>
            <Grid item xs={12} md={5} sx={{ display: { xs: 'none', md: 'block' } }}>
              <Box
                sx={{
                  position: 'relative'
                }}
              >
                <Paper
                  elevation={24}
                  sx={{
                    p: 3,
                    bgcolor: alpha('#fff', 0.95),
                    backdropFilter: 'blur(20px)',
                    borderRadius: 4
                  }}
                >
                  <Stack spacing={2}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ bgcolor: 'success.main' }}><TrendingUp /></Avatar>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Ventes du mois</Typography>
                        <Typography variant="h5" fontWeight="bold" color="success.main">+€15,247</Typography>
                      </Box>
                    </Box>
                    <Divider />
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ bgcolor: 'primary.main' }}><Campaign /></Avatar>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Campagnes actives</Typography>
                        <Typography variant="h5" fontWeight="bold">32</Typography>
                      </Box>
                    </Box>
                  </Stack>
                </Paper>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Stats Section - Floating Cards */}
      <Container maxWidth="lg" sx={{ mt: { xs: 4, md: -8 }, position: 'relative', zIndex: 2 }}>
        <Grid container spacing={3}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Paper 
                elevation={8}
                sx={{ 
                  p: 4,
                  textAlign: 'center',
                  borderRadius: 3,
                  background: `linear-gradient(135deg, ${alpha(stat.color, 0.1)} 0%, ${alpha(stat.color, 0.05)} 100%)`,
                  border: `1px solid ${alpha(stat.color, 0.2)}`,
                  transition: 'all 0.3s',
                  '&:hover': { 
                    transform: 'translateY(-8px)',
                    boxShadow: `0 20px 40px ${alpha(stat.color, 0.3)}`
                  }
                }}
              >
                <Box 
                  sx={{ 
                    color: stat.color, 
                    mb: 2,
                    display: 'inline-flex',
                    p: 2,
                    borderRadius: 2,
                    bgcolor: alpha(stat.color, 0.1)
                  }}
                >
                  {React.cloneElement(stat.icon, { sx: { fontSize: 40 } })}
                </Box>
                <Typography variant="h3" fontWeight="800" sx={{ mb: 1 }}>
                  {stat.value}
                </Typography>
                <Typography variant="body1" color="text.secondary" fontWeight={500}>
                  {stat.label}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ mt: 12 }}>
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography 
            variant="h2" 
            fontWeight="800" 
            gutterBottom
            sx={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 2
            }}
          >
            Pourquoi ShareYourSales ?
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
            Une plateforme complète pensée pour maximiser vos revenus et simplifier vos collaborations
          </Typography>
        </Box>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Paper
                elevation={0}
                sx={{
                  p: 4,
                  height: '100%',
                  borderRadius: 3,
                  border: '1px solid',
                  borderColor: 'divider',
                  transition: 'all 0.3s',
                  '&:hover': {
                    borderColor: feature.color,
                    transform: 'translateY(-4px)',
                    boxShadow: `0 12px 24px ${alpha(feature.color, 0.15)}`
                  }
                }}
              >
                <Box
                  sx={{
                    display: 'inline-flex',
                    p: 2,
                    borderRadius: 2,
                    bgcolor: alpha(feature.color, 0.1),
                    color: feature.color,
                    mb: 3
                  }}
                >
                  {React.cloneElement(feature.icon, { sx: { fontSize: 32 } })}
                </Box>
                <Typography variant="h6" fontWeight="700" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" lineHeight={1.7}>
                  {feature.description}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Products Section */}
      <Container maxWidth="lg" sx={{ mt: 12 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 6 }}>
          <Box>
            <Typography variant="h3" fontWeight="800" gutterBottom>
              Produits Populaires
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Découvrez les produits les plus performants du moment
            </Typography>
          </Box>
          <Button 
            endIcon={<ArrowForward />}
            onClick={() => navigate('/marketplace')}
            sx={{ display: { xs: 'none', sm: 'flex' } }}
          >
            Voir tout
          </Button>
        </Box>
        <Grid container spacing={3}>
          {products.map((product) => (
            <Grid item xs={12} sm={6} md={4} key={product.id}>
              <Card 
                sx={{ 
                  height: '100%',
                  borderRadius: 3,
                  overflow: 'hidden',
                  transition: 'all 0.3s',
                  border: '1px solid',
                  borderColor: 'divider',
                  '&:hover': { 
                    transform: 'translateY(-8px)',
                    boxShadow: 12,
                    borderColor: 'primary.main'
                  }
                }}
              >
                <Box sx={{ position: 'relative' }}>
                  <CardMedia
                    component="img"
                    height="220"
                    image={product.image_url || 'https://via.placeholder.com/400x300'}
                    alt={product.name}
                    sx={{ objectFit: 'cover' }}
                  />
                  <Chip 
                    icon={<LocalOffer />}
                    label={`${product.commission_rate}% commission`}
                    size="small"
                    color="success"
                    sx={{ 
                      position: 'absolute', 
                      top: 12, 
                      right: 12,
                      fontWeight: 600
                    }}
                  />
                </Box>
                <CardContent>
                  <Typography variant="overline" color="text.secondary" fontWeight={600}>
                    {product.category}
                  </Typography>
                  <Typography variant="h6" fontWeight="700" gutterBottom>
                    {product.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }} noWrap>
                    {product.description}
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h5" color="primary" fontWeight="800">
                      €{product.price}
                    </Typography>
                    <Button 
                      size="small" 
                      variant="contained"
                      endIcon={<East />}
                      sx={{ borderRadius: 2 }}
                    >
                      Promouvoir
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Top Influencers */}
      <Container maxWidth="lg" sx={{ mt: 12 }}>
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="h3" fontWeight="800" gutterBottom>
            Influenceurs Partenaires
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Rejoignez une communauté de créateurs à succès
          </Typography>
        </Box>
        <Grid container spacing={4}>
          {topInfluencers.map((influencer, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Paper 
                elevation={3}
                sx={{ 
                  p: 4,
                  textAlign: 'center',
                  borderRadius: 3,
                  transition: 'all 0.3s',
                  '&:hover': { 
                    transform: 'translateY(-8px)',
                    boxShadow: 8
                  }
                }}
              >
                <Avatar
                  sx={{ 
                    width: 100, 
                    height: 100, 
                    mx: 'auto', 
                    mb: 2,
                    fontSize: '2rem',
                    fontWeight: 700,
                    bgcolor: 'primary.main'
                  }}
                >
                  {influencer.avatar}
                </Avatar>
                <Stack direction="row" spacing={0.5} justifyContent="center" sx={{ mb: 1 }}>
                  <Typography variant="h6" fontWeight="700">
                    {influencer.name}
                  </Typography>
                  <Verified color="primary" sx={{ fontSize: 20 }} />
                </Stack>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {influencer.niche}
                </Typography>
                <Stack direction="row" spacing={2} justifyContent="center" sx={{ mt: 3 }}>
                  <Box>
                    <Typography variant="h6" fontWeight="700" color="primary">
                      {influencer.followers}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Abonnés
                    </Typography>
                  </Box>
                  <Divider orientation="vertical" flexItem />
                  <Box>
                    <Typography variant="h6" fontWeight="700" color="success.main">
                      {influencer.sales}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Ventes/mois
                    </Typography>
                  </Box>
                </Stack>
                <Chip 
                  icon={<TrendingUp />}
                  label={`${influencer.growth} ce mois`}
                  color="success"
                  size="small"
                  sx={{ mt: 2 }}
                />
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Testimonials */}
      <Container maxWidth="lg" sx={{ mt: 12 }}>
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="h3" fontWeight="800" gutterBottom>
            Ils Nous Font Confiance
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Des milliers d'utilisateurs satisfaits partagent leur expérience
          </Typography>
        </Box>
        <Grid container spacing={4}>
          {testimonials.map((testimonial, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Paper
                elevation={3}
                sx={{
                  p: 4,
                  height: '100%',
                  borderRadius: 3,
                  position: 'relative',
                  '&::before': {
                    content: '"""',
                    position: 'absolute',
                    top: 20,
                    left: 20,
                    fontSize: '4rem',
                    color: alpha(theme.palette.primary.main, 0.1),
                    fontFamily: 'Georgia, serif',
                    lineHeight: 0
                  }
                }}
              >
                <Rating value={testimonial.rating} readOnly sx={{ mb: 2 }} />
                <Typography variant="body1" sx={{ mb: 3, lineHeight: 1.8 }}>
                  "{testimonial.comment}"
                </Typography>
                <Stack direction="row" spacing={2} alignItems="center">
                  <Avatar sx={{ bgcolor: 'primary.main', fontWeight: 700 }}>
                    {testimonial.avatar}
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle1" fontWeight="700">
                      {testimonial.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {testimonial.role}
                    </Typography>
                  </Box>
                </Stack>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box sx={{ mt: 12 }}>
        <Container maxWidth="md">
          <Paper
            elevation={12}
            sx={{
              p: { xs: 6, md: 8 },
              borderRadius: 4,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              textAlign: 'center',
              position: 'relative',
              overflow: 'hidden',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: -100,
                right: -100,
                width: 300,
                height: 300,
                borderRadius: '50%',
                background: alpha('#fff', 0.1)
              }
            }}
          >
            <Typography variant="h2" fontWeight="800" gutterBottom sx={{ position: 'relative' }}>
              Prêt à Décoller ?
            </Typography>
            <Typography variant="h6" sx={{ mb: 4, opacity: 0.95, position: 'relative' }}>
              Rejoignez +10,000 marques et influenceurs qui génèrent des revenus sur ShareYourSales
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center" sx={{ position: 'relative' }}>
              <Button 
                variant="contained" 
                size="large"
                endIcon={<Rocket />}
                onClick={() => navigate('/register')}
                sx={{ 
                  bgcolor: 'white', 
                  color: 'primary.main',
                  py: 2,
                  px: 5,
                  fontSize: '1.1rem',
                  fontWeight: 700,
                  boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
                  '&:hover': { 
                    bgcolor: 'grey.100',
                    transform: 'translateY(-2px)'
                  }
                }}
              >
                Commencer Maintenant
              </Button>
              <Button 
                variant="outlined"
                size="large"
                onClick={() => navigate('/pricing')}
                sx={{ 
                  borderColor: 'white',
                  color: 'white',
                  py: 2,
                  px: 5,
                  fontSize: '1.1rem',
                  fontWeight: 700,
                  borderWidth: 2,
                  '&:hover': { 
                    borderColor: 'white',
                    borderWidth: 2,
                    bgcolor: alpha('#fff', 0.1)
                  }
                }}
              >
                Voir les Tarifs
              </Button>
            </Stack>
            <Typography variant="caption" sx={{ display: 'block', mt: 3, opacity: 0.8, position: 'relative' }}>
              ✨ Aucune carte bancaire requise • Configuration en 2 minutes
            </Typography>
          </Paper>
        </Container>
      </Box>

      <Box sx={{ py: 8 }} />
    </Box>
  );
};

export default HomePage;
