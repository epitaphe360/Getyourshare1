import React, { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';

/**
 * Bouton WhatsApp flottant
 * Permet aux visiteurs de contacter directement via WhatsApp
 */
const WhatsAppFloatingButton = ({ 
  phoneNumber = '+212600000000',  // Remplacez par votre vrai numéro
  message = 'Bonjour! Je suis intéressé par ShareYourSales.',
  position = 'left'  // 'left' ou 'right'
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleClick = () => {
    const cleanPhone = phoneNumber.replace(/[^\d]/g, '');
    const encodedMessage = encodeURIComponent(message);
    const whatsappUrl = `https://wa.me/${cleanPhone}?text=${encodedMessage}`;
    window.open(whatsappUrl, '_blank');
  };

  const positionClasses = position === 'left' 
    ? 'left-6' 
    : 'right-6';

  return (
    <button
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`fixed bottom-24 ${positionClasses} z-40 w-14 h-14 bg-[#25D366] hover:bg-[#20BA5A] text-white rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 group`}
      aria-label="Contacter sur WhatsApp"
    >
      {isHovered ? (
        <MessageCircle className="w-7 h-7 animate-pulse" />
      ) : (
        <MessageCircle className="w-7 h-7" />
      )}
      
      {/* Tooltip */}
      <div className={`absolute ${position === 'left' ? 'left-16' : 'right-16'} bg-gray-900 text-white px-3 py-2 rounded-lg text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none`}>
        Contactez-nous sur WhatsApp
        <div className={`absolute top-1/2 -translate-y-1/2 ${position === 'left' ? '-left-1' : '-right-1'} w-2 h-2 bg-gray-900 rotate-45`}></div>
      </div>

      {/* Cercles d'animation */}
      <span className="absolute inset-0 rounded-full bg-[#25D366] opacity-75 animate-ping"></span>
    </button>
  );
};

export default WhatsAppFloatingButton;
