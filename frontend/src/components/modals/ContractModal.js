import React, { useState, useEffect } from 'react';
import { X, FileText, CheckCircle, Edit3 } from 'lucide-react';
import api from '../../utils/api';

const ContractModal = ({ isOpen, onClose, requestId, userRole, onSigned }) => {
  const [contractTerms, setContractTerms] = useState(null);
  const [accepted, setAccepted] = useState(false);
  const [signature, setSignature] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchContractTerms();
    }
  }, [isOpen]);

  const fetchContractTerms = async () => {
    try {
      const response = await api.get('/api/collaborations/contract-terms');
      setContractTerms(response.data.contract);
    } catch (err) {
      setError('Erreur lors du chargement du contrat');
    }
  };

  const handleSign = async () => {
    if (!accepted || !signature.trim()) {
      setError('Veuillez accepter les conditions et signer');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Hash simple de la signature (en production, utiliser crypto plus robuste)
      const signatureHash = btoa(`${signature}-${Date.now()}-${userRole}`);

      const response = await api.post(
        `/api/collaborations/requests/${requestId}/sign-contract`,
        { signature: signatureHash }
      );

      if (response.data.success) {
        onSigned && onSigned(response.data);
        onClose();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la signature');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !contractTerms) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
                <FileText size={28} />
                Contrat de Collaboration
              </h2>
              <p className="text-indigo-100">Version {contractTerms.version}</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-full p-2 transition"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Contract Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Introduction */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-bold text-blue-900 mb-2">📋 Préambule</h3>
            <p className="text-sm text-blue-800">
              Le présent contrat définit les termes et conditions de la collaboration entre le Marchand et l'Influenceur
              dans le cadre de la promotion de produits via la plateforme TrackNow.
            </p>
          </div>

          {/* Contract Terms */}
          <div className="space-y-4">
            {contractTerms.terms.map((term, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 transition">
                <h4 className="font-bold text-gray-900 mb-2">{term.title}</h4>
                <p className="text-sm text-gray-700 leading-relaxed">{term.content}</p>
              </div>
            ))}
          </div>

          {/* Ethical Guidelines */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-bold text-green-900 mb-3 flex items-center gap-2">
              <CheckCircle size={20} />
              Code de Conduite Éthique
            </h3>
            <ul className="text-sm text-green-800 space-y-2">
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>Transparence totale : mentionner #ad ou #sponsored dans toutes les publications</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>Honnêteté : ne pas faire de fausses déclarations sur le produit</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>Respect : maintenir une image professionnelle et respectueuse</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>Conformité : respecter toutes les lois en vigueur au Maroc</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>Non-discrimination : promouvoir dans un esprit d'inclusion et de diversité</span>
              </li>
            </ul>
          </div>

          {/* Acceptance Checkbox */}
          <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4">
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={accepted}
                onChange={(e) => setAccepted(e.target.checked)}
                className="mt-1 w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <span className="text-sm text-gray-900">
                <strong>J'ai lu et j'accepte</strong> l'intégralité des termes et conditions de ce contrat,
                y compris le code de conduite éthique. Je m'engage à respecter mes obligations et à promouvoir
                les produits de manière honnête et transparente.
              </span>
            </label>
          </div>

          {/* Signature */}
          {accepted && (
            <div className="border-2 border-indigo-200 rounded-lg p-4 bg-indigo-50">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-900 mb-2">
                <Edit3 size={18} className="text-indigo-600" />
                Signature électronique
              </label>
              <input
                type="text"
                value={signature}
                onChange={(e) => setSignature(e.target.value)}
                placeholder="Tapez votre nom complet pour signer"
                className="w-full px-4 py-3 border border-indigo-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-signature text-lg"
                required
              />
              <p className="text-xs text-gray-600 mt-2">
                En signant, vous acceptez que ce document a la même valeur juridique qu'une signature manuscrite.
              </p>
              <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
                <span>Date:</span>
                <span className="font-medium">{new Date().toLocaleDateString('fr-FR', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}</span>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="border-t bg-gray-50 p-6">
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition font-medium"
              disabled={loading}
            >
              Annuler
            </button>
            <button
              onClick={handleSign}
              disabled={loading || !accepted || !signature.trim()}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition font-medium shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Signature...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <Edit3 size={18} />
                  Signer le contrat
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        .font-signature {
          font-family: 'Brush Script MT', cursive, 'Dancing Script', cursive;
        }
      `}</style>
    </div>
  );
};

export default ContractModal;
