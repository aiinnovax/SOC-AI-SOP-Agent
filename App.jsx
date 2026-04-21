import React, { useState, useEffect } from 'react';
import { initializeApp } from "firebase/app";
import { 
  getAuth, 
  signInAnonymously, 
  signInWithCustomToken, 
  onAuthStateChanged 
} from "firebase/auth";
import { 
  getFirestore, 
  collection, 
  onSnapshot,
  doc,
  setDoc,
  addDoc,
  serverTimestamp
} from "firebase/firestore";
import { 
  Shield, 
  Users, 
  FileText, 
  Activity, 
  Database, 
  LayoutDashboard, 
  AlertCircle,
  Bell,
  Search,
  Key,
  ExternalLink,
  ChevronRight,
  Settings,
  Plus,
  PlusCircle,
  Trash2,
  Save,
  X
} from 'lucide-react';

/**
 * AIInnovax Firebase Configuration
 */
const firebaseConfig = {
  apiKey: "AIzaSyD4jTLlcwSlq9N3YuvBhPLCmnBtUyhRMfs",
  authDomain: "soc-ai-sop-agent.firebaseapp.com",
  projectId: "soc-ai-sop-agent",
  storageBucket: "soc-ai-sop-agent.firebasestorage.app",
  messagingSenderId: "785445958281",
  appId: "1:785445958281:web:c00b3a13cf79d481fa0c58"
};

const isConfigValid = firebaseConfig.apiKey !== "YOUR_API_KEY" && firebaseConfig.apiKey !== "";

