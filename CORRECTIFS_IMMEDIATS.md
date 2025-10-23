# 🚀 CORRECTIFS IMMÉDIATS - SHAREYOURSALES

## ✅ ACTIONS À EFFECTUER (2-3 HEURES)

### 1. ACTIVER LES COMPOSANTS CACHÉS

#### A. Créer CreateCampaign.js dans pages (pas components/forms)
```bash
# Déplacer le fichier
mv frontend/src/components/forms/CreateCampaign.js frontend/src/pages/campaigns/CreateCampaign.js
```

#### B. Créer InfluencerSearch.js dans pages (pas components/search)
```bash
mv frontend/src/components/search/InfluencerSearch.js frontend/src/pages/influencers/InfluencerSearchAdvanced.js
```

---

### 2. MODIFIER App.js - AJOUTER ROUTES

**Fichier**: `frontend/src/App.js`

**Après la ligne** `import CampaignsList from './pages/campaigns/CampaignsList';`

**Ajouter**:
```javascript
import CreateCampaign from './pages/campaigns/CreateCampaign';
import InfluencerSearchAdvanced from './pages/influencers/InfluencerSearchAdvanced';
```

**Dans la section `<Routes>`, après** `<Route path="/campaigns" element={<CampaignsList />} />`

**Ajouter**:
```javascript
<Route path="/campaigns/create" element={<CreateCampaign />} />
<Route path="/influencers/search" element={<InfluencerSearchAdvanced />} />
```

---

### 3. AJOUTER BOUTONS DANS MERCHANTDASHBOARD

**Fichier**: `frontend/src/pages/dashboards/MerchantDashboard.js`

**Remplacer le bouton existant** (ligne ~80):
```javascript
<button 
  onClick={() => navigate('/products/new')}
  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
>
  + Ajouter Produit
</button>
```

**Par**:
```javascript
<div className="flex space-x-3">
  <button 
    onClick={() => navigate('/campaigns/create')}
    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
  >
    + Créer Campagne
  </button>
  <button 
    onClick={() => navigate('/influencers/search')}
    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
  >
    🔍 Rechercher Influenceurs
  </button>
</div>
```

---

### 4. AJOUTER BOUTON DANS CAMPAIGNSLIST

**Fichier**: `frontend/src/pages/campaigns/CampaignsList.js`

**Après** `<h1 className="text-3xl font-bold text-gray-900">Campagnes</h1>`

**Ajouter**:
```javascript
<div className="flex justify-between items-center mb-6">
  <div>
    <h1 className="text-3xl font-bold text-gray-900">Campagnes</h1>
    <p className="text-gray-600 mt-2">Gérez vos campagnes d'affiliation</p>
  </div>
  <button
    onClick={() => navigate('/campaigns/create')}
    className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition font-semibold"
  >
    + Créer une Campagne
  </button>
</div>
```

**Ajouter l'import** en haut du fichier:
```javascript
import { useNavigate } from 'react-router-dom';

// Dans le composant
const navigate = useNavigate();
```

---

### 5. INTÉGRER FILEUPLOAD DANS CREATECAMPAIGN

**Fichier**: `frontend/src/pages/campaigns/CreateCampaign.js`

**Ajouter l'import** (ligne ~3):
```javascript
import FileUpload from '../../components/common/FileUpload';
```

**Ajouter state pour fichiers** (après les autres useState):
```javascript
const [uploadedFiles, setUploadedFiles] = useState([]);
```

**Ajouter section Upload** (après la section Briefing, avant les boutons):
```javascript
{/* Section 7: Upload Matériel Promotionnel */}
<Card title="📎 Matériel Promotionnel" icon={<Upload size={20} />}>
  <div className="space-y-4">
    <p className="text-sm text-gray-600">
      Uploadez logos, bannières, images produits, kits de presse, etc.
    </p>
    
    <FileUpload
      onUploadComplete={(urls) => {
        setUploadedFiles([...uploadedFiles, ...urls]);
        console.log('Fichiers uploadés:', urls);
      }}
      accept="image/*,.pdf,.zip"
      maxFiles={10}
      maxSize={10 * 1024 * 1024} // 10MB
    />

    {uploadedFiles.length > 0 && (
      <div className="mt-4">
        <p className="text-sm font-medium text-gray-700 mb-2">
          Fichiers uploadés ({uploadedFiles.length}):
        </p>
        <div className="space-y-2">
          {uploadedFiles.map((file, idx) => (
            <div key={idx} className="flex items-center justify-between bg-gray-50 p-2 rounded">
              <span className="text-sm text-gray-700">{file.name || `Fichier ${idx + 1}`}</span>
              <button
                onClick={() => setUploadedFiles(uploadedFiles.filter((_, i) => i !== idx))}
                className="text-red-600 hover:text-red-800 text-sm"
              >
                Supprimer
              </button>
            </div>
          ))}
        </div>
      </div>
    )}
  </div>
</Card>
```

