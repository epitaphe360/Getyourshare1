import React from 'react';
import { Package } from 'lucide-react';

const EmptyState = ({ 
  icon,
  title,
  description,
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
  loading
}) => {
  // Accept both icon components (Search) or ready-made elements (<Search />)
  const renderIcon = () => {
    if (React.isValidElement(icon)) {
      // Preserve existing props but ensure consistent sizing/styling
      return React.cloneElement(icon, {
        size: icon.props.size || 40,
        className: icon.props.className ? `${icon.props.className}` : 'text-gray-400'
      });
    }
    if (typeof icon === 'function') {
      const IconComponent = icon;
      return <IconComponent className="text-gray-400" size={40} />;
    }
    return <Package className="text-gray-400" size={40} />;
  };
  const displayTitle = title || "Aucune donnée disponible";
  const displayDescription = description || "Commencez par ajouter des éléments";
  const isLoading = loading || false;
  
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4">
        {renderIcon()}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{displayTitle}</h3>
      <p className="text-gray-500 text-center mb-6 max-w-md">{displayDescription}</p>
      
      {(actionLabel || secondaryActionLabel) && (
        <div className="flex gap-3">
          {actionLabel && (
            <button 
              onClick={onAction} 
              disabled={isLoading} 
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {actionLabel}
            </button>
          )}
          {secondaryActionLabel && (
            <button 
              onClick={onSecondaryAction} 
              disabled={isLoading}
              className="px-4 py-2 border-2 border-blue-600 text-blue-600 hover:bg-blue-50 font-semibold rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {secondaryActionLabel}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default EmptyState;