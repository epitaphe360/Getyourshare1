import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../utils/api';
import Card from '../components/common/Card';
import {
  Mail, Phone, MapPin, Send, MessageSquare,
  HelpCircle, Users, Briefcase, Gift,
  Bug, Lightbulb, AlertTriangle, CheckCircle
} from 'lucide-react';

/**
 * Contact Page
 * Public contact form for support, inquiries, partnerships
 */
const Contact = () => {
  const { user } = useAuth();
  const toast = useToast();

  const [formData, setFormData] = useState({
    name: user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() : '',
    email: user?.email || '',
    phone: user?.phone || '',
    subject: '',
    message: '',
    category: 'general'
  });

  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const categories = [
    {
      id: 'general',
      name: 'Question Générale',
      icon: MessageSquare,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      id: 'support',
      name: 'Support Technique',
      icon: HelpCircle,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      id: 'merchant_inquiry',
      name: 'Question Marchand',
      icon: Briefcase,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      id: 'influencer_inquiry',
      name: 'Question Influenceur',
      icon: Users,
      color: 'text-pink-600',
      bgColor: 'bg-pink-100'
    },
    {
      id: 'partnership',
      name: 'Partenariat',
      icon: Gift,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    },
    {
      id: 'bug_report',
      name: 'Signaler un Bug',
      icon: Bug,
      color: 'text-red-600',
      bgColor: 'bg-red-100'
    },
    {
      id: 'feature_request',
      name: 'Demande de Fonctionnalité',
      icon: Lightbulb,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100'
    },
    {
      id: 'complaint',
      name: 'Réclamation',
      icon: AlertTriangle,
      color: 'text-gray-600',
      bgColor: 'bg-gray-100'
    }
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.name || !formData.email || !formData.subject || !formData.message) {
      toast.warning('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setSubmitting(true);

    try {
      const response = await api.post('/api/contact/submit', formData);

      if (response.data.success) {
        toast.success(response.data.message || 'Message envoyé avec succès!');
        setSubmitted(true);
        setFormData({
          name: user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() : '',
          email: user?.email || '',
          phone: user?.phone || '',
          subject: '',
          message: '',
          category: 'general'
        });

        // Reset submitted state after 5 seconds
        setTimeout(() => setSubmitted(false), 5000);
      }
    } catch (error) {
      console.error('Error submitting contact form:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'envoi du message');
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16">
        <Card>
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Message Envoyé!</h2>
            <p className="text-gray-600 mb-6">
              Merci de nous avoir contactés. Nous vous répondrons dans les plus brefs délais.
            </p>
            <button
              onClick={() => setSubmitted(false)}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              Envoyer un Autre Message
            </button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Contactez-Nous</h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Une question ? Un problème ? Notre équipe est là pour vous aider
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Contact Info - Left Column */}
        <div className="space-y-6">
          {/* Contact Cards */}
          <Card>
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900 mb-4">Coordonnées</h3>

              <div className="flex items-start space-x-3">
                <div className="bg-purple-100 p-2 rounded-lg">
                  <Mail className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <div className="text-sm text-gray-600">Email</div>
                  <div className="font-medium text-gray-900">support@shareyoursales.ma</div>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="bg-green-100 p-2 rounded-lg">
                  <Phone className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <div className="text-sm text-gray-600">Téléphone</div>
                  <div className="font-medium text-gray-900">+212 5 22 XX XX XX</div>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <MapPin className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <div className="text-sm text-gray-600">Adresse</div>
                  <div className="font-medium text-gray-900">
                    Casablanca, Maroc
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* Hours */}
          <Card>
            <h3 className="font-semibold text-gray-900 mb-4">Heures d'Ouverture</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Lundi - Vendredi</span>
                <span className="font-medium text-gray-900">9h - 18h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Samedi</span>
                <span className="font-medium text-gray-900">9h - 13h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Dimanche</span>
                <span className="font-medium text-red-600">Fermé</span>
              </div>
            </div>
          </Card>

          {/* FAQ Link */}
          <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
            <div className="text-center">
              <HelpCircle className="w-12 h-12 text-purple-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Questions Fréquentes</h3>
              <p className="text-sm text-gray-600 mb-4">
                Consultez notre FAQ pour des réponses rapides
              </p>
              <a
                href="/faq"
                className="inline-block px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                Voir la FAQ
              </a>
            </div>
          </Card>
        </div>

        {/* Contact Form - Right Column */}
        <div className="lg:col-span-2">
          <Card>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Envoyez-nous un Message</h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Category Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Catégorie *
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {categories.map((category) => {
                    const Icon = category.icon;
                    return (
                      <button
                        key={category.id}
                        type="button"
                        onClick={() => setFormData({ ...formData, category: category.id })}
                        className={`p-3 border-2 rounded-lg transition-all ${
                          formData.category === category.id
                            ? 'border-purple-500 bg-purple-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div
                          className={`w-8 h-8 ${category.bgColor} rounded-lg flex items-center justify-center mx-auto mb-2`}
                        >
                          <Icon className={`w-5 h-5 ${category.color}`} />
                        </div>
                        <div className="text-xs text-center text-gray-700 font-medium">
                          {category.name}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Name */}
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Nom Complet *
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Votre nom complet"
                />
              </div>

              {/* Email & Phone */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="votre@email.com"
                  />
                </div>

                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                    Téléphone (Optionnel)
                  </label>
                  <input
                    type="tel"
                    id="phone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="+212 6 XX XX XX XX"
                  />
                </div>
              </div>

              {/* Subject */}
              <div>
                <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                  Sujet *
                </label>
                <input
                  type="text"
                  id="subject"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Résumez votre demande en quelques mots"
                />
              </div>

              {/* Message */}
              <div>
                <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                  Message *
                </label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows="6"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Décrivez votre demande en détail..."
                />
              </div>

              {/* Privacy Notice */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-600">
                  En soumettant ce formulaire, vous acceptez que vos données soient utilisées pour
                  traiter votre demande conformément à notre{' '}
                  <a href="/privacy" className="text-purple-600 hover:underline">
                    politique de confidentialité
                  </a>
                  .
                </p>
              </div>

              {/* Submit Button */}
              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {submitting ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" />
                      Envoi en cours...
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5 mr-2" />
                      Envoyer le Message
                    </>
                  )}
                </button>
              </div>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Contact;
