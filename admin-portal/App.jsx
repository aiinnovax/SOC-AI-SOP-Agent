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
 * Note: These are active credentials based on your previous setup.
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
          // Rule 1: Public data path for multi-tenant setup
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
          <p className="text-slate-400 mb-6">{authError || "Firebase configuration is invalid or provider is disabled."}</p>
          <a 
            href="https://console.firebase.google.com/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="bg-blue-600 block py-3 rounded-xl font-bold hover:bg-blue-700 transition"
          >
            Open Firebase Console
          </a>
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
          <button 
            onClick={() => setActiveTab('dashboard')} 
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition ${activeTab === 'dashboard' ? 'bg-blue-600 shadow-lg shadow-blue-900/20' : 'hover:bg-slate-800'}`}
          >
            <LayoutDashboard size={20} /> Dashboard
          </button>
          <button 
            onClick={() => setActiveTab('clients')} 
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition ${activeTab === 'clients' ? 'bg-blue-600 shadow-lg shadow-blue-900/20' : 'hover:bg-slate-800'}`}
          >
            <Users size={20} /> Client Management
          </button>
          <button 
            onClick={() => setActiveTab('repository')} 
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition ${activeTab === 'repository' ? 'bg-blue-600 shadow-lg shadow-blue-900/20' : 'hover:bg-slate-800'}`}
          >
            <Database size={20} /> SOP Repository
          </button>
        </nav>
        <div className="p-6 border-t border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-xs">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            Cloud Connection Active
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <header className="bg-white border-b px-8 py-4 flex justify-between items-center sticky top-0 z-10 shadow-sm">
          <h2 className="text-xl font-bold capitalize">{activeTab.replace('-', ' ')}</h2>
          <div className="flex items-center gap-4">
            <div className="relative p-2 hover:bg-slate-50 rounded-full cursor-pointer transition">
              <Bell className="text-slate-400" size={20} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
            </div>
            <div className="h-8 w-px bg-slate-200 mx-2"></div>
            <div className="flex items-center gap-3 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-100">
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold">AD</div>
              <div>
                <p className="text-xs font-bold leading-none">Administrator</p>
                <p className="text-[10px] text-slate-400 mt-1">Super User</p>
              </div>
            </div>
          </div>
        </header>

        <div className="p-8 max-w-7xl mx-auto">
          {activeTab === 'dashboard' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-in fade-in slide-in-from-top-4 duration-500">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition">
                <p className="text-slate-400 text-sm font-medium">Active Clients</p>
                <h3 className="text-3xl font-bold mt-1">{customers.length}</h3>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition">
                <p className="text-slate-400 text-sm font-medium">Managed SOPs</p>
                <h3 className="text-3xl font-bold mt-1">{sops.length}</h3>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition">
                <p className="text-slate-400 text-sm font-medium">AI Reliability</p>
                <h3 className="text-3xl font-bold mt-1 text-green-500">99.9%</h3>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition">
                <p className="text-slate-400 text-sm font-medium">Token Usage</p>
                <h3 className="text-3xl font-bold mt-1">4.2M</h3>
              </div>
            </div>
          )}

          {activeTab === 'clients' && (
            <div className="space-y-6 animate-in fade-in duration-300">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-2xl font-bold tracking-tight text-slate-800">Organization Directory</h3>
                  <p className="text-slate-400 text-sm mt-1">Add clients and configure their environment-specific log sources</p>
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
                  <div key={client.id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-300 transition-all group">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center gap-3">
                        <div className="bg-slate-100 p-2.5 rounded-xl text-blue-600 group-hover:bg-blue-50 transition">
                          <Shield size={20} />
                        </div>
                        <div>
                          <h4 className="font-bold text-lg text-slate-800">{client.name}</h4>
                          <span className="text-[10px] uppercase font-black bg-blue-50 text-blue-600 px-2 py-0.5 rounded tracking-widest">{client.siem}</span>
                        </div>
                      </div>
                      <Settings className="text-slate-300 cursor-pointer hover:text-slate-600" size={18} />
                    </div>
                    <div className="space-y-3">
                      <div>
                        <p className="text-[10px] uppercase font-bold text-slate-400 mb-2 tracking-wide">Integrated Log Sources</p>
                        <div className="flex flex-wrap gap-1.5">
                          {client.logSources ? client.logSources.split(',').map((log, i) => (
                            <span key={i} className="text-[10px] bg-slate-50 border border-slate-100 px-2 py-1 rounded text-slate-600 font-semibold">
                              {log.trim()}
                            </span>
                          )) : (
                            <span className="text-[10px] text-slate-300 italic font-medium">No sources configured</span>
                          )}
                        </div>
                      </div>
                      <div className="flex justify-between items-center pt-4 border-t border-slate-50 mt-4">
                        <div className="text-xs font-bold text-slate-400 flex items-center gap-1.5">
                          <FileText size={14} className="text-slate-300" /> {client.activeSops || 0} SOPs
                        </div>
                        <button className="text-blue-600 text-xs font-bold flex items-center hover:translate-x-1 transition-transform">
                          Environment Settings <ChevronRight size={14} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {customers.length === 0 && (
                <div className="text-center py-24 bg-white rounded-3xl border border-dashed border-slate-300 flex flex-col items-center">
                  <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                    <Users size={32} className="text-slate-200" />
                  </div>
                  <p className="text-slate-500 font-medium">No organizations registered yet.</p>
                  <p className="text-slate-400 text-xs mt-1">Start by adding your first client using the button above.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'repository' && (
            <div className="bg-white rounded-3xl border p-20 text-center flex flex-col items-center animate-in slide-in-from-bottom-4 duration-500">
              <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-6">
                <Database size={40} className="text-slate-200" />
              </div>
              <h4 className="text-lg font-bold text-slate-800">Global SOP Archive</h4>
              <p className="text-slate-400 max-w-sm mt-2 text-sm leading-relaxed">
                Centralized repository of all generated procedures. Select a client to audit historical detection logic and triage plans.
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Add Client Modal */}
      {showAddClient && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-6 animate-in fade-in zoom-in-95 duration-200">
          <div className="bg-white w-full max-w-md rounded-3xl shadow-2xl overflow-hidden border border-slate-200">
            <div className="p-6 border-b flex justify-between items-center bg-slate-50/50">
              <h3 className="font-bold text-xl text-slate-800 tracking-tight">Register Organization</h3>
              <div 
                onClick={() => setShowAddClient(false)} 
                className="p-1 hover:bg-slate-200 rounded-full cursor-pointer transition text-slate-400"
              >
                <X size={20} />
              </div>
            </div>
            <form onSubmit={handleAddClient} className="p-8 space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase text-slate-500 tracking-widest px-1">Client Name</label>
                <input 
                  required
                  type="text" 
                  placeholder="e.g. Acme Corp" 
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 outline-none transition font-medium"
                  value={newClient.name}
                  onChange={(e) => setNewClient({...newClient, name: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase text-slate-500 tracking-widest px-1">Primary SIEM Stack</label>
                <select 
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 outline-none transition font-medium cursor-pointer"
                  value={newClient.siem}
                  onChange={(e) => setNewClient({...newClient, siem: e.target.value})}
                >
                  <option>Sentinel</option>
                  <option>Splunk</option>
                  <option>QRadar</option>
                  <option>CrowdStrike</option>
                  <option>LogRhythm</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase text-slate-500 tracking-widest px-1">Integrated Log Sources</label>
                <textarea 
                  placeholder="e.g. Azure AD, Palo Alto, O365 Audit Logs" 
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl h-28 focus:ring-2 focus:ring-blue-500/20 outline-none transition resize-none font-medium leading-relaxed"
                  value={newClient.logSources}
                  onChange={(e) => setNewClient({...newClient, logSources: e.target.value})}
                />
                <p className="text-[10px] text-slate-400 italic px-1 leading-relaxed">
                  Separating sources with commas allows the AI to suggest specific investigation steps for this organization.
                </p>
              </div>
              <button 
                type="submit" 
                className="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-blue-700 transition shadow-xl shadow-blue-900/20 mt-2"
              >
                <Save size={18} /> Initialize Environment
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}