import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Card from '../components/common/Card';
import { 
  Sparkles, Wand2, TrendingUp, Target, 
  MessageSquare, Mail, BarChart3, Zap,
  Instagram, Facebook, Youtube, Play
} from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const AIMarketing = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('content');
  const [loading, setLoading] = useState(false);
  
  // Content Generator State
  const [contentType, setContentType] = useState('social_post');
  const [platform, setPlatform] = useState('Instagram');
  const [tone, setTone] = useState('friendly');
  const [generatedContent, setGeneratedContent] = useState('');
  
  // Predictions State
  const [predictions, setPredictions] = useState(null);

  const handleGenerateContent = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        `${API_URL}/api/ai/generate-content`,
        { type: contentType, platform, tone },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      setGeneratedContent(response.data.content);
    } catch (error) {
      console.error('Error generating content:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGetPredictions = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `${API_URL}/api/ai/predictions`,
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      setPredictions(response.data);
    } catch (error) {
      console.error('Error fetching predictions:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center space-x-3 mb-4">
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 w-16 h-16 rounded-2xl flex items-center justify-center">
            <Sparkles className="text-white" size={32} />
          </div>
        </div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-4">
          SmartAI Marketer
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Boostez vos performances marketing avec l'intelligence artificielle
        </p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 bg-gray-100 p-2 rounded-xl max-w-md mx-auto">
        <button
          onClick={() => setActiveTab('content')}
          className={`flex-1 px-4 py-3 rounded-lg font-medium transition ${
            activeTab === 'content'
              ? 'bg-white text-indigo-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Wand2 className="inline-block w-5 h-5 mr-2" />
          Génération de Contenu
        </button>
        <button
          onClick={() => setActiveTab('predictions')}
          className={`flex-1 px-4 py-3 rounded-lg font-medium transition ${
            activeTab === 'predictions'
              ? 'bg-white text-indigo-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <TrendingUp className="inline-block w-5 h-5 mr-2" />
          Analyse Prédictive
        </button>
      </div>

      {/* Content Generator Tab */}
      {activeTab === 'content' && (
        <div className="max-w-4xl mx-auto space-y-6">
          <Card title="Générateur de Contenu Hyper-Personnalisé" icon={<Wand2 size={20} />}>
            <div className="space-y-6">
              {/* Type Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Type de Contenu
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button
                    onClick={() => setContentType('social_post')}
                    className={`p-4 rounded-xl border-2 transition ${
                      contentType === 'social_post'
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 hover:border-indigo-300'
                    }`}
                  >
                    <MessageSquare className="w-8 h-8 text-indigo-600 mb-2 mx-auto" />
                    <div className="font-semibold">Post Social</div>
                  </button>
                  <button
                    onClick={() => setContentType('email')}
                    className={`p-4 rounded-xl border-2 transition ${
                      contentType === 'email'
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 hover:border-indigo-300'
                    }`}
                  >
                    <Mail className="w-8 h-8 text-indigo-600 mb-2 mx-auto" />
                    <div className="font-semibold">Email</div>
                  </button>
                  <button
                    onClick={() => setContentType('blog')}
                    className={`p-4 rounded-xl border-2 transition ${
                      contentType === 'blog'
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 hover:border-indigo-300'
                    }`}
                  >
                    <BarChart3 className="w-8 h-8 text-indigo-600 mb-2 mx-auto" />
                    <div className="font-semibold">Article Blog</div>
                  </button>
                </div>
              </div>

              {/* Platform Selection (for social posts) */}
              {contentType === 'social_post' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Plateforme
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {['Instagram', 'Facebook', 'TikTok', 'LinkedIn'].map((p) => (
                      <button
                        key={p}
                        onClick={() => setPlatform(p)}
                        className={`p-3 rounded-lg border-2 transition ${
                          platform === p
                            ? 'border-indigo-600 bg-indigo-50 text-indigo-600'
                            : 'border-gray-200 hover:border-indigo-300'
                        }`}
                      >
                        {p === 'Instagram' && <Instagram className="w-5 h-5 inline mr-2" />}
                        {p === 'Facebook' && <Facebook className="w-5 h-5 inline mr-2" />}
                        {p === 'TikTok' && <Play className="w-5 h-5 inline mr-2" />}
                        {p === 'LinkedIn' && <Target className="w-5 h-5 inline mr-2" />}
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Tone Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Tonalité
                </label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="friendly">Amical</option>
                  <option value="professional">Professionnel</option>
                  <option value="casual">Décontracté</option>
                  <option value="enthusiastic">Enthousiaste</option>
                  <option value="formal">Formel</option>
                </select>
              </div>

              {/* Generate Button */}
              <button
                onClick={handleGenerateContent}
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 rounded-xl font-semibold hover:from-indigo-700 hover:to-purple-700 transition disabled:opacity-50 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Génération en cours...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Générer avec l'IA
                  </>
                )}
              </button>

              {/* Generated Content */}
              {generatedContent && (
                <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-6 rounded-xl border-2 border-indigo-200">
                  <div className="flex justify-between items-start mb-3">
                    <div className="font-semibold text-indigo-900">Contenu Généré ✨</div>
                    <button
                      onClick={() => navigator.clipboard.writeText(generatedContent)}
                      className="text-sm text-indigo-600 hover:text-indigo-700"
                    >
                      Copier
                    </button>
                  </div>
                  <p className="text-gray-800 whitespace-pre-wrap">{generatedContent}</p>
                </div>
              )}
            </div>
          </Card>

          {/* Features Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="bg-indigo-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Zap className="text-indigo-600" size={24} />
              </div>
              <h3 className="font-semibold text-lg mb-2">Optimisation SEO</h3>
              <p className="text-gray-600 text-sm">
                Contenu optimisé automatiquement pour les moteurs de recherche
              </p>
            </div>

            <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="bg-purple-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Target className="text-purple-600" size={24} />
              </div>
              <h3 className="font-semibold text-lg mb-2">Personnalisation</h3>
              <p className="text-gray-600 text-sm">
                Messages adaptés à votre audience et votre marque
              </p>
            </div>

            <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="text-green-600" size={24} />
              </div>
              <h3 className="font-semibold text-lg mb-2">Multi-Plateforme</h3>
              <p className="text-gray-600 text-sm">
                Compatible avec tous les réseaux sociaux majeurs
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Predictions Tab */}
      {activeTab === 'predictions' && (
        <div className="max-w-4xl mx-auto space-y-6">
          <Card title="Analyse Prédictive & Recommandations" icon={<TrendingUp size={20} />}>
            <div className="space-y-6">
              <p className="text-gray-600">
                Utilisez le machine learning pour anticiper les tendances du marché, 
                les comportements d'achat et les risques de désabonnement.
              </p>

              <button
                onClick={handleGetPredictions}
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 rounded-xl font-semibold hover:from-indigo-700 hover:to-purple-700 transition disabled:opacity-50 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Analyse en cours...
                  </>
                ) : (
                  <>
                    <BarChart3 className="w-5 h-5 mr-2" />
                    Lancer l'Analyse Prédictive
                  </>
                )}
              </button>

              {predictions && (
                <div className="space-y-6">
                  {/* Sales Forecast */}
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-xl border-2 border-green-200">
                    <h3 className="font-semibold text-lg mb-4 text-green-900">
                      📈 Prévisions de Ventes
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-green-700 mb-1">Mois Prochain (estimé)</div>
                        <div className="text-3xl font-bold text-green-900">
                          {predictions.predicted_sales_next_month || 0} ventes
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-green-700 mb-1">30 Derniers Jours</div>
                        <div className="text-3xl font-bold text-green-900">
                          {predictions.total_sales_last_30_days || 0} ventes
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-green-700">Moyenne/jour: </span>
                        <span className="font-semibold text-green-900">{predictions.current_daily_average || 0}</span>
                      </div>
                      <div>
                        <span className="text-green-700">Potentiel: </span>
                        <span className="font-semibold text-green-900">{predictions.growth_potential || 'N/A'}</span>
                      </div>
                    </div>
                    <div className="mt-4 text-sm text-green-700">
                      Score de Tendance: {predictions.trend_score || 0}% 
                      <div className="w-full bg-green-200 rounded-full h-2 mt-1">
                        <div 
                          className="bg-green-600 h-2 rounded-full transition-all" 
                          style={{width: `${predictions.trend_score || 0}%`}}
                        ></div>
                      </div>
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-6 rounded-xl border-2 border-indigo-200">
                    <h3 className="font-semibold text-lg mb-4 text-indigo-900">
                      💡 Recommandation Stratégique
                    </h3>
                    <div className="bg-white p-4 rounded-lg border border-indigo-200">
                      <p className="text-gray-700 leading-relaxed">
                        {predictions.recommended_strategy || 'Continuez à créer des campagnes pour obtenir des recommandations personnalisées.'}
                      </p>
                    </div>
                    {predictions.note && (
                      <div className="mt-4 text-sm text-indigo-600 italic">
                        ℹ️ {predictions.note}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* Info Banner */}
      <div className="max-w-4xl mx-auto bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white text-center">
        <h3 className="text-2xl font-bold mb-2">🚀 Améliorez vos Performances</h3>
        <p className="text-indigo-100 mb-4">
          Économisez 60% de temps sur les tâches répétitives et augmentez votre ROI jusqu'à 4x
        </p>
        <div className="flex justify-center space-x-8 mt-6">
          <div>
            <div className="text-3xl font-bold">60%</div>
            <div className="text-indigo-100 text-sm">Temps Économisé</div>
          </div>
          <div>
            <div className="text-3xl font-bold">4x</div>
            <div className="text-indigo-100 text-sm">ROI Multiplié</div>
          </div>
          <div>
            <div className="text-3xl font-bold">87%</div>
            <div className="text-indigo-100 text-sm">Précision IA</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIMarketing;
