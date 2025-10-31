import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Modal from '../../components/common/Modal';
import {
  Plus, Send, Calendar, TrendingUp, Eye, Heart,
  Share2, MousePointerClick, Instagram, Facebook,
  Twitter, Linkedin, Edit, Trash2, Clock, CheckCircle,
  XCircle, Sparkles, Copy, Layout, BarChart3, FileText
} from 'lucide-react';

/**
 * Admin Social Media Dashboard
 * Manage platform promotional posts across social networks
 */
const AdminSocialDashboard = () => {
  const { user } = useAuth();
  const toast = useToast();

  const [posts, setPosts] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [selectedPost, setSelectedPost] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const [createFormData, setCreateFormData] = useState({
    title: '',
    caption: '',
    media_urls: [''],
    media_type: 'image',
    cta_text: '',
    cta_url: '',
    hashtags: [],
    campaign_type: 'general'
  });

  const [publishFormData, setPublishFormData] = useState({
    platforms: [],
    publish_now: true,
    scheduled_for: null
  });

  const campaignTypes = [
    { id: 'general', name: 'Général', icon: '📱' },
    { id: 'app_launch', name: 'Lancement App', icon: '🚀' },
    { id: 'new_feature', name: 'Nouvelle Fonctionnalité', icon: '✨' },
    { id: 'merchant_recruitment', name: 'Recrutement Marchands', icon: '🏪' },
    { id: 'influencer_recruitment', name: 'Recrutement Influenceurs', icon: '🌟' },
    { id: 'seasonal_promo', name: 'Promo Saisonnière', icon: '🎁' },
    { id: 'user_testimonial', name: 'Témoignage', icon: '💬' },
    { id: 'milestone_celebration', name: 'Célébration', icon: '🎉' },
    { id: 'contest', name: 'Concours', icon: '🎯' }
  ];

  const platforms = [
    { id: 'instagram', name: 'Instagram', icon: Instagram, color: 'from-purple-600 to-pink-600' },
    { id: 'facebook', name: 'Facebook', icon: Facebook, color: 'from-blue-600 to-blue-700' },
    { id: 'tiktok', name: 'TikTok', icon: () => <span className="font-bold">TT</span>, color: 'from-black to-gray-800' },
    { id: 'twitter', name: 'Twitter', icon: Twitter, color: 'from-sky-500 to-sky-600' },
    { id: 'linkedin', name: 'LinkedIn', icon: Linkedin, color: 'from-blue-700 to-blue-800' }
  ];

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchPosts();
      fetchTemplates();
      fetchAnalytics();
    }
  }, [user]);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/admin/social/posts');
      if (response.data.success) {
        setPosts(response.data.posts || []);
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
      toast.error('Erreur lors du chargement des posts');
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/api/admin/social/templates');
      if (response.data.success) {
        setTemplates(response.data.templates || []);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/api/admin/social/analytics');
      if (response.data.success) {
        setAnalytics(response.data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const handleUseTemplate = (template) => {
    setSelectedTemplate(template);
    setCreateFormData({
      ...createFormData,
      caption: template.caption_template,
      hashtags: template.suggested_hashtags || [],
      cta_text: template.suggested_cta_text || '',
      cta_url: template.suggested_cta_url || '',
      campaign_type: template.category || 'general'
    });
    setShowCreateModal(true);
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();

    try {
      const payload = {
        ...createFormData,
        template_id: selectedTemplate?.id
      };

      const response = await api.post('/api/admin/social/posts', payload);
      if (response.data.success) {
        toast.success('Post créé avec succès!');
        setShowCreateModal(false);
        resetCreateForm();
        fetchPosts();
      }
    } catch (error) {
      console.error('Error creating post:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la création du post');
    }
  };

  const handlePublishPost = async () => {
    if (!selectedPost || publishFormData.platforms.length === 0) {
      toast.warning('Veuillez sélectionner au moins une plateforme');
      return;
    }

    try {
      const response = await api.post(
        `/api/admin/social/posts/${selectedPost.id}/publish`,
        publishFormData
      );

      if (response.data.success) {
        const published = response.data.published || [];
        const failed = response.data.failed || [];

        if (published.length > 0) {
          toast.success(`Publié sur ${published.length} plateforme(s)!`);
          setShowPublishModal(false);
          setSelectedPost(null);
          resetPublishForm();
          fetchPosts();
          fetchAnalytics();
        } else {
          toast.error('Échec de la publication sur toutes les plateformes');
        }
      }
    } catch (error) {
      console.error('Error publishing post:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la publication');
    }
  };

  const handleDeletePost = async (postId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir archiver ce post?')) return;

    try {
      const response = await api.delete(`/api/admin/social/posts/${postId}`);
      if (response.data.success) {
        toast.success('Post archivé');
        fetchPosts();
      }
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const resetCreateForm = () => {
    setCreateFormData({
      title: '',
      caption: '',
      media_urls: [''],
      media_type: 'image',
      cta_text: '',
      cta_url: '',
      hashtags: [],
      campaign_type: 'general'
    });
    setSelectedTemplate(null);
  };

  const resetPublishForm = () => {
    setPublishFormData({
      platforms: [],
      publish_now: true,
      scheduled_for: null
    });
  };

  const togglePlatform = (platformId) => {
    setPublishFormData((prev) => ({
      ...prev,
      platforms: prev.platforms.includes(platformId)
        ? prev.platforms.filter((p) => p !== platformId)
        : [...prev.platforms, platformId]
    }));
  };

  const getPlatformIcon = (platformId) => {
    const platform = platforms.find((p) => p.id === platformId);
    return platform ? platform.icon : null;
  };

  if (user?.role !== 'admin') {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <XCircle className="w-16 h-16 text-red-300 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Accès Réservé aux Admins</h2>
        <p className="text-gray-600">Cette page est réservée aux administrateurs</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Social Media Admin</h1>
          <p className="text-gray-600 mt-1">
            Gérez les publications promotionnelles de la plateforme
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition"
        >
          <Plus className="w-5 h-5 mr-2" />
          Nouveau Post
        </button>
      </div>

      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Posts</p>
                <p className="text-3xl font-bold text-gray-900">
                  {analytics.global_stats?.total_posts || 0}
                </p>
              </div>
              <div className="bg-purple-100 p-3 rounded-lg">
                <FileText className="w-8 h-8 text-purple-600" />
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Vues Totales</p>
                <p className="text-3xl font-bold text-gray-900">
                  {(analytics.global_stats?.total_views || 0).toLocaleString()}
                </p>
              </div>
              <div className="bg-blue-100 p-3 rounded-lg">
                <Eye className="w-8 h-8 text-blue-600" />
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Engagement</p>
                <p className="text-3xl font-bold text-gray-900">
                  {(analytics.global_stats?.total_likes || 0).toLocaleString()}
                </p>
              </div>
              <div className="bg-pink-100 p-3 rounded-lg">
                <Heart className="w-8 h-8 text-pink-600" />
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Taux Engagement</p>
                <p className="text-3xl font-bold text-gray-900">
                  {(analytics.global_stats?.engagement_rate_percent || 0).toFixed(1)}%
                </p>
              </div>
              <div className="bg-green-100 p-3 rounded-lg">
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Templates Section */}
      <div>
        <div className="flex items-center mb-4">
          <Layout className="w-6 h-6 text-purple-600 mr-2" />
          <h2 className="text-2xl font-bold text-gray-900">Templates de Posts</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {templates.slice(0, 8).map((template) => (
            <Card key={template.id} className="hover:shadow-lg transition-shadow cursor-pointer">
              <div onClick={() => handleUseTemplate(template)}>
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-gray-900">{template.name}</h3>
                  <Sparkles className="w-5 h-5 text-purple-500" />
                </div>
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">{template.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                    {template.category}
                  </span>
                  <span className="text-xs text-gray-500">{template.usage_count || 0} fois</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Posts List */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Posts Récents</h2>
        {loading ? (
          <div className="text-center py-12">Chargement...</div>
        ) : posts.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun post</h3>
              <p className="text-gray-600 mb-4">Créez votre premier post promotionnel</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Créer un Post
              </button>
            </div>
          </Card>
        ) : (
          <div className="space-y-4">
            {posts.map((post) => (
              <Card key={post.id}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-start space-x-4">
                      {post.media_urls && post.media_urls[0] && (
                        <img
                          src={post.media_urls[0]}
                          alt={post.title}
                          className="w-24 h-24 object-cover rounded-lg"
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                      )}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">{post.title}</h3>
                          <span
                            className={`text-xs px-2 py-1 rounded ${
                              post.status === 'published'
                                ? 'bg-green-100 text-green-700'
                                : post.status === 'scheduled'
                                ? 'bg-orange-100 text-orange-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}
                          >
                            {post.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{post.caption}</p>

                        {/* Platforms Published */}
                        {post.platforms && Object.keys(post.platforms).length > 0 && (
                          <div className="flex items-center space-x-2 mb-3">
                            {Object.keys(post.platforms).map((platformId) => {
                              const Icon = getPlatformIcon(platformId);
                              const platformData = post.platforms[platformId];
                              return Icon ? (
                                <div
                                  key={platformId}
                                  className={`flex items-center space-x-1 px-2 py-1 rounded text-xs text-white ${
                                    platformData.status === 'published'
                                      ? 'bg-green-500'
                                      : 'bg-gray-400'
                                  }`}
                                >
                                  <Icon className="w-3 h-3" />
                                  <span className="capitalize">{platformId}</span>
                                </div>
                              ) : null;
                            })}
                          </div>
                        )}

                        {/* Stats */}
                        {post.status === 'published' && (
                          <div className="flex items-center space-x-4 text-sm text-gray-600">
                            <span className="flex items-center">
                              <Eye className="w-4 h-4 mr-1" />
                              {post.total_views || 0}
                            </span>
                            <span className="flex items-center">
                              <Heart className="w-4 h-4 mr-1" />
                              {post.total_likes || 0}
                            </span>
                            <span className="flex items-center">
                              <Share2 className="w-4 h-4 mr-1" />
                              {post.total_shares || 0}
                            </span>
                            <span className="flex items-center">
                              <MousePointerClick className="w-4 h-4 mr-1" />
                              {post.total_clicks || 0}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex space-x-2">
                    {post.status === 'draft' && (
                      <button
                        onClick={() => {
                          setSelectedPost(post);
                          setShowPublishModal(true);
                        }}
                        className="p-2 bg-green-100 text-green-600 rounded-lg hover:bg-green-200"
                        title="Publier"
                      >
                        <Send className="w-5 h-5" />
                      </button>
                    )}
                    <button
                      onClick={() => handleDeletePost(post.id)}
                      className="p-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200"
                      title="Archiver"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Create Post Modal */}
      {showCreateModal && (
        <Modal isOpen={true} onClose={() => {
          setShowCreateModal(false);
          resetCreateForm();
        }} size="large">
          <div className="p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              {selectedTemplate ? `Template: ${selectedTemplate.name}` : 'Créer un Post'}
            </h2>

            <form onSubmit={handleCreatePost} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Titre</label>
                <input
                  type="text"
                  value={createFormData.title}
                  onChange={(e) => setCreateFormData({ ...createFormData, title: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Titre du post"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Type de Campagne</label>
                <select
                  value={createFormData.campaign_type}
                  onChange={(e) => setCreateFormData({ ...createFormData, campaign_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {campaignTypes.map((type) => (
                    <option key={type.id} value={type.id}>
                      {type.icon} {type.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Caption</label>
                <textarea
                  value={createFormData.caption}
                  onChange={(e) => setCreateFormData({ ...createFormData, caption: e.target.value })}
                  rows="6"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
                  placeholder="Texte du post..."
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">CTA Text</label>
                  <input
                    type="text"
                    value={createFormData.cta_text}
                    onChange={(e) => setCreateFormData({ ...createFormData, cta_text: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Ex: Télécharger maintenant"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">CTA URL</label>
                  <input
                    type="url"
                    value={createFormData.cta_url}
                    onChange={(e) => setCreateFormData({ ...createFormData, cta_url: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="https://..."
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">URL Média</label>
                <input
                  type="url"
                  value={createFormData.media_urls[0]}
                  onChange={(e) => setCreateFormData({ ...createFormData, media_urls: [e.target.value] })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="https://..."
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700"
                >
                  Créer le Post
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    resetCreateForm();
                  }}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300"
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </Modal>
      )}

      {/* Publish Modal */}
      {showPublishModal && selectedPost && (
        <Modal isOpen={true} onClose={() => {
          setShowPublishModal(false);
          setSelectedPost(null);
          resetPublishForm();
        }}>
          <div className="p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Publier sur les Réseaux Sociaux</h2>

            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-2">{selectedPost.title}</h3>
              <p className="text-sm text-gray-600 line-clamp-2">{selectedPost.caption}</p>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Sélectionner les plateformes
              </label>
              <div className="grid grid-cols-2 gap-3">
                {platforms.map((platform) => {
                  const Icon = platform.icon;
                  const isSelected = publishFormData.platforms.includes(platform.id);

                  return (
                    <button
                      key={platform.id}
                      type="button"
                      onClick={() => togglePlatform(platform.id)}
                      className={`p-4 border-2 rounded-lg transition-all ${
                        isSelected
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className={`w-10 h-10 rounded-lg bg-gradient-to-r ${platform.color} flex items-center justify-center text-white mb-2 mx-auto`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      <div className="text-sm font-medium text-gray-900">{platform.name}</div>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={handlePublishPost}
                disabled={publishFormData.platforms.length === 0}
                className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50"
              >
                <Send className="inline-block w-5 h-5 mr-2" />
                Publier sur {publishFormData.platforms.length} plateforme(s)
              </button>
              <button
                onClick={() => {
                  setShowPublishModal(false);
                  setSelectedPost(null);
                  resetPublishForm();
                }}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300"
              >
                Annuler
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default AdminSocialDashboard;