export default function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [customers, setCustomers] = useState([]);
  const [sops, setSops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);
  
  // Client Management State
  const [showAddClient, setShowAddClient] = useState(false);
  const [newClient, setNewClient] = useState({ name: '', siem: 'Sentinel', logSources: '' });

  useEffect(() => {
    if (!isConfigValid) {
      setLoading(false);
      return;
    }

    let auth, db, unsubCustomers, unsubSops, unsubscribeAuth;

    try {
      const app = initializeApp(firebaseConfig);
      auth = getAuth(app);
      db = getFirestore(app);
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';

      const initAuth = async () => {
        try {
          if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
            try {
              await signInWithCustomToken(auth, __initial_auth_token);
            } catch (tokenErr) {
              await signInAnonymously(auth);
            }
          } else {
            await signInAnonymously(auth);
          }
        } catch (error) {
          if (error.code === 'auth/admin-restricted-operation') {
            setAuthError("Anonymous Authentication is disabled. Please enable it in the Firebase Console.");
          } else {
            setAuthError(`Authentication error: ${error.message}`);
          }
        }
      };
      initAuth();

      unsubscribeAuth = onAuthStateChanged(auth, (u) => {
        setUser(u);
        setLoading(false);
        
        if (u) {
          // Rule 1: Public data path
          const customersRef = collection(db, 'artifacts', appId, 'public', 'data', 'customers');
          const sopsRef = collection(db, 'artifacts', appId, 'public', 'data', 'sops');

          unsubCustomers = onSnapshot(customersRef, (snapshot) => {
            setCustomers(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
          });

          unsubSops = onSnapshot(sopsRef, (snapshot) => {
            setSops(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
          });
        }
      });

    } catch (err) {
      setAuthError("Failed to initialize Firebase.");
      setLoading(false);
    }

    return () => {
      if (unsubscribeAuth) unsubscribeAuth();
      if (unsubCustomers) unsubCustomers();
      if (unsubSops) unsubSops();
    };
  }, []);

  const handleAddClient = async (e) => {
    e.preventDefault();
    if (!user || !newClient.name) return;

    try {
      const app = initializeApp(firebaseConfig);
      const db = getFirestore(app);
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      
      const customersRef = collection(db, 'artifacts', appId, 'public', 'data', 'customers');
      await addDoc(customersRef, {
        ...newClient,
        createdAt: serverTimestamp(),
        activeSops: 0,
        tier: 'Standard'
      });
      
      setNewClient({ name: '', siem: 'Sentinel', logSources: '' });
      setShowAddClient(false);
    } catch (err) {
      console.error("Error adding client:", err);
    }
  };

  if (!isConfigValid || authError) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-slate-900 text-white p-6">
        <div className="max-w-md w-full bg-slate-800 rounded-2xl p-8 border border-slate-700 shadow-2xl text-center">
          <Settings size={48} className="mx-auto mb-6 text-blue-500 animate-pulse" />
          <h2 className="text-2xl font-bold mb-4">Action Required</h2>
          <p className="text-slate-400 mb-6">{authError || "Firebase Config invalid."}</p>
          <a href="https://console.firebase.google.com/" target="_blank" className="bg-blue-600 block py-3 rounded-xl font-bold">Open Firebase Console</a>
        </div>
      </div>
    );
  }

  if (loading) return (
    <div className="h-screen w-full flex items-center justify-center bg-slate-50 text-blue-600">
      <Activity className="animate-spin mr-2" /> Initializing AIInnovax...
    </div>
  );

  return (
    <div className="flex bg-slate-50 h-screen overflow-hidden font-sans text-slate-900">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col border-r border-slate-800">
        <div className="p-6 flex items-center gap-3">
          <Shield className="text-blue-500" size={28} />
          <span className="font-bold text-xl tracking-tight">AIInnovax</span>
        </div>
        <nav className="flex-1 px-4 py-6 space-y-2">
          <button onClick={() => setActiveTab('dashboard')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition ${activeTab === 'dashboard' ? 'bg-blue-600 shadow-lg shadow-blue-900/20' : 'hover:bg-slate-800'}`}>
            <LayoutDashboard size={20} /> Dashboard
          </button>
          <button onClick={() => setActiveTab('clients')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition ${activeTab === 'clients' ? 'bg-blue-600 shadow-lg shadow-blue-900/20' : 'hover:bg-slate-800'}`}>
            <Users size={20} /> Client Management
          </button>
          <button onClick={() => setActiveTab('repository')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition ${activeTab === 'repository' ? 'bg-blue-600 shadow-lg shadow-blue-900/20' : 'hover:bg-slate-800'}`}>
            <Database size={20} /> SOP Repository
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <header className="bg-white border-b px-8 py-4 flex justify-between items-center sticky top-0 z-10 shadow-sm">
          <h2 className="text-xl font-bold capitalize">{activeTab}</h2>
          <div className="flex items-center gap-4">
            <Bell className="text-slate-400 cursor-pointer" size={20} />
            <div className="flex items-center gap-3 bg-slate-50 px-3 py-1.5 rounded-full border">
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold">AD</div>
              <span className="text-sm font-semibold">Administrator</span>
            </div>
          </div>
        </header>

        <div className="p-8 max-w-7xl mx-auto">
          {activeTab === 'dashboard' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-in fade-in slide-in-from-top-4 duration-500">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p className="text-slate-400 text-sm">Active Clients</p>
                <h3 className="text-3xl font-bold mt-1">{customers.length}</h3>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p className="text-slate-400 text-sm">Managed SOPs</p>
                <h3 className="text-3xl font-bold mt-1">{sops.length}</h3>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p className="text-slate-400 text-sm">AI Health</p>
                <h3 className="text-3xl font-bold mt-1 text-green-500">99.9%</h3>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p className="text-slate-400 text-sm">Monthly Tokens</p>
                <h3 className="text-3xl font-bold mt-1">4.2M</h3>
              </div>
            </div>
          )}

          {activeTab === 'clients' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-2xl font-bold">Organization Directory</h3>
                  <p className="text-slate-400">Add clients and configure their environment-specific log sources</p>
                </div>
                <button 
                  onClick={() => setShowAddClient(true)}
                  className="bg-blue-600 text-white px-5 py-2.5 rounded-xl font-bold flex items-center gap-2 hover:bg-blue-700 transition shadow-lg shadow-blue-200"
                >
                  <Plus size={18} /> Add New Client
                </button>
              </div>

              {/* Client List */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {customers.map((client) => (
                  <div key={client.id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-300 transition">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center gap-3">
                        <div className="bg-slate-100 p-2.5 rounded-xl text-blue-600">
                          <Shield size={20} />
                        </div>
                        <div>
                          <h4 className="font-bold text-lg">{client.name}</h4>
                          <span className="text-[10px] uppercase font-black bg-blue-50 text-blue-600 px-2 py-0.5 rounded tracking-widest">{client.siem}</span>
                        </div>
                      </div>
                      <Settings className="text-slate-300 cursor-pointer hover:text-slate-600" size={18} />
                    </div>
                    <div className="space-y-3">
                      <div>
                        <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Integrated Log Sources</p>
                        <div className="flex flex-wrap gap-1.5">
                          {client.logSources?.split(',').map((log, i) => (
                            <span key={i} className="text-[10px] bg-slate-50 border border-slate-100 px-2 py-1 rounded text-slate-600 font-medium">
                              {log.trim()}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="flex justify-between items-center pt-4 border-t border-slate-50 mt-4">
                        <div className="text-xs font-bold text-slate-400 flex items-center gap-1">
                          <FileText size={14} /> {client.activeSops} SOPs
                        </div>
                        <button className="text-blue-600 text-xs font-bold flex items-center hover:underline">
                          View Details <ChevronRight size={14} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {customers.length === 0 && (
                <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-slate-300">
                  <Users size={48} className="mx-auto text-slate-200 mb-4" />
                  <p className="text-slate-400 font-medium">No clients found. Start by adding your first organization.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'repository' && (
            <div className="bg-white rounded-2xl border p-12 text-center text-slate-400">
              <Database size={48} className="mx-auto mb-4 opacity-20" />
              <p className="font-medium">Global SOP Archive is ready.</p>
              <p className="text-xs">Connect to a live client to audit historical detection logs.</p>
            </div>
          )}
        </div>
      </main>

      {/* Add Client Modal */}
      {showAddClient && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-6 animate-in fade-in duration-300">
          <div className="bg-white w-full max-w-md rounded-3xl shadow-2xl overflow-hidden border border-slate-200">
            <div className="p-6 border-b flex justify-between items-center bg-slate-50/50">
              <h3 className="font-bold text-xl">Create New Organization</h3>
              <X onClick={() => setShowAddClient(false)} className="text-slate-400 cursor-pointer" />
            </div>
            <form onSubmit={handleAddClient} className="p-8 space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Client Name</label>
                <input 
                  required
                  type="text" 
                  placeholder="e.g. Acme Corp" 
                  className="w-full px-4 py-3 bg-slate-50 border rounded-xl focus:ring-2 focus:ring-blue-500/20 outline-none transition"
                  value={newClient.name}
                  onChange={(e) => setNewClient({...newClient, name: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Primary SIEM</label>
                <select 
                  className="w-full px-4 py-3 bg-slate-50 border rounded-xl focus:ring-2 focus:ring-blue-500/20 outline-none transition"
                  value={newClient.siem}
                  onChange={(e) => setNewClient({...newClient, siem: e.target.value})}
                >
                  <option>Sentinel</option>
                  <option>Splunk</option>
                  <option>QRadar</option>
                  <option>CrowdStrike</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Log Sources (Comma Separated)</label>
                <textarea 
                  placeholder="e.g. Azure AD, Palo Alto, O365" 
                  className="w-full px-4 py-3 bg-slate-50 border rounded-xl h-24 focus:ring-2 focus:ring-blue-500/20 outline-none transition resize-none"
                  value={newClient.logSources}
                  onChange={(e) => setNewClient({...newClient, logSources: e.target.value})}
                />
                <p className="text-[10px] text-slate-400 italic">These will be used to context-inject the AI architect.</p>
              </div>
              <button type="submit" className="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-blue-700 transition shadow-xl shadow-blue-900/20">
                <Save size={18} /> Initialize Client Environment
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
