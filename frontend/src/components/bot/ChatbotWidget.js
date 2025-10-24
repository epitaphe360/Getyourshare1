/**
 * Widget Chatbot IA Ultra Sophistiqué
 *
 * Fonctionnalités:
 * - Interface conversationnelle moderne
 * - Support multilingue (FR, EN, AR)
 * - Suggestions contextuelles
 * - Indicateur de frappe
 * - Historique des conversations
 * - Mode sombre/clair
 * - Feedback sur les réponses
 * - Animations fluides
 * - Raccourcis clavier
 * - Voice input (optionnel)
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../../services/api';

const ChatbotWidget = ({ user, language = 'fr' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll vers le bas quand nouveau message
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Focus sur l'input quand le chat s'ouvre
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Charger suggestions au montage
  useEffect(() => {
    if (isOpen && suggestions.length === 0) {
      loadSuggestions();
    }
  }, [isOpen]);

  // Message de bienvenue
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          role: 'assistant',
          content: getWelcomeMessage(),
          timestamp: new Date(),
        },
      ]);
    }
  }, [isOpen]);

  const getWelcomeMessage = () => {
    const welcomeMessages = {
      fr: `👋 Bonjour ${user?.full_name || ''}! Je suis ShareBot, votre assistant intelligent.\n\nComment puis-je vous aider aujourd'hui?`,
      en: `👋 Hello ${user?.full_name || ''}! I'm ShareBot, your intelligent assistant.\n\nHow can I help you today?`,
      ar: `👋 مرحبا ${user?.full_name || ''}! أنا ShareBot، مساعدك الذكي.\n\nكيف يمكنني مساعدتك اليوم؟`,
    };
    return welcomeMessages[language] || welcomeMessages.fr;
  };

  const loadSuggestions = async () => {
    try {
      const response = await api.get('/api/bot/suggestions');
      setSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const loadConversationHistory = async () => {
    try {
      const response = await api.get('/api/bot/conversations', {
        params: { limit: 10 },
      });
      setConversationHistory(response.data || []);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const sendMessage = async (messageText = null) => {
    const textToSend = messageText || inputValue.trim();

    if (!textToSend) return;

    // Ajouter message utilisateur
    const userMessage = {
      role: 'user',
      content: textToSend,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await api.post('/api/bot/chat', {
        message: textToSend,
        language: language,
        session_id: sessionId,
      });

      // Sauvegarder session ID
      if (!sessionId) {
        setSessionId(response.data.session_id);
      }

      // Ajouter réponse bot
      const botMessage = {
        role: 'assistant',
        content: response.data.bot_response,
        timestamp: new Date(response.data.timestamp),
        intent: response.data.intent_detected,
        action: response.data.action_executed,
      };
      setMessages((prev) => [...prev, botMessage]);

      // Mettre à jour suggestions
      if (response.data.suggestions) {
        setSuggestions(response.data.suggestions);
      }
    } catch (error) {
      console.error('Error sending message:', error);

      // Message d'erreur
      const errorMessage = {
        role: 'assistant',
        content: '😔 Désolé, une erreur est survenue. Veuillez réessayer.',
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  const handleFeedback = async (messageIndex, rating) => {
    // TODO: Envoyer feedback au backend
    console.log('Feedback:', messageIndex, rating);
  };

  const clearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: getWelcomeMessage(),
        timestamp: new Date(),
      },
    ]);
    setSessionId(null);
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <>
      {/* Bouton flottant */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full shadow-lg flex items-center justify-center text-white text-2xl z-50 hover:shadow-xl transition-shadow"
          >
            🤖
          </motion.button>
        )}
      </AnimatePresence>

      {/* Widget Chatbot */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            className={`fixed bottom-6 right-6 w-[400px] h-[600px] rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden ${
              isDarkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'
            }`}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-2xl">
                  🤖
                </div>
                <div>
                  <h3 className="font-bold text-white">ShareBot</h3>
                  <p className="text-xs text-purple-100">
                    {isTyping ? 'En train d\'écrire...' : 'En ligne'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {/* Dark mode toggle */}
                <button
                  onClick={toggleDarkMode}
                  className="p-2 hover:bg-white/20 rounded-full transition"
                >
                  {isDarkMode ? '☀️' : '🌙'}
                </button>

                {/* History */}
                <button
                  onClick={() => {
                    setShowHistory(!showHistory);
                    if (!showHistory) loadConversationHistory();
                  }}
                  className="p-2 hover:bg-white/20 rounded-full transition"
                >
                  📜
                </button>

                {/* Clear */}
                <button
                  onClick={clearChat}
                  className="p-2 hover:bg-white/20 rounded-full transition"
                >
                  🗑️
                </button>

                {/* Close */}
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-white/20 rounded-full transition"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Historique des conversations (si ouvert) */}
            {showHistory ? (
              <div className="flex-1 overflow-y-auto p-4">
                <h4 className="font-bold mb-3">Conversations récentes</h4>
                {conversationHistory.length > 0 ? (
                  <div className="space-y-2">
                    {conversationHistory.map((conv) => (
                      <div
                        key={conv.session_id}
                        className="p-3 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 cursor-pointer transition"
                        onClick={() => {
                          // TODO: Charger conversation
                          setShowHistory(false);
                        }}
                      >
                        <p className="text-sm font-medium">
                          {new Date(conv.created_at).toLocaleDateString()}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          {conv.message_count} messages
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">Aucun historique</p>
                )}
              </div>
            ) : (
              <>
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((msg, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex ${
                        msg.role === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      <div
                        className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                          msg.role === 'user'
                            ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                            : isDarkMode
                            ? 'bg-gray-800 text-white'
                            : 'bg-gray-100 text-gray-900'
                        } ${msg.isError ? 'border-2 border-red-500' : ''}`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {msg.timestamp.toLocaleTimeString('fr-FR', {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>

                        {/* Feedback buttons (seulement pour bot) */}
                        {msg.role === 'assistant' && !msg.isError && (
                          <div className="flex gap-2 mt-2">
                            <button
                              onClick={() => handleFeedback(index, 5)}
                              className="text-xs hover:scale-110 transition"
                            >
                              👍
                            </button>
                            <button
                              onClick={() => handleFeedback(index, 1)}
                              className="text-xs hover:scale-110 transition"
                            >
                              👎
                            </button>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}

                  {/* Indicateur de frappe */}
                  {isTyping && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex justify-start"
                    >
                      <div
                        className={`rounded-2xl px-4 py-2 ${
                          isDarkMode ? 'bg-gray-800' : 'bg-gray-100'
                        }`}
                      >
                        <div className="flex gap-1">
                          <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></span>
                          <span
                            className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                            style={{ animationDelay: '0.1s' }}
                          ></span>
                          <span
                            className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                            style={{ animationDelay: '0.2s' }}
                          ></span>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Suggestions */}
                {suggestions.length > 0 && (
                  <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                      Suggestions:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {suggestions.slice(0, 3).map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => handleSuggestionClick(suggestion)}
                          className={`text-xs px-3 py-1 rounded-full ${
                            isDarkMode
                              ? 'bg-gray-800 hover:bg-gray-700'
                              : 'bg-gray-100 hover:bg-gray-200'
                          } transition`}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Input */}
                <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex gap-2">
                    <input
                      ref={inputRef}
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Tapez votre message..."
                      className={`flex-1 px-4 py-2 rounded-full border-2 ${
                        isDarkMode
                          ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-500'
                          : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400'
                      } focus:border-purple-500 focus:outline-none transition`}
                    />
                    <button
                      onClick={() => sendMessage()}
                      disabled={!inputValue.trim() || isTyping}
                      className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
                    >
                      ➤
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
                    Appuyez sur Entrée pour envoyer
                  </p>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatbotWidget;
