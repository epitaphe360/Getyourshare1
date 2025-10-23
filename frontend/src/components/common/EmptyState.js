import React from 'react';
import { Package, Plus } from 'lucide-react';
import Button from './Button';

const EmptyState = ({ 
  icon: Icon = Package,
  title = "Aucune donnée disponible",
  description = "Commencez par ajouter des éléments",
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4">
        <Icon className="text-gray-400" size={40} />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-500 text-center mb-6 max-w-md">{description}</p>
      
      {(actionLabel || secondaryActionLabel) && (
        <div className="flex gap-3">
          {actionLabel && (
            <Button onClick={onAction} className="flex items-center gap-2">
              <Plus size={18} />
              {actionLabel}
            </Button>
          )}
          {secondaryActionLabel && (
            <Button variant="outline" onClick={onSecondaryAction}>
              {secondaryActionLabel}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default EmptyState;
