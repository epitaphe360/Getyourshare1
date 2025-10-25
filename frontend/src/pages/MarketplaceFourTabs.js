import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Tabs,
  Tab,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Button,
  TextField,
  InputAdornment,
  Chip,
  Avatar,
  Rating,
  IconButton,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import WorkIcon from '@mui/icons-material/Work';
import PeopleIcon from '@mui/icons-material/People';
import StarIcon from '@mui/icons-material/Star';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import InstagramIcon from '@mui/icons-material/Instagram';
import FacebookIcon from '@mui/icons-material/Facebook';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

/**
 * Marketplace 4 Tabs - Conforme aux spécifications
 *
 * Tab 1: Produits (biens physiques)
 * Tab 2: Services (offres immatérielles)
 * Tab 3: Annuaire Commerciaux
 * Tab 4: Annuaire Influenceurs
 */

const MarketplaceFourTabs = () => {
  const navigate = useNavigate();
  const [currentTab, setCurrentTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Products/Services state
  const [products, setProducts] = useState([]);
  const [services, setServices] = useState([]);

  // Commercials state
  const [commercials, setCommercials] = useState([]);
  const [commercialFilters, setCommercialFilters] = useState({
    specialty: '',
    city: '',
    availability_type: ''
  });

  // Influencers state
  const [influencers, setInfluencers] = useState([]);
  const [influencerFilters, setInfluencerFilters] = useState({
    niche: '',
    platform: '',
    min_followers: ''
  });

  useEffect(() => {
    loadTabData();
  }, [currentTab]);

  const loadTabData = async () => {
    setLoading(true);
    setError(null);

    try {
      if (currentTab === 0) {
        await fetchProducts();
      } else if (currentTab === 1) {
        await fetchServices();
      } else if (currentTab === 2) {
        await fetchCommercials();
      } else if (currentTab === 3) {
        await fetchInfluencers();
      }
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  // ============================================
  // TAB 1: PRODUCTS
  // ============================================

  const fetchProducts = async () => {
    try {
      const params = {
        search: searchQuery || undefined,
        type: 'product',
        limit: 20
      };
      const response = await api.get('/api/marketplace/products', { params });
      setProducts(response.data.products || []);
    } catch (err) {
      console.error('Error fetching products:', err);
    }
  };

  const renderProducts = () => (
    <Grid container spacing={3}>
      {products.map((product) => (
        <Grid item xs={12} sm={6} md={4} key={product.id}>
          <Card
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              '&:hover': { boxShadow: 6 }
            }}
          >
            {product.images && product.images.length > 0 && (
              <CardMedia
                component="img"
                height="200"
                image={product.images[0]}
                alt={product.name}
              />
            )}
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="h6" gutterBottom>
                {product.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" noWrap>
                {product.description}
              </Typography>
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" color="primary">
                  {product.price} {product.currency || 'MAD'}
                </Typography>
                {product.discount_percentage > 0 && (
                  <Chip
                    label={`-${product.discount_percentage}%`}
                    color="error"
                    size="small"
                  />
                )}
              </Box>
              <Typography variant="caption" color="success.main">
                Commission: {product.commission_rate}%
              </Typography>
            </CardContent>
            <CardActions>
              <Button
                fullWidth
                variant="contained"
                startIcon={<ShoppingCartIcon />}
                onClick={() => navigate(`/marketplace/product/${product.id}`)}
              >
                Voir détails
              </Button>
            </CardActions>
          </Card>
        </Grid>
      ))}
      {products.length === 0 && (
        <Grid item xs={12}>
          <Alert severity="info">Aucun produit trouvé</Alert>
        </Grid>
      )}
    </Grid>
  );

  // ============================================
  // TAB 2: SERVICES
  // ============================================

  const fetchServices = async () => {
    try {
      const params = {
        search: searchQuery || undefined,
        type: 'service',
        limit: 20
      };
      const response = await api.get('/api/marketplace/products', { params });
      setServices(response.data.products || []);
    } catch (err) {
      console.error('Error fetching services:', err);
    }
  };

  const renderServices = () => (
    <Grid container spacing={3}>
      {services.map((service) => (
        <Grid item xs={12} sm={6} md={4} key={service.id}>
          <Card
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              '&:hover': { boxShadow: 6 }
            }}
          >
            {service.images && service.images.length > 0 && (
              <CardMedia
                component="img"
                height="200"
                image={service.images[0]}
                alt={service.name}
              />
            )}
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="h6" gutterBottom>
                {service.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {service.description}
              </Typography>
              {service.service_duration && (
                <Chip
                  label={`Durée: ${service.service_duration} min`}
                  size="small"
                  sx={{ mb: 1, mr: 1 }}
                />
              )}
              {service.service_delivery && (
                <Chip
                  label={service.service_delivery}
                  size="small"
                  color="secondary"
                  sx={{ mb: 1 }}
                />
              )}
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" color="primary">
                  {service.price} {service.currency || 'MAD'}
                </Typography>
              </Box>
              <Typography variant="caption" color="success.main">
                Commission: {service.commission_rate}%
              </Typography>
            </CardContent>
            <CardActions>
              <Button
                fullWidth
                variant="contained"
                startIcon={<WorkIcon />}
                onClick={() => navigate(`/marketplace/product/${service.id}`)}
              >
                Voir détails
              </Button>
            </CardActions>
          </Card>
        </Grid>
      ))}
      {services.length === 0 && (
        <Grid item xs={12}>
          <Alert severity="info">Aucun service trouvé</Alert>
        </Grid>
      )}
    </Grid>
  );

  // ============================================
  // TAB 3: COMMERCIALS DIRECTORY
  // ============================================

  const fetchCommercials = async () => {
    try {
      const params = {
        search: searchQuery || undefined,
        specialty: commercialFilters.specialty || undefined,
        city: commercialFilters.city || undefined,
        availability_type: commercialFilters.availability_type || undefined,
        limit: 20
      };
      const response = await api.get('/api/commercials/directory', { params });
      setCommercials(response.data.commercials || []);
    } catch (err) {
      console.error('Error fetching commercials:', err);
    }
  };

  const renderCommercials = () => (
    <>
      {/* Filters */}
      <Box sx={{ mb: 4, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Spécialité</InputLabel>
          <Select
            value={commercialFilters.specialty}
            onChange={(e) => setCommercialFilters({ ...commercialFilters, specialty: e.target.value })}
            label="Spécialité"
          >
            <MenuItem value="">Toutes</MenuItem>
            <MenuItem value="Tech">Tech</MenuItem>
            <MenuItem value="Finance">Finance</MenuItem>
            <MenuItem value="Retail">Retail</MenuItem>
            <MenuItem value="B2B">B2B</MenuItem>
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Disponibilité</InputLabel>
          <Select
            value={commercialFilters.availability_type}
            onChange={(e) => setCommercialFilters({ ...commercialFilters, availability_type: e.target.value })}
            label="Disponibilité"
          >
            <MenuItem value="">Toutes</MenuItem>
            <MenuItem value="full_time">Temps plein</MenuItem>
            <MenuItem value="part_time">Temps partiel</MenuItem>
            <MenuItem value="freelance">Freelance</MenuItem>
          </Select>
        </FormControl>

        <Button variant="contained" onClick={fetchCommercials}>
          Appliquer les filtres
        </Button>
      </Box>

      <Grid container spacing={3}>
        {commercials.map((commercial) => (
          <Grid item xs={12} sm={6} md={4} key={commercial.user_id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                '&:hover': { boxShadow: 6 }
              }}
            >
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <Avatar
                  src={commercial.profile_picture}
                  sx={{ width: 80, height: 80, mx: 'auto', mb: 2 }}
                >
                  {commercial.first_name?.[0]}
                </Avatar>
                <Typography variant="h6" gutterBottom>
                  {commercial.first_name} {commercial.last_name}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {commercial.headline}
                </Typography>
                {commercial.city && (
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 1 }}>
                    <LocationOnIcon fontSize="small" sx={{ mr: 0.5 }} />
                    <Typography variant="caption">{commercial.city}</Typography>
                  </Box>
                )}
              </Box>

              <CardContent sx={{ flexGrow: 1, pt: 0 }}>
                {commercial.specialties && commercial.specialties.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    {commercial.specialties.slice(0, 3).map((spec, idx) => (
                      <Chip key={idx} label={spec} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                    ))}
                  </Box>
                )}

                {commercial.years_of_experience && (
                  <Typography variant="body2" color="text.secondary">
                    {commercial.years_of_experience} ans d'expérience
                  </Typography>
                )}

                {commercial.average_rating > 0 && (
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <Rating value={commercial.average_rating} readOnly size="small" precision={0.1} />
                    <Typography variant="caption" sx={{ ml: 1 }}>
                      ({commercial.review_count} avis)
                    </Typography>
                  </Box>
                )}
              </CardContent>

              <CardActions>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate(`/commercial/${commercial.user_id}`)}
                >
                  Voir profil
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
        {commercials.length === 0 && (
          <Grid item xs={12}>
            <Alert severity="info">Aucun commercial trouvé</Alert>
          </Grid>
        )}
      </Grid>
    </>
  );

  // ============================================
  // TAB 4: INFLUENCERS DIRECTORY
  // ============================================

  const fetchInfluencers = async () => {
    try {
      const params = {
        search: searchQuery || undefined,
        niche: influencerFilters.niche || undefined,
        platform: influencerFilters.platform || undefined,
        min_followers: influencerFilters.min_followers || undefined,
        limit: 20
      };
      const response = await api.get('/api/influencers/directory', { params });
      setInfluencers(response.data.influencers || []);
    } catch (err) {
      console.error('Error fetching influencers:', err);
    }
  };

  const renderInfluencers = () => (
    <>
      {/* Filters */}
      <Box sx={{ mb: 4, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Niche</InputLabel>
          <Select
            value={influencerFilters.niche}
            onChange={(e) => setInfluencerFilters({ ...influencerFilters, niche: e.target.value })}
            label="Niche"
          >
            <MenuItem value="">Toutes</MenuItem>
            <MenuItem value="Fashion">Fashion</MenuItem>
            <MenuItem value="Beauty">Beauty</MenuItem>
            <MenuItem value="Tech">Tech</MenuItem>
            <MenuItem value="Travel">Travel</MenuItem>
            <MenuItem value="Food">Food</MenuItem>
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Plateforme</InputLabel>
          <Select
            value={influencerFilters.platform}
            onChange={(e) => setInfluencerFilters({ ...influencerFilters, platform: e.target.value })}
            label="Plateforme"
          >
            <MenuItem value="">Toutes</MenuItem>
            <MenuItem value="instagram">Instagram</MenuItem>
            <MenuItem value="tiktok">TikTok</MenuItem>
            <MenuItem value="youtube">YouTube</MenuItem>
            <MenuItem value="facebook">Facebook</MenuItem>
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Followers minimum</InputLabel>
          <Select
            value={influencerFilters.min_followers}
            onChange={(e) => setInfluencerFilters({ ...influencerFilters, min_followers: e.target.value })}
            label="Followers minimum"
          >
            <MenuItem value="">Tous</MenuItem>
            <MenuItem value="1000">1K+</MenuItem>
            <MenuItem value="10000">10K+</MenuItem>
            <MenuItem value="50000">50K+</MenuItem>
            <MenuItem value="100000">100K+</MenuItem>
          </Select>
        </FormControl>

        <Button variant="contained" onClick={fetchInfluencers}>
          Appliquer les filtres
        </Button>
      </Box>

      <Grid container spacing={3}>
        {influencers.map((influencer) => (
          <Grid item xs={12} sm={6} md={4} key={influencer.user_id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                '&:hover': { boxShadow: 6 }
              }}
            >
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <Avatar
                  src={influencer.profile_picture}
                  sx={{ width: 80, height: 80, mx: 'auto', mb: 2 }}
                >
                  {influencer.display_name?.[0]}
                </Avatar>
                <Typography variant="h6" gutterBottom>
                  {influencer.display_name}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {influencer.headline}
                </Typography>
              </Box>

              <CardContent sx={{ flexGrow: 1, pt: 0 }}>
                {influencer.niches && influencer.niches.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    {influencer.niches.slice(0, 3).map((niche, idx) => (
                      <Chip key={idx} label={niche} size="small" color="secondary" sx={{ mr: 0.5, mb: 0.5 }} />
                    ))}
                  </Box>
                )}

                <Typography variant="h6" color="primary" gutterBottom>
                  {(influencer.total_followers || 0).toLocaleString()} followers
                </Typography>

                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  {influencer.instagram_followers > 0 && (
                    <Chip
                      icon={<InstagramIcon />}
                      label={`${(influencer.instagram_followers / 1000).toFixed(0)}K`}
                      size="small"
                    />
                  )}
                  {influencer.tiktok_followers > 0 && (
                    <Chip
                      label={`TT ${(influencer.tiktok_followers / 1000).toFixed(0)}K`}
                      size="small"
                    />
                  )}
                </Box>

                {influencer.average_engagement_rate && (
                  <Typography variant="body2" color="success.main">
                    Engagement: {influencer.average_engagement_rate.toFixed(1)}%
                  </Typography>
                )}

                {influencer.average_rating > 0 && (
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <Rating value={influencer.average_rating} readOnly size="small" precision={0.1} />
                    <Typography variant="caption" sx={{ ml: 1 }}>
                      ({influencer.review_count} avis)
                    </Typography>
                  </Box>
                )}
              </CardContent>

              <CardActions>
                <Button
                  fullWidth
                  variant="outlined"
                  color="secondary"
                  onClick={() => navigate(`/influencer/${influencer.user_id}`)}
                >
                  Voir profil
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
        {influencers.length === 0 && (
          <Grid item xs={12}>
            <Alert severity="info">Aucun influenceur trouvé</Alert>
          </Grid>
        )}
      </Grid>
    </>
  );

  // ============================================
  // MAIN RENDER
  // ============================================

  const handleSearch = (e) => {
    e.preventDefault();
    loadTabData();
  };

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
      <Container maxWidth="lg">
        {/* Header */}
        <Typography variant="h3" component="h1" gutterBottom fontWeight="bold" align="center">
          Marketplace Share Your Sales
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
          Découvrez nos produits, services, et collaborez avec des professionnels
        </Typography>

        {/* Search Bar */}
        <Box component="form" onSubmit={handleSearch} sx={{ mb: 4 }}>
          <TextField
            fullWidth
            placeholder="Rechercher..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: (
                <Button type="submit" variant="contained">
                  Rechercher
                </Button>
              )
            }}
          />
        </Box>

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 4 }}>
          <Tabs
            value={currentTab}
            onChange={(e, newValue) => setCurrentTab(newValue)}
            variant="fullWidth"
            sx={{
              '& .MuiTab-root': {
                fontWeight: 600,
                fontSize: '1rem'
              }
            }}
          >
            <Tab
              icon={<ShoppingCartIcon />}
              iconPosition="start"
              label="Produits"
            />
            <Tab
              icon={<WorkIcon />}
              iconPosition="start"
              label="Services"
            />
            <Tab
              icon={<PeopleIcon />}
              iconPosition="start"
              label="Commerciaux"
            />
            <Tab
              icon={<StarIcon />}
              iconPosition="start"
              label="Influenceurs"
            />
          </Tabs>
        </Box>

        {/* Tab Content */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress size={60} />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 4 }}>
            {error}
          </Alert>
        ) : (
          <>
            {currentTab === 0 && renderProducts()}
            {currentTab === 1 && renderServices()}
            {currentTab === 2 && renderCommercials()}
            {currentTab === 3 && renderInfluencers()}
          </>
        )}
      </Container>
    </Box>
  );
};

export default MarketplaceFourTabs;