**Ajouter fichiers dans la soumission** (fonction handleSubmit):
```javascript
const campaignData = {
  // ... données existantes
  uploaded_files: uploadedFiles, // AJOUTER CETTE LIGNE
};
```

---

### 6. FIXER MODULE INFLUENCER_SEARCH NON TROUVÉ

**Fichier**: `backend/advanced_endpoints.py`

**Ligne ~486**, remplacer:
```python
# Ajouter les endpoints de recherche d'influenceurs
try:
    from influencer_search_endpoints import add_influencer_search_endpoints
    add_influencer_search_endpoints(app, verify_token)
    print("✅ Endpoints de recherche d'influenceurs intégrés")
except ImportError:
    print("⚠️  Module influencer_search_endpoints non trouvé")
```

**Par**:
```python
# Ajouter les endpoints de recherche d'influenceurs
try:
    from influencer_search_endpoints import add_influencer_search_endpoints
    add_influencer_search_endpoints(app, verify_token)
    print("✅ Endpoints de recherche d'influenceurs intégrés")
except ImportError as e:
    print(f"⚠️  Module influencer_search_endpoints non trouvé: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Erreur lors du chargement influencer_search_endpoints: {e}")
    import traceback
    traceback.print_exc()
```

**Vérifier que le fichier existe**:
```bash
ls backend/influencer_search_endpoints.py
```

---

### 7. CRÉER ENDPOINT LEADS (CORRIGER MOCK DATA)

**Fichier**: `backend/advanced_endpoints.py`

**Ajouter à la fin** (avant `integrate_all_endpoints`):
```python
def add_leads_endpoints(app, verify_token):
    """Ajoute les endpoints pour les leads"""
    
    @app.get("/api/leads")
    async def get_leads(
        status: Optional[str] = None,
        campaign_id: Optional[str] = None,
        current_user: dict = Depends(verify_token)
    ):
        """Récupère les leads (conversions en attente de validation)"""
        try:
            supabase = get_supabase_client()
            
            # Base query
            query = supabase.table('sales').select(
                '*, products(name), users(first_name, last_name, email)'
            ).eq('status', 'pending')
            
            # Filtres
            if status:
                query = query.eq('status', status)
            if campaign_id:
                query = query.eq('campaign_id', campaign_id)
            
            # Filtrer par merchant si non admin
            if current_user['role'] == 'merchant':
                merchant = supabase.table('merchants').select('id').eq(
                    'user_id', current_user['user_id']
                ).single().execute()
                
                if merchant.data:
                    query = query.eq('merchant_id', merchant.data['id'])
            
            result = query.order('created_at', desc=True).execute()
            
            # Formatter les leads
            leads = []
            for sale in result.data:
                leads.append({
                    'id': sale['id'],
                    'email': sale['users']['email'] if sale.get('users') else 'N/A',
                    'campaign': sale.get('campaign_name', 'N/A'),
                    'affiliate': f"{sale['users']['first_name']} {sale['users']['last_name']}" if sale.get('users') else 'N/A',
                    'status': sale['status'],
                    'amount': sale.get('amount', 0),
                    'created_at': sale['created_at']
                })
            
            return {"leads": leads, "total": len(leads)}
            
        except Exception as e:
            print(f"Error fetching leads: {e}")
            raise HTTPException(status_code=500, detail=str(e))
```

**Puis dans `integrate_all_endpoints`, ajouter**:
```python
add_leads_endpoints(app, verify_token)
print("✅ Endpoints leads intégrés")
```

---

### 8. MODIFIER LEADS.JS POUR UTILISER API

**Fichier**: `frontend/src/pages/performance/Leads.js`

**Remplacer tout le contenu par**:
```javascript
import React, { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import { formatDate } from '../../utils/helpers';
import api from '../../utils/api';

const Leads = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const response = await api.get('/api/leads');
      setLeads(response.data.leads || []);
    } catch (error) {
      console.error('Error fetching leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      header: 'ID',
      accessor: 'id',
      render: (row) => <span className="font-mono text-sm">{row.id.substring(0, 8)}</span>,
    },
    {
      header: 'Email',
      accessor: 'email',
    },
    {
      header: 'Campagne',
      accessor: 'campaign',
    },
    {
      header: 'Affilié',
      accessor: 'affiliate',
    },
    {
      header: 'Montant',
      accessor: 'amount',
      render: (row) => `${row.amount?.toFixed(2) || 0} €`,
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => <Badge status={row.status}>{row.status}</Badge>,
    },
    {
      header: 'Date',
      accessor: 'created_at',
      render: (row) => formatDate(row.created_at),
    },
  ];

  if (loading) {
    return <div className="text-center py-12">Chargement...</div>;
  }

  return (
    <div className="space-y-6" data-testid="leads">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Leads</h1>
        <p className="text-gray-600 mt-2">
          {leads.length} leads générés en attente de validation
        </p>
      </div>

      <Card>
        {leads.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            Aucun lead pour le moment
          </div>
        ) : (
          <Table columns={columns} data={leads} />
        )}
      </Card>
    </div>
  );
};

export default Leads;
```

---

