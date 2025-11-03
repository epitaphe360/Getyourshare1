import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import api from '../../utils/api';
import Card from '../common/Card';
import Button from '../common/Button';
import { X, Search, Plus, Check, MessageSquare } from 'lucide-react';

const InvitationModal = ({ onClose, onSent }) => {
  const [users, setUsers] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedProducts, setSelectedProducts] = useState(new Set());
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersRes, productsRes] = await Promise.allSettled([
        api.get('/api/influencers?limit=50'),
        api.get('/api/products')
      ]);

      if (usersRes.status === 'fulfilled') {
        // adapt to possible response shapes
        setUsers(usersRes.value.data.influencers || usersRes.value.data || []);
      } else {
        setUsers([]);
      }

      if (productsRes.status === 'fulfilled') {
        setProducts(productsRes.value.data.products || productsRes.value.data || []);
      } else {
        setProducts([]);
      }
    } catch (err) {
      console.error('Error loading invite modal data', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleProduct = (productId) => {
    const next = new Set(selectedProducts);
    if (next.has(productId)) next.delete(productId);
    else next.add(productId);
    setSelectedProducts(next);
  };

  const sendInvitation = async () => {
    if (!selectedUser) return alert('Sélectionnez un affilié');
    if (selectedProducts.size === 0) return alert('Sélectionnez au moins un produit');
    try {
      setSending(true);
      const payload = {
        invitee_id: selectedUser.id || selectedUser.user_id || selectedUser._id,
        product_ids: Array.from(selectedProducts),
        message
      };

      const res = await api.post('/api/invitations/send', payload);
      if (res.data && res.data.success) {
        if (onSent) onSent(res.data.invitation);
      } else {
        alert(res.data?.message || 'Erreur lors de l\'envoi');
      }
    } catch (err) {
      console.error('Send invitation error', err);
      alert('Erreur lors de l\'envoi de l\'invitation');
    } finally {
      setSending(false);
    }
  };

  const filteredUsers = users.filter(u => {
    const s = search.toLowerCase();
    if (!s) return true;
    return (u.first_name?.toLowerCase().includes(s) || u.last_name?.toLowerCase().includes(s) || u.username?.toLowerCase().includes(s) || u.email?.toLowerCase().includes(s));
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-4xl mx-4">
        <Card className="relative">
          <button onClick={onClose} className="absolute right-4 top-4 p-2 rounded-md hover:bg-gray-100">
            <X />
          </button>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-1">
              <h3 className="text-lg font-semibold">Sélectionnez un affilié</h3>
              <div className="mt-3">
                <div className="relative mb-3">
                  <Search className="absolute left-3 top-3 text-gray-400" size={18} />
                  <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..." className="w-full pl-10 pr-3 py-2 border rounded-lg" />
                </div>

                <div className="h-64 overflow-auto border rounded-lg p-2 space-y-2">
                  {loading ? (
                    <div>Chargement...</div>
                  ) : filteredUsers.length === 0 ? (
                    <div className="text-sm text-gray-500">Aucun affilié trouvé</div>
                  ) : (
                    filteredUsers.map(user => (
                      <div key={user.id || user.user_id || user._id} className={`p-2 rounded-lg hover:bg-gray-50 cursor-pointer ${selectedUser && (selectedUser.id || selectedUser.user_id || selectedUser._id) === (user.id || user.user_id || user._id) ? 'bg-indigo-50 border border-indigo-200' : ''}`} onClick={() => setSelectedUser(user)}>
                        <div className="font-medium">{user.first_name} {user.last_name} {user.username ? `(${user.username})` : ''}</div>
                        <div className="text-xs text-gray-500">{user.email}</div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            <div className="md:col-span-2">
              <h3 className="text-lg font-semibold">Sélectionnez les produits</h3>
              <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 max-h-60 overflow-auto">
                {products.length === 0 ? (
                  <div className="text-sm text-gray-500">Aucun produit</div>
                ) : products.map(prod => (
                  <div key={prod.id || prod._id} className="flex items-center gap-3 p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium">{prod.name || prod.title}</div>
                      <div className="text-sm text-gray-500">{prod.price ? `${prod.price}€` : ''}</div>
                    </div>
                    <div>
                      <input type="checkbox" checked={selectedProducts.has(prod.id || prod._id)} onChange={() => toggleProduct(prod.id || prod._id)} />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4">
                <h4 className="font-medium">Message</h4>
                <textarea value={message} onChange={e => setMessage(e.target.value)} placeholder="Message optionnel à l'affilié" className="w-full mt-2 p-3 border rounded-lg h-28"></textarea>
              </div>

              <div className="mt-4 flex items-center gap-3 justify-end">
                <Button onClick={onClose} className="bg-gray-100 text-gray-800">Annuler</Button>
                <Button onClick={sendInvitation} disabled={sending} className="bg-indigo-600 text-white">
                  {sending ? 'Envoi...' : (<><MessageSquare size={16} className="inline mr-2"/> Envoyer l'invitation</>)}
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

InvitationModal.propTypes = {
  onClose: PropTypes.func.isRequired,
  onSent: PropTypes.func,
};

export default InvitationModal;
