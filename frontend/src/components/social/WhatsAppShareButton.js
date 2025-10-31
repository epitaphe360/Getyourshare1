import React, { useState } from 'react';
import { useI18n } from '../../i18n/i18n';
import { MessageCircle, Share2, Copy, Check } from 'lucide-react';

/**
 * Bouton de partage WhatsApp
 *
 * Permet de partager facilement du contenu sur WhatsApp:
 * - Liens d'affiliation
 * - Produits
 * - Messages personnalisés
 *
 * Fonctionne sur mobile (app WhatsApp) et desktop (WhatsApp Web)
 */
const WhatsAppShareButton = ({
  text,
  url,
  phoneNumber = null,
  productName = null,
  commissionRate = null,
  variant = 'primary',  // primary, secondary, minimal
  size = 'medium',      // small, medium, large
  showCopyOption = true,
  onShare = null,
  className = ''
}) => {
  const { t } = useI18n();
  const [showOptions, setShowOptions] = useState(false);
  const [copied, setCopied] = useState(false);

  // Construire le message WhatsApp
  const buildMessage = () => {
    if (productName && commissionRate) {
      // Message pour lien d'affiliation
      return `🎉 *${productName}*\n\n💰 Commission: ${commissionRate}%\n\n🔗 ${url || text}\n\nPartage ce lien et gagne de l'argent! 🚀`;
    } else if (url) {
      // Message avec URL
      return `${text}\n\n${url}`;
    } else {
      // Message simple
      return text;
    }
  };

  // Générer l'URL WhatsApp
  const getWhatsAppUrl = () => {
    const message = encodeURIComponent(buildMessage());

    if (phoneNumber) {
      // Message direct à un numéro
      const cleanPhone = phoneNumber.replace(/[^\d]/g, '');
      return `https://wa.me/${cleanPhone}?text=${message}`;
    } else {
      // Partage général (choix du destinataire)
      return `https://wa.me/?text=${message}`;
    }
  };

  // Copier le message dans le presse-papiers
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(buildMessage());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);

      if (onShare) {
        onShare({ type: 'copy', success: true });
      }
    } catch (err) {
      console.error('Erreur copie:', err);
    }
  };

  // Ouvrir WhatsApp
  const handleShare = () => {
    const whatsappUrl = getWhatsAppUrl();
    window.open(whatsappUrl, '_blank');

    if (onShare) {
      onShare({ type: 'whatsapp', success: true });
    }
  };

  // Classes selon le variant
  const getButtonClasses = () => {
    const baseClasses = 'inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-all duration-200';

    const sizeClasses = {
      small: 'px-3 py-1.5 text-sm',
      medium: 'px-4 py-2 text-base',
      large: 'px-6 py-3 text-lg'
    };

    const variantClasses = {
      primary: 'bg-[#25D366] text-white hover:bg-[#20BA5A] shadow-md hover:shadow-lg',
      secondary: 'bg-white text-[#25D366] border-2 border-[#25D366] hover:bg-[#25D366] hover:text-white',
      minimal: 'bg-transparent text-[#25D366] hover:bg-[#25D366]/10'
    };

    return `${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`;
  };

  return (
    <div className="relative inline-block">
      {showCopyOption && !phoneNumber ? (
        // Bouton avec menu déroulant (partager OU copier)
        <>
          <button
            onClick={() => setShowOptions(!showOptions)}
            className={getButtonClasses()}
          >
            <MessageCircle size={size === 'small' ? 16 : size === 'large' ? 24 : 20} />
            <span>{t('share_whatsapp') || 'Partager sur WhatsApp'}</span>
            <Share2 size={14} />
          </button>

          {showOptions && (
            <div className="absolute top-full left-0 mt-2 bg-white rounded-lg shadow-xl border border-gray-200 z-50 min-w-[200px]">
              <button
                onClick={() => {
                  handleShare();
                  setShowOptions(false);
                }}
                className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition text-left rounded-t-lg"
              >
                <MessageCircle size={18} className="text-[#25D366]" />
                <span className="font-medium">Partager sur WhatsApp</span>
              </button>

              <button
                onClick={() => {
                  handleCopy();
                  setShowOptions(false);
                }}
                className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition text-left rounded-b-lg border-t"
              >
                {copied ? (
                  <>
                    <Check size={18} className="text-green-600" />
                    <span className="font-medium text-green-600">Copié!</span>
                  </>
                ) : (
                  <>
                    <Copy size={18} className="text-gray-600" />
                    <span className="font-medium">Copier le message</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* Backdrop pour fermer le menu */}
          {showOptions && (
            <div
              className="fixed inset-0 z-40"
              onClick={() => setShowOptions(false)}
            />
          )}
        </>
      ) : (
        // Bouton simple (partage direct)
        <button
          onClick={handleShare}
          className={getButtonClasses()}
        >
          <MessageCircle size={size === 'small' ? 16 : size === 'large' ? 24 : 20} />
          <span>
            {phoneNumber
              ? t('contact_whatsapp') || 'Contacter sur WhatsApp'
              : t('share_whatsapp') || 'Partager sur WhatsApp'}
          </span>
        </button>
      )}
    </div>
  );
};

export default WhatsAppShareButton;
