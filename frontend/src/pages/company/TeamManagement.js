import React, { useState, useEffect } from 'react';
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
  Avatar,
  Box as MuiBox
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import EmailIcon from '@mui/icons-material/Email';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import PeopleIcon from '@mui/icons-material/People';
import api from '../../services/api';

/**
 * Team Management - Gestion de l'équipe entreprise
 *
 * Fonctionnalités:
 * - Inviter des commerciaux/influenceurs
 * - Gérer les permissions
 * - Voir les membres actifs et en attente
 * - Retirer des membres
 * - Renvoyer des invitations
 */

const TeamManagement = () => {
  const [loading, setLoading] = useState(true);
  const [members, setMembers] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState(null);

  // Invite form state
  const [inviteForm, setInviteForm] = useState({
    email: '',
    team_role: 'commercial',
    can_view_all_sales: false,
    can_manage_products: false,
    custom_commission_rate: '',
    notes: ''
  });

  useEffect(() => {
    fetchTeamData();
  }, []);

  const fetchTeamData = async () => {
    try {
      const [membersResponse, statsResponse] = await Promise.all([
        api.get('/api/team/members'),
        api.get('/api/team/stats')
      ]);

      setMembers(membersResponse.data);
      setStats(statsResponse.data);
    } catch (err) {
      console.error('Error fetching team data:', err);
      setError('Erreur lors du chargement de l\'équipe');
    } finally {
      setLoading(false);
    }
  };

  const handleInviteMember = async () => {
    try {
      await api.post('/api/team/invite', inviteForm);
      alert('Invitation envoyée avec succès');
      setInviteDialogOpen(false);
      setInviteForm({
        email: '',
        team_role: 'commercial',
        can_view_all_sales: false,
        can_manage_products: false,
        custom_commission_rate: '',
        notes: ''
      });
      fetchTeamData();
    } catch (err) {
      console.error('Error inviting member:', err);
      alert(err.response?.data?.detail || 'Erreur lors de l\'invitation');
    }
  };

  const handleUpdateMember = async () => {
    try {
      await api.patch(`/api/team/members/${selectedMember.id}`, {
        team_role: selectedMember.team_role,
        can_view_all_sales: selectedMember.can_view_all_sales,
        can_manage_products: selectedMember.can_manage_products,
        custom_commission_rate: selectedMember.custom_commission_rate
      });

      alert('Membre mis à jour');
      setEditDialogOpen(false);
      setSelectedMember(null);
      fetchTeamData();
    } catch (err) {
      console.error('Error updating member:', err);
      alert('Erreur lors de la mise à jour');
    }
  };

  const handleRemoveMember = async (memberId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir retirer ce membre ?')) {
      return;
    }

    try {
      await api.delete(`/api/team/members/${memberId}`);
      alert('Membre retiré');
      fetchTeamData();
    } catch (err) {
      console.error('Error removing member:', err);
      alert('Erreur lors de la suppression');
    }
  };

  const handleResendInvitation = async (memberId) => {
    try {
      await api.post(`/api/team/members/${memberId}/resend-invitation`);
      alert('Invitation renvoyée');
    } catch (err) {
      console.error('Error resending invitation:', err);
      alert('Erreur lors du renvoi');
    }
  };

  const getRoleLabel = (role) => {
    switch (role) {
      case 'commercial':
        return 'Commercial';
      case 'influencer':
        return 'Influenceur';
      case 'manager':
        return 'Manager';
      default:
        return role;
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'commercial':
        return 'primary';
      case 'influencer':
        return 'secondary';
      case 'manager':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'pending_invitation':
        return 'warning';
      case 'inactive':
        return 'default';
      default:
        return 'default';
    }
  };

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
            Gestion de l'équipe
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Invitez et gérez les membres de votre équipe
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setInviteDialogOpen(true)}
          size="large"
          disabled={stats && !stats.can_add_member}
        >
          Inviter un membre
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Stats Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <PeopleIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Total membres
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold">
                  {stats.total_members}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Actifs
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {stats.active_members}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <HourglassEmptyIcon color="warning" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    En attente
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold" color="warning.main">
                  {stats.pending_invitations}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Places disponibles
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="primary">
                  {stats.team_limit === null ? '∞' : stats.available_slots}
                </Typography>
                {stats.team_limit !== null && (
                  <Typography variant="caption" color="text.secondary">
                    sur {stats.team_limit}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {stats && !stats.can_add_member && stats.team_limit !== null && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Limite de membres atteinte ({stats.team_limit}).
          <Button
            size="small"
            onClick={() => window.location.href = '/pricing'}
            sx={{ ml: 1 }}
          >
            Upgrader le plan
          </Button>
        </Alert>
      )}

      {/* Members Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Membre</TableCell>
                <TableCell>Rôle</TableCell>
                <TableCell>Statut</TableCell>
                <TableCell>Commission</TableCell>
                <TableCell>Permissions</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {members.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                      Aucun membre dans votre équipe. Commencez par inviter des commerciaux ou influenceurs.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                members.map((member) => (
                  <TableRow key={member.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                          {member.member_first_name?.[0] || member.invited_email?.[0]?.toUpperCase()}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="600">
                            {member.member_first_name
                              ? `${member.member_first_name} ${member.member_last_name}`
                              : 'Invitation en attente'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {member.member_email || member.invited_email}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>

                    <TableCell>
                      <Chip
                        label={getRoleLabel(member.team_role)}
                        color={getRoleColor(member.team_role)}
                        size="small"
                      />
                    </TableCell>

                    <TableCell>
                      <Chip
                        label={
                          member.status === 'active'
                            ? 'Actif'
                            : member.status === 'pending_invitation'
                            ? 'En attente'
                            : 'Inactif'
                        }
                        color={getStatusColor(member.status)}
                        size="small"
                      />
                    </TableCell>

                    <TableCell>
                      {member.custom_commission_rate
                        ? `${member.custom_commission_rate}%`
                        : 'Par défaut'}
                    </TableCell>

                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {member.can_view_all_sales && (
                          <Chip label="Voir ventes" size="small" variant="outlined" />
                        )}
                        {member.can_manage_products && (
                          <Chip label="Gérer produits" size="small" variant="outlined" />
                        )}
                      </Box>
                    </TableCell>

                    <TableCell align="right">
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                        {member.status === 'pending_invitation' && (
                          <Tooltip title="Renvoyer l'invitation">
                            <IconButton
                              size="small"
                              onClick={() => handleResendInvitation(member.id)}
                            >
                              <EmailIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="Modifier">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedMember(member);
                              setEditDialogOpen(true);
                            }}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Retirer">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleRemoveMember(member.id)}
                          >
                            <DeleteIcon fontSize="small" />
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

      {/* Invite Dialog */}
      <Dialog open={inviteDialogOpen} onClose={() => setInviteDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Inviter un membre</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Email"
              type="email"
              fullWidth
              value={inviteForm.email}
              onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
              required
            />

            <FormControl fullWidth>
              <InputLabel>Rôle</InputLabel>
              <Select
                value={inviteForm.team_role}
                onChange={(e) => setInviteForm({ ...inviteForm, team_role: e.target.value })}
                label="Rôle"
              >
                <MenuItem value="commercial">Commercial</MenuItem>
                <MenuItem value="influencer">Influenceur</MenuItem>
                <MenuItem value="manager">Manager</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Taux de commission personnalisé (%)"
              type="number"
              fullWidth
              value={inviteForm.custom_commission_rate}
              onChange={(e) => setInviteForm({ ...inviteForm, custom_commission_rate: e.target.value })}
              inputProps={{ min: 0, max: 100 }}
            />

            <FormControl component="fieldset">
              <Typography variant="subtitle2" gutterBottom>
                Permissions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant={inviteForm.can_view_all_sales ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => setInviteForm({
                    ...inviteForm,
                    can_view_all_sales: !inviteForm.can_view_all_sales
                  })}
                >
                  Voir toutes les ventes
                </Button>
                <Button
                  variant={inviteForm.can_manage_products ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => setInviteForm({
                    ...inviteForm,
                    can_manage_products: !inviteForm.can_manage_products
                  })}
                >
                  Gérer les produits
                </Button>
              </Box>
            </FormControl>

            <TextField
              label="Notes (optionnel)"
              multiline
              rows={3}
              fullWidth
              value={inviteForm.notes}
              onChange={(e) => setInviteForm({ ...inviteForm, notes: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInviteDialogOpen(false)}>
            Annuler
          </Button>
          <Button
            onClick={handleInviteMember}
            variant="contained"
            disabled={!inviteForm.email}
          >
            Envoyer l'invitation
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      {selectedMember && (
        <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Modifier le membre</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Rôle</InputLabel>
                <Select
                  value={selectedMember.team_role}
                  onChange={(e) => setSelectedMember({ ...selectedMember, team_role: e.target.value })}
                  label="Rôle"
                >
                  <MenuItem value="commercial">Commercial</MenuItem>
                  <MenuItem value="influencer">Influenceur</MenuItem>
                  <MenuItem value="manager">Manager</MenuItem>
                </Select>
              </FormControl>

              <TextField
                label="Taux de commission personnalisé (%)"
                type="number"
                fullWidth
                value={selectedMember.custom_commission_rate || ''}
                onChange={(e) => setSelectedMember({
                  ...selectedMember,
                  custom_commission_rate: e.target.value
                })}
                inputProps={{ min: 0, max: 100 }}
              />

              <FormControl component="fieldset">
                <Typography variant="subtitle2" gutterBottom>
                  Permissions
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Button
                    variant={selectedMember.can_view_all_sales ? 'contained' : 'outlined'}
                    size="small"
                    onClick={() => setSelectedMember({
                      ...selectedMember,
                      can_view_all_sales: !selectedMember.can_view_all_sales
                    })}
                  >
                    Voir toutes les ventes
                  </Button>
                  <Button
                    variant={selectedMember.can_manage_products ? 'contained' : 'outlined'}
                    size="small"
                    onClick={() => setSelectedMember({
                      ...selectedMember,
                      can_manage_products: !selectedMember.can_manage_products
                    })}
                  >
                    Gérer les produits
                  </Button>
                </Box>
              </FormControl>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEditDialogOpen(false)}>
              Annuler
            </Button>
            <Button onClick={handleUpdateMember} variant="contained">
              Sauvegarder
            </Button>
          </DialogActions>
        </Dialog>
      )}
    </Container>
  );
};

export default TeamManagement;
