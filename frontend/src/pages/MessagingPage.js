import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import {
  MessageSquare, Send, ArrowLeft, User, Search,
  CheckCheck, Check, Circle
} from 'lucide-react';
import { formatDate } from '../utils/helpers';

const MessagingPage = () => {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (conversationId && conversations.length > 0) {
      const conv = conversations.find(c => c.id === conversationId);
      if (conv) {
        setActiveConversation(conv);
        fetchMessages(conversationId);
      }
    }
  }, [conversationId, conversations]);

  useEffect(() => {
    // Auto-scroll vers le bas quand nouveaux messages
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const response = await api.get('/api/messages/conversations');
      setConversations(response.data.conversations || []);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (convId) => {
    try {
      const response = await api.get(`/api/messages/${convId}`);
      setMessages(response.data.messages || []);
      setActiveConversation(response.data.conversation);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !activeConversation) return;

    setSending(true);
    try {
      // Déterminer le destinataire
      const isUser1 = activeConversation.user1_id === user.id;
      const recipientId = isUser1 ? activeConversation.user2_id : activeConversation.user1_id;
      const recipientType = isUser1 ? activeConversation.user2_type : activeConversation.user1_type;

      await api.post('/api/messages/send', {
        recipient_id: recipientId,
        recipient_type: recipientType,
        content: newMessage,
        campaign_id: activeConversation.campaign_id
      });

      setNewMessage('');
      await fetchMessages(activeConversation.id);
      await fetchConversations(); // Rafraîchir la liste
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Erreur lors de l\'envoi du message');
    } finally {
      setSending(false);
    }
  };

  const getOtherUserName = (conversation) => {
    if (!conversation) return '';
    const isUser1 = conversation.user1_id === user?.id;
    const otherType = isUser1 ? conversation.user2_type : conversation.user1_type;
    return `${otherType.charAt(0).toUpperCase() + otherType.slice(1)} #${isUser1 ? conversation.user2_id.substring(0, 8) : conversation.user1_id.substring(0, 8)}`;
  };

  const filteredConversations = conversations.filter(conv =>
    getOtherUserName(conv).toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.subject?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl">Chargement des messages...</div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-120px)]">
      <div className="flex h-full gap-6">
        {/* Liste des conversations - Sidebar */}
        <div className="w-80 flex-shrink-0">
          <Card className="h-full flex flex-col">
            <div className="p-4 border-b">
              <h2 className="text-xl font-bold mb-4">Messages</h2>
              
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Rechercher..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            {/* Conversations list */}
            <div className="flex-1 overflow-y-auto">
              {filteredConversations.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  <MessageSquare size={48} className="mx-auto mb-3 text-gray-300" />
                  <p>Aucune conversation</p>
                  <p className="text-sm mt-1">Commencez à échanger avec des influenceurs</p>
                </div>
              ) : (
                filteredConversations.map((conv) => (
                  <div
                    key={conv.id}
                    onClick={() => navigate(`/messages/${conv.id}`)}
                    className={`p-4 border-b cursor-pointer hover:bg-gray-50 transition ${
                      activeConversation?.id === conv.id ? 'bg-indigo-50 border-l-4 border-indigo-600' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <User size={20} className="text-gray-600" />
                        <span className="font-semibold text-sm">{getOtherUserName(conv)}</span>
                      </div>
                      {conv.unread_count > 0 && (
                        <span className="bg-indigo-600 text-white text-xs rounded-full px-2 py-0.5">
                          {conv.unread_count}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 font-medium mb-1">{conv.subject}</p>
                    {conv.last_message && (
                      <p className="text-xs text-gray-500 truncate">
                        {conv.last_message.content}
                      </p>
                    )}
                    <p className="text-xs text-gray-400 mt-1">
                      {formatDate(conv.last_message_at)}
                    </p>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>

        {/* Zone de conversation */}
        <div className="flex-1">
          {activeConversation ? (
            <Card className="h-full flex flex-col">
              {/* Header conversation */}
              <div className="p-4 border-b flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => navigate('/messages')}
                    className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
                  >
                    <ArrowLeft size={20} />
                  </button>
                  <div className="bg-indigo-100 w-10 h-10 rounded-full flex items-center justify-center">
                    <User size={20} className="text-indigo-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{getOtherUserName(activeConversation)}</h3>
                    <p className="text-sm text-gray-500">{activeConversation.subject}</p>
                  </div>
                </div>
                <Circle size={12} className="text-green-500 fill-green-500" />
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 mt-12">
                    <MessageSquare size={48} className="mx-auto mb-3 text-gray-300" />
                    <p>Aucun message encore</p>
                    <p className="text-sm mt-1">Commencez la conversation !</p>
                  </div>
                ) : (
                  messages.map((msg, idx) => {
                    const isOwn = msg.sender_id === user?.id;
                    return (
                      <div
                        key={msg.id}
                        className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-md px-4 py-2 rounded-lg ${
                            isOwn
                              ? 'bg-indigo-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                          <div className={`flex items-center gap-1 mt-1 text-xs ${isOwn ? 'text-indigo-200' : 'text-gray-500'}`}>
                            <span>{new Date(msg.created_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</span>
                            {isOwn && (
                              msg.is_read ? <CheckCheck size={14} /> : <Check size={14} />
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input message */}
              <div className="p-4 border-t">
                <form onSubmit={handleSendMessage} className="flex gap-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Écrivez votre message..."
                    className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    disabled={sending}
                  />
                  <Button type="submit" disabled={sending || !newMessage.trim()}>
                    <Send size={20} />
                  </Button>
                </form>
              </div>
            </Card>
          ) : (
            <Card className="h-full flex items-center justify-center">
              <div className="text-center text-gray-500">
                <MessageSquare size={64} className="mx-auto mb-4 text-gray-300" />
                <p className="text-xl font-semibold mb-2">Sélectionnez une conversation</p>
                <p>Choisissez une conversation dans la liste pour commencer à échanger</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessagingPage;
