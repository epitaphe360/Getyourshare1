import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../utils/api';

/**
 * Query Keys
 * Centralized query key management
 */
export const QUERY_KEYS = {
  // Sales
  sales: ['sales'],
  sale: (id) => ['sales', id],
  salesStats: ['sales', 'stats'],

  // Commissions
  commissions: ['commissions'],
  commission: (id) => ['commissions', id],
  commissionsStats: ['commissions', 'stats'],

  // Payments
  payments: ['payments'],
  payment: (id) => ['payments', id],
  paymentsStats: ['payments', 'stats'],

  // Affiliates
  affiliates: ['affiliates'],
  affiliate: (id) => ['affiliates', id],
  affiliateBalance: (id) => ['affiliates', id, 'balance'],

  // Advertisers
  advertisers: ['advertisers'],
  advertiser: (id) => ['advertisers', id],

  // Campaigns
  campaigns: ['campaigns'],
  campaign: (id) => ['campaigns', id],

  // Dashboard
  dashboard: ['dashboard'],
  dashboardStats: (role) => ['dashboard', 'stats', role],
};

/**
 * Sales Queries
 */
export const useSales = (filters = {}) => {
  return useQuery({
    queryKey: [...QUERY_KEYS.sales, filters],
    queryFn: () => api.get('/api/sales', { params: filters }),
  });
};

export const useSale = (id) => {
  return useQuery({
    queryKey: QUERY_KEYS.sale(id),
    queryFn: () => api.get(`/api/sales/${id}`),
    enabled: !!id,
  });
};

export const useSalesStats = () => {
  return useQuery({
    queryKey: QUERY_KEYS.salesStats,
    queryFn: () => api.get('/api/sales/stats'),
  });
};

/**
 * Sales Mutations
 */
export const useCreateSale = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (saleData) => api.post('/api/sales', saleData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.sales });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.salesStats });
    },
  });
};

export const useUpdateSale = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, ...data }) => api.put(`/api/sales/${id}`, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.sales });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.sale(variables.id) });
    },
  });
};

export const useDeleteSale = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id) => api.delete(`/api/sales/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.sales });
    },
  });
};

/**
 * Commissions Queries
 */
export const useCommissions = (filters = {}) => {
  return useQuery({
    queryKey: [...QUERY_KEYS.commissions, filters],
    queryFn: () => api.get('/api/commissions', { params: filters }),
  });
};

export const useCommission = (id) => {
  return useQuery({
    queryKey: QUERY_KEYS.commission(id),
    queryFn: () => api.get(`/api/commissions/${id}`),
    enabled: !!id,
  });
};

/**
 * Commissions Mutations
 */
export const useCreateCommission = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (commissionData) => api.post('/api/commissions', commissionData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.commissions });
    },
  });
};

export const useUpdateCommission = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, ...data }) => api.put(`/api/commissions/${id}`, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.commissions });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.commission(variables.id) });
    },
  });
};

/**
 * Payments Queries
 */
export const usePayments = (filters = {}) => {
  return useQuery({
    queryKey: [...QUERY_KEYS.payments, filters],
    queryFn: () => api.get('/api/payments', { params: filters }),
  });
};

export const usePayment = (id) => {
  return useQuery({
    queryKey: QUERY_KEYS.payment(id),
    queryFn: () => api.get(`/api/payments/${id}`),
    enabled: !!id,
  });
};

/**
 * Payments Mutations
 */
export const useCreatePayment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (paymentData) => api.post('/api/payments', paymentData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.payments });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.affiliates });
    },
  });
};

export const useUpdatePaymentStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }) => api.patch(`/api/payments/${id}/status`, { status }),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.payments });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.payment(variables.id) });
    },
  });
};

/**
 * Affiliates Queries
 */
export const useAffiliates = (filters = {}) => {
  return useQuery({
    queryKey: [...QUERY_KEYS.affiliates, filters],
    queryFn: () => api.get('/api/affiliates', { params: filters }),
  });
};

export const useAffiliate = (id) => {
  return useQuery({
    queryKey: QUERY_KEYS.affiliate(id),
    queryFn: () => api.get(`/api/affiliates/${id}`),
    enabled: !!id,
  });
};

export const useAffiliateBalance = (id) => {
  return useQuery({
    queryKey: QUERY_KEYS.affiliateBalance(id),
    queryFn: () => api.get(`/api/affiliates/${id}/balance`),
    enabled: !!id,
  });
};

/**
 * Dashboard Queries
 */
export const useDashboardStats = (role) => {
  return useQuery({
    queryKey: QUERY_KEYS.dashboardStats(role),
    queryFn: () => api.get('/api/dashboard/stats', { params: { role } }),
  });
};

/**
 * Campaigns Queries
 */
export const useCampaigns = (filters = {}) => {
  return useQuery({
    queryKey: [...QUERY_KEYS.campaigns, filters],
    queryFn: () => api.get('/api/campaigns', { params: filters }),
  });
};

export const useCampaign = (id) => {
  return useQuery({
    queryKey: QUERY_KEYS.campaign(id),
    queryFn: () => api.get(`/api/campaigns/${id}`),
    enabled: !!id,
  });
};

/**
 * Campaigns Mutations
 */
export const useCreateCampaign = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (campaignData) => api.post('/api/campaigns', campaignData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.campaigns });
    },
  });
};

export const useUpdateCampaign = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, ...data }) => api.put(`/api/campaigns/${id}`, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.campaigns });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.campaign(variables.id) });
    },
  });
};
