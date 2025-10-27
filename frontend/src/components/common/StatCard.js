import React, { memo } from 'react';
import { formatNumber, formatCurrency } from '../../utils/helpers';

const StatCard = memo(({ title, value, icon, trend, isCurrency = false, suffix = '' }) => {
  // Handle different value types
  let displayValue;
  
  if (typeof value === 'string') {
    // If value is already a string (e.g., "320%"), use it as-is
    displayValue = value;
  } else if (isCurrency) {
    displayValue = formatCurrency(value);
  } else if (suffix) {
    displayValue = `${formatNumber(value)}${suffix}`;
  } else {
    displayValue = formatNumber(value);
  }
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{displayValue}</p>
          {trend && (
            <p className={`text-sm font-medium mt-2 ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend >= 0 ? '↗' : '↘'} {Math.abs(trend)}% ce mois
            </p>
          )}
        </div>
        {icon && (
          <div className="ml-4 p-3 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
});

StatCard.displayName = 'StatCard';

export default StatCard;
