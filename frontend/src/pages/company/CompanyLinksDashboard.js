import React, { useState, useEffect } from 'react';
import { useToast } from '../../context/ToastContext';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Tooltip,
  Tabs,
  Tab,
  InputAdornment
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import LinkIcon from '@mui/icons-material/Link';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import QrCodeIcon from '@mui/icons-material/QrCode';
import ShareIcon from '@mui/icons-material/Share';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import api from '../../services/api';

/**
 * Company Links Dashboard - Génération et attribution de liens
 *
 * WORKFLOW CONFORME:
 * 1. Entreprise génère des liens pour ses produits
 * 2. Entreprise attribue ces liens à des membres d'équipe
 * 3. Membres reçoivent les liens et peuvent les promouvoir
 *
 * Fonctionnalités:
 * - Génération de liens pour produits
 * - Attribution aux membres
 * - Suivi des performances par lien/membre
 * - Désactivation de liens
 */

const CompanyLinksDashboard = () => {
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [links, setLinks] = useState([]);
  const [products, setProducts] = useState([]);
  const [teamMembers, setTeamMembers] = useState([]);
  const [error, setError] = useState(null);
  const [currentTab, setCurrentTab] = useState(0); // 0: All, 1: Unassigned, 2: Assigned

  // Dialogs
  const [generateDialogOpen, setGenerateDialogOpen] = useState(false);
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [selectedLink, setSelectedLink] = useState(null);

  // Forms
  const [generateForm, setGenerateForm] = useState({
    product_id: '',
    custom_slug: '',
    commission_rate: '',
    notes: ''
  });

  const [assignForm, setAssignForm] = useState({
    link_id: '',
    member_id: '',
    custom_commission_rate: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [linksRes, productsRes, membersRes] = await Promise.all([
        api.get('/api/company/links/my-company-links'),
        api.get('/api/products/my-products'),
        api.get('/api/team/members', { params: { status_filter: 'active' } })
      ]);

      setLinks(linksRes.data.links || []);
      setProducts(productsRes.data || []);
      setTeamMembers(membersRes.data || []);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateLink = async () => {
    try {
      await api.post('/api/company/links/generate', generateForm);
      toast.success('Lien généré avec succès');
      setGenerateDialogOpen(false);
      setGenerateForm({
        product_id: '',
        custom_slug: '',
        commission_rate: '',
        notes: ''
      });
      fetchData();
    } catch (err) {
      console.error('Error generating link:', err);
      toast.error(err.response?.data?.detail || 'Erreur lors de la génération');
    }
  };

  const handleAssignLink = async () => {
    try {
      await api.post('/api/company/links/assign', assignForm);
      toast.success('Lien attribué avec succès');
      setAssignDialogOpen(false);
      setAssignForm({
        link_id: '',
        member_id: '',
        custom_commission_rate: ''
      });
      fetchData();
    } catch (err) {
      console.error('Error assigning link:', err);
      toast.error(err.response?.data?.detail || 'Erreur lors de l\'attribution');
    }
  };

  const handleCopyLink = (url) => {
    navigator.clipboard.writeText(url);
    toast.success('Lien copié dans le presse-papier');
  };

  const handleDeactivateLink = async (linkId) => {
    if (!window.confirm('Désactiver ce lien ? Il ne pourra plus être utilisé.')) {
      return;
    }

    try {
      await api.delete(`/api/company/links/${linkId}`);
      toast.success('Lien désactivé');
      fetchData();
    } catch (err) {
      console.error('Error deactivating link:', err);
      toast.error('Erreur lors de la désactivation');
    }
  };

  const getFilteredLinks = () => {
    if (currentTab === 1) {
      // Unassigned
      return links.filter(link => !link.influencer_id);
    } else if (currentTab === 2) {
      // Assigned
      return links.filter(link => link.influencer_id);
    }
    // All
    return links;
  };

  const filteredLinks = getFilteredLinks();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Gestion des liens d'affiliation
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Générez des liens et attribuez-les à vos membres
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setGenerateDialogOpen(true)}
          size="large"
        >
          Générer un lien
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2" fontWeight="600" gutterBottom>
          Comment ça marche ?
        </Typography>
        <Typography variant="body2">
          1. Générez des liens pour vos produits<br />
          2. Attribuez ces liens à vos commerciaux ou influenceurs<br />
          3. Ils reçoivent les liens et peuvent les partager<br />
          4. Suivez les performances de chaque membre
        </Typography>
      </Alert>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Total liens
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {links.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Non attribués
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="warning.main">
                {links.filter(l => !l.influencer_id).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Attribués
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                {links.filter(l => l.influencer_id).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={(e, newValue) => setCurrentTab(newValue)}>
          <Tab label={`Tous (${links.length})`} />
          <Tab label={`Non attribués (${links.filter(l => !l.influencer_id).length})`} />
          <Tab label={`Attribués (${links.filter(l => l.influencer_id).length})`} />
        </Tabs>
      </Box>

      {/* Links Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Produit</TableCell>
                <TableCell>Lien court</TableCell>
                <TableCell>Commission</TableCell>
                <TableCell>Attribué à</TableCell>
                <TableCell>Clics</TableCell>
                <TableCell>Ventes</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredLinks.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                      {currentTab === 0
                        ? 'Aucun lien. Commencez par générer un lien pour l\'un de vos produits.'
                        : currentTab === 1
                        ? 'Tous vos liens ont été attribués.'
                        : 'Aucun lien attribué pour le moment.'}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredLinks.map((link) => (
                  <TableRow key={link.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="600">
                        {link.product?.name || 'Produit'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {link.product?.price} MAD
                      </Typography>
                    </TableCell>

                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip
                          label={link.short_code}
                          size="small"
                          color="primary"
                          icon={<LinkIcon />}
                        />
                        <Tooltip title="Copier le lien">
                          <IconButton
                            size="small"
                            onClick={() => handleCopyLink(link.full_url)}
                          >
                            <ContentCopyIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>

                    <TableCell>
                      <Typography variant="body2" color="success.main" fontWeight="600">
                        {link.commission_rate}%
                      </Typography>
                    </TableCell>

                    <TableCell>
                      {link.member ? (
                        <Chip
                          label={`${link.member.first_name} ${link.member.last_name}`}
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      ) : (
                        <Chip
                          label="Non attribué"
                          size="small"
                          color="warning"
                          variant="outlined"
                        />
                      )}
                    </TableCell>

                    <TableCell>
                      <Typography variant="body2">
                        {link.clicks || 0}
                      </Typography>
                    </TableCell>

                    <TableCell>
                      <Typography variant="body2">
                        {link.conversions || 0}
                      </Typography>
                    </TableCell>

                    <TableCell align="right">
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                        {!link.influencer_id && (
                          <Tooltip title="Attribuer à un membre">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => {
                                setAssignForm({
                                  ...assignForm,
                                  link_id: link.id
                                });
                                setAssignDialogOpen(true);
                              }}
                            >
                              <PersonAddIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}

                        <Tooltip title="QR Code">
                          <IconButton
                            size="small"
                            onClick={() => window.open(link.qr_code_url, '_blank')}
                          >
                            <QrCodeIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>

                        <Tooltip title="Désactiver">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeactivateLink(link.id)}
                          >
                            <VisibilityOffIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Generate Link Dialog */}
      <Dialog open={generateDialogOpen} onClose={() => setGenerateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Générer un lien d'affiliation</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <FormControl fullWidth required>
              <InputLabel>Produit</InputLabel>
              <Select
                value={generateForm.product_id}
                onChange={(e) => setGenerateForm({ ...generateForm, product_id: e.target.value })}
                label="Produit"
              >
                {products.map((product) => (
                  <MenuItem key={product.id} value={product.id}>
                    {product.name} - {product.price} MAD
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="Slug personnalisé (optionnel)"
              fullWidth
              value={generateForm.custom_slug}
              onChange={(e) => setGenerateForm({ ...generateForm, custom_slug: e.target.value })}
              helperText="Laissez vide pour un code automatique"
            />

            <TextField
              label="Taux de commission personnalisé (%)"
              type="number"
              fullWidth
              value={generateForm.commission_rate}
              onChange={(e) => setGenerateForm({ ...generateForm, commission_rate: e.target.value })}
              inputProps={{ min: 0, max: 100 }}
              helperText="Laissez vide pour utiliser le taux par défaut du produit"
            />

            <TextField
              label="Notes (optionnel)"
              multiline
              rows={3}
              fullWidth
              value={generateForm.notes}
              onChange={(e) => setGenerateForm({ ...generateForm, notes: e.target.value })}
            />

            <Alert severity="info">
              Ce lien sera généré mais non attribué. Vous pourrez l'attribuer à un membre ensuite.
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGenerateDialogOpen(false)}>
            Annuler
          </Button>
          <Button
            onClick={handleGenerateLink}
            variant="contained"
            disabled={!generateForm.product_id}
          >
            Générer le lien
          </Button>
        </DialogActions>
      </Dialog>

      {/* Assign Link Dialog */}
      <Dialog open={assignDialogOpen} onClose={() => setAssignDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Attribuer le lien à un membre</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <FormControl fullWidth required>
              <InputLabel>Membre de l'équipe</InputLabel>
              <Select
                value={assignForm.member_id}
                onChange={(e) => setAssignForm({ ...assignForm, member_id: e.target.value })}
                label="Membre de l'équipe"
              >
                {teamMembers.map((member) => (
                  <MenuItem key={member.member_id} value={member.member_id}>
                    {member.member_first_name} {member.member_last_name} - {member.team_role}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="Commission personnalisée pour ce membre (%)"
              type="number"
              fullWidth
              value={assignForm.custom_commission_rate}
              onChange={(e) => setAssignForm({ ...assignForm, custom_commission_rate: e.target.value })}
              inputProps={{ min: 0, max: 100 }}
              helperText="Optionnel - Permet de définir un taux différent pour ce membre"
            />

            <Alert severity="info">
              Un nouveau lien unique sera créé pour ce membre. Il pourra le partager et gagner des commissions sur les ventes générées.
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignDialogOpen(false)}>
            Annuler
          </Button>
          <Button
            onClick={handleAssignLink}
            variant="contained"
            disabled={!assignForm.member_id}
          >
            Attribuer
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CompanyLinksDashboard;