### 9. CRÉER ENDPOINT DASHBOARD CHARTS

**Fichier**: `backend/advanced_endpoints.py`

**Ajouter**:
```python
def add_dashboard_charts_endpoints(app, verify_token):
    """Endpoints pour graphiques dashboards"""
    
    @app.get("/api/dashboard/charts/sales")
    async def get_sales_chart_data(
        days: int = 7,
        current_user: dict = Depends(verify_token)
    ):
        """Données graphique ventes (7 derniers jours)"""
        try:
            supabase = get_supabase_client()
            
            # Calculer date de début
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Query ventes par jour
            query = supabase.table('sales').select('amount, created_at').gte(
                'created_at', start_date
            )
            
            # Filtrer par merchant si nécessaire
            if current_user['role'] == 'merchant':
                merchant = supabase.table('merchants').select('id').eq(
                    'user_id', current_user['user_id']
                ).single().execute()
                if merchant.data:
                    query = query.eq('merchant_id', merchant.data['id'])
            
            result = query.execute()
            
            # Grouper par jour
            sales_by_day = {}
            for sale in result.data:
                day = sale['created_at'][:10]  # YYYY-MM-DD
                if day not in sales_by_day:
                    sales_by_day[day] = {'ventes': 0, 'revenus': 0}
                sales_by_day[day]['ventes'] += 1
                sales_by_day[day]['revenus'] += sale.get('amount', 0)
            
            # Formatter pour frontend
            chart_data = [
                {
                    'date': day,
                    'ventes': data['ventes'],
                    'revenus': round(data['revenus'], 2)
                }
                for day, data in sorted(sales_by_day.items())
            ]
            
            return {"data": chart_data}
            
        except Exception as e:
            print(f"Error fetching sales chart: {e}")
            raise HTTPException(status_code=500, detail=str(e))
```

**Intégrer dans** `integrate_all_endpoints`:
```python
add_dashboard_charts_endpoints(app, verify_token)
print("✅ Endpoints dashboard charts intégrés")
```

---

### 10. MODIFIER MERCHANTDASHBOARD POUR UTILISER VRAIES DONNÉES

**Fichier**: `frontend/src/pages/dashboards/MerchantDashboard.js`

**Remplacer la section mock data** (ligne ~43):
```javascript
// SUPPRIMER:
// const salesData = [ ... ];

// AJOUTER:
const [salesData, setSalesData] = useState([]);

useEffect(() => {
  fetchChartData();
}, []);

const fetchChartData = async () => {
  try {
    const response = await api.get('/api/dashboard/charts/sales?days=7');
    setSalesData(response.data.data || []);
  } catch (error) {
    console.error('Error fetching chart data:', error);
  }
};
```

---

## 🧪 TESTS À EFFECTUER

### 1. Test Navigation
```
✅ Cliquer "Créer Campagne" depuis MerchantDashboard
✅ Remplir formulaire CreateCampaign
✅ Upload fichiers avec FileUpload
✅ Soumettre campagne
✅ Vérifier création dans BDD
```

### 2. Test Recherche Influenceurs
```
✅ Aller sur /influencers/search
✅ Filtrer par catégorie
✅ Filtrer par followers min/max
✅ Trier par engagement
✅ Vérifier résultats
```

### 3. Test Leads
```
✅ Aller sur /performance/leads
✅ Vérifier chargement depuis API
✅ Pas de données mock
✅ Affichage correct
```

### 4. Test Dashboard Charts
```
✅ Aller sur MerchantDashboard
✅ Vérifier graphique ventes (7 jours)
✅ Données réelles (pas 12, 19, 15...)
✅ Chiffres cohérents avec BDD
```

---

## 🚀 COMMANDES POUR APPLIQUER LES CHANGEMENTS

```bash
# 1. Backend: Redémarrer le serveur
cd backend
python server.py

# 2. Frontend: Rebuild
cd frontend
npm run build

# 3. Frontend: Lancer en dev pour tester
npm start

# 4. Tester les routes:
# http://localhost:3000/campaigns/create
# http://localhost:3000/influencers/search
# http://localhost:3000/performance/leads
```

---

## ✅ CHECKLIST FINALE

- [ ] Routes ajoutées dans App.js
- [ ] Boutons navigation ajoutés
- [ ] FileUpload intégré dans CreateCampaign
- [ ] Endpoint /api/leads créé
- [ ] Endpoint /api/dashboard/charts/sales créé
- [ ] Leads.js utilise API
- [ ] MerchantDashboard utilise vraies données
- [ ] Module influencer_search mieux debuggé
- [ ] Serveur redémarré
- [ ] Frontend rebuild
- [ ] Tests navigation OK
- [ ] Tests upload fichiers OK
- [ ] Tests recherche influenceurs OK
- [ ] Données mock remplacées

---

**Estimation temps**: 2-3 heures  
**Impact**: Passe de 70% à 85% de complétude  
**Priorité**: 🔴 HAUTE - Quick wins

**Une fois terminé, l'application sera pleinement fonctionnelle pour les use cases principaux !**
