// Format currency
export const formatCurrency = (amount, currency = 'EUR') => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: currency,
  }).format(amount);
};

// Format date
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('fr-FR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

// Format date short
export const formatDateShort = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('fr-FR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
};

// Format number
export const formatNumber = (num) => {
  return new Intl.NumberFormat('fr-FR').format(num);
};

// Get status badge color
export const getStatusColor = (status) => {
  // Convert to string and handle null/undefined
  if (!status) return 'bg-gray-100 text-gray-800';
  
  const statusStr = typeof status === 'string' ? status : String(status);
  
  const colors = {
    approved: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    rejected: 'bg-red-100 text-red-800',
    denied: 'bg-red-100 text-red-800',
    active: 'bg-blue-100 text-blue-800',
    paused: 'bg-gray-100 text-gray-800',
    inactive: 'bg-gray-100 text-gray-800',
    draft: 'bg-purple-100 text-purple-800',
    completed: 'bg-green-100 text-green-800',
    ended: 'bg-red-100 text-red-800',
    archived: 'bg-gray-100 text-gray-800',
  };
  return colors[statusStr.toLowerCase()] || 'bg-gray-100 text-gray-800';
};

// Truncate text
export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};
