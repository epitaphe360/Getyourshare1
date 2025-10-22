import React from 'react';
import { getStatusColor } from '../../utils/helpers';

const Badge = ({ status, children }) => {
  const colorClass = getStatusColor(status || children);
  
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colorClass}`}>
      {children || status}
    </span>
  );
};

export default Badge;
