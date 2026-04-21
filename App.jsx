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
  Settings
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

// Check if the config has been updated
const isConfigValid = firebaseConfig.apiKey !== "YOUR_API_KEY" && firebaseConfig.apiKey !== "";

// Main Application Component
export default function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [customers, setCustomers] = useState([]);
  const [sops, setSops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Initialize Firebase inside the component
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
          // Rule 3: Auth before queries
          if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
            try {
              await signInWithCustomToken(auth, __initial_auth_token);
            } catch (tokenErr) {
              console.warn("Custom token failed, falling back to anonymous sign-in.");
              await signInAnonymously(auth);
            }
          } else {
            await signInAnonymously(auth);
          }
        } catch (error) {
          console.error("Global Auth error:", error);
          
          // Specifically handle 'admin-restricted-operation' which means Anonymous Auth is disabled
          if (error.code === 'auth/admin-restricted-operation') {
            setAuthError("Anonymous Authentication is disabled. Please enable it in the Firebase Console (Build > Authentication > Sign-in method).");
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
          // Data Fetching
          const customersRef = collection(db, 'artifacts', appId, 'public', 'data', 'customers');
          const sopsRef = collection(db, 'artifacts', appId, 'public', 'data', 'sops');

          unsubCustomers = onSnapshot(customersRef, (snapshot) => {
            setCustomers(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
          }, (err) => console.error("Firestore customer error:", err));

          unsubSops = onSnapshot(sopsRef, (snapshot) => {
            setSops(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
          }, (err) => console.error("Firestore SOP error:", err));
        }
      });

    } catch (err) {
      console.error("Firebase Initialization Error:", err);
      setAuthError("Failed to initialize Firebase. Check your configuration object.");
      setLoading(false);
    }

    return () => {
      if (unsubscribeAuth) unsubscribeAuth();
      if (unsubCustomers) unsubCustomers();
      if (unsubSops) unsubSops();
    };
  }, []);

  if (!isConfigValid || authError) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-slate-900 text-white p-6">
        <div className="max-w-md w-full bg-slate-800 rounded-2xl p-8 border border-slate-700 shadow-2xl">
          <div className="flex justify-center mb-6 text-blue-500">
            <Settings size={48} className="animate-pulse" />
          </div>
          <h2 className="text-2xl font-bold text-center mb-4">Action Required</h2>
          
          <div className="space-y-4">
            <p className="text-slate-400 text-center">
              {authError || "Please ensure your Firebase configuration is valid and all required providers are enabled."}
            </p>

            {authError?.includes("Anonymous") && (
              <div className="bg-slate-900/50 p-4 rounded-lg border border-blue-500/30 text-sm">
                <p className="font-bold text-blue-400 mb-2">How to fix:</p>
                <ol className="list-decimal list-inside space-y-1 text-slate-300">
                  <li>Open <strong>Firebase Console</strong></li>
                  <li>Go to <strong>Authentication</strong></li>
                  <li>Click <strong>Sign-in method</strong> tab</li>
                  <li>Click <strong>Add new provider</strong></li>
                  <li>Select <strong>Anonymous</strong> and click <strong>Enable</strong></li>
                </ol>
              </div>
            )}
            
            <div className="pt-4 space-y-3">
              <a 
                href="https://console.firebase.google.com/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-xl transition"
              >
                Go to Firebase Console <ExternalLink size={16} />
              </a>
              <button 
                onClick={() => window.location.reload()}
                className="w-full py-2 text-slate-400 hover:text-white text-sm font-medium transition"
              >
                Retry Connection
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="text-slate-500 font-medium">Connecting to AIInnovax Cloud...</p>
        </div>
      </div>
    );
  }

  const Sidebar = () => (
    <div className="w-64 h-screen bg-slate-900 text-white flex flex-col border-r border-slate-800">
      <div className="p-6 flex items-center gap-3">
        <div className="bg-blue-600 p-2 rounded-lg">
          <Shield size={24} />
        </div>
        <span className="font-bold text-xl tracking-tight">AIInnovax</span>
      </div>
      
      <nav className="flex-1 px-4 py-4 space-y-2">
        <button 
          onClick={() => setActiveTab('dashboard')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${activeTab === 'dashboard' ? 'bg-blue-600' : 'hover:bg-slate-800'}`}
        >
          <LayoutDashboard size={20} /> Dashboard
        </button>
        <button 
          onClick={() => setActiveTab('users')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${activeTab === 'users' ? 'bg-blue-600' : 'hover:bg-slate-800'}`}
        >
          <Users size={20} /> User Licenses
        </button>
        <button 
          onClick={() => setActiveTab('repository')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${activeTab === 'repository' ? 'bg-blue-600' : 'hover:bg-slate-800'}`}
        >
          <Database size={20} /> SOP Repository
        </button>
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-3 px-4 py-2 text-slate-400">
          <Activity size={16} className="text-green-500" />
          <span className="text-sm">System Healthy</span>
        </div>
      </div>
    </div>
  );

  const StatCard = ({ title, value, icon: Icon, color }) => (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between hover:shadow-md transition cursor-default">
      <div>
        <p className="text-slate-500 text-sm font-medium">{title}</p>
        <h3 className="text-2xl font-bold mt-1">{value}</h3>
      </div>
      <div className={`${color} p-3 rounded-lg text-white`}>
        <Icon size={24} />
      </div>
    </div>
  );

  return (
    <div className="flex bg-slate-50 h-screen overflow-hidden font-sans text-slate-900">
      <Sidebar />
      
      <main className="flex-1 overflow-y-auto">
        <header className="bg-white border-b border-slate-200 px-8 py-4 flex justify-between items-center sticky top-0 z-10 shadow-sm">
          <h2 className="text-xl font-bold text-slate-800 capitalize">
            {activeTab.replace('-', ' ')}
          </h2>
          <div className="flex items-center gap-4">
            <div className="relative p-2 hover:bg-slate-50 rounded-full transition cursor-pointer">
              <Bell className="text-slate-400" size={20} />
              <span className="absolute top-2 right-2 bg-red-500 w-2 h-2 rounded-full border-2 border-white"></span>
            </div>
            <div className="h-8 w-px bg-slate-200 mx-2"></div>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-sm border border-blue-200">
                AD
              </div>
              <div>
                <p className="text-xs font-bold text-slate-800 leading-none">Admin Portal</p>
                <p className="text-[10px] text-slate-400 mt-1">Super User</p>
              </div>
            </div>
          </div>
        </header>

        <div className="p-8 max-w-7xl mx-auto">
          {activeTab === 'dashboard' && (
            <div className="space-y-8 animate-in fade-in duration-500">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard 
                  title="Total Customers" 
                  value={customers.length || "12"} 
                  icon={Users} 
                  color="bg-indigo-600" 
                />
                <StatCard 
                  title="Total SOPs Created" 
                  value={sops.length || "1,248"} 
                  icon={FileText} 
                  color="bg-blue-600" 
                />
                <StatCard 
                  title="Gemini API Utilization" 
                  value="84%" 
                  icon={Activity} 
                  color="bg-emerald-600" 
                />
                <StatCard 
                  title="Token Matrix" 
                  value="12.4M" 
                  icon={Database} 
                  color="bg-amber-500" 
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                  <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <h3 className="font-bold flex items-center gap-2">
                      <Bell size={18} className="text-blue-600" />
                      Subscription Alerts
                    </h3>
                  </div>
                  <div className="divide-y divide-slate-50">
                    {[
                      { user: "Acme Corp", days: 2, tier: "Pro" },
                      { user: "Global Finance", days: 5, tier: "MSSP" },
                      { user: "TechSolutions", days: 12, tier: "Standard" }
                    ].map((alert, i) => (
                      <div key={i} className="p-5 flex items-center justify-between hover:bg-slate-50 transition">
                        <div className="flex items-center gap-4">
                          <div className="bg-amber-50 p-2 rounded-lg">
                            <AlertCircle size={20} className="text-amber-500" />
                          </div>
                          <div>
                            <p className="text-sm font-bold text-slate-800">{alert.user}</p>
                            <p className="text-xs text-slate-500">Subscription expiring in {alert.days} days</p>
                          </div>
                        </div>
                        <span className="px-3 py-1 bg-slate-100 text-slate-600 text-[10px] uppercase font-black rounded-full tracking-wider">
                          {alert.tier}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                  <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <h3 className="font-bold flex items-center gap-2">
                      <Search size={18} className="text-blue-600" />
                      Support Queue
                    </h3>
                  </div>
                  <div className="p-5 space-y-4">
                    {[
                      { name: "John Doe", customer: "Acme Corp", msg: "Issue with KQL export formatting" },
                      { name: "Sarah Smith", customer: "Global Bank", msg: "License upgrade inquiry" }
                    ].map((ticket, i) => (
                      <div key={i} className="bg-slate-50 p-4 rounded-xl border border-slate-100 relative group cursor-pointer hover:border-blue-200 transition">
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">{ticket.customer}</span>
                          <span className="text-[10px] text-slate-400 italic">2h ago</span>
                        </div>
                        <p className="text-xs text-slate-700 font-medium leading-relaxed">{ticket.msg}</p>
                        <div className="text-[10px] text-slate-400 mt-3 flex items-center gap-1 font-semibold tracking-wide">
                          <div className="w-1.5 h-1.5 bg-slate-300 rounded-full"></div>
                          {ticket.name}
                        </div>
                      </div>
                    ))}
                    <button className="w-full py-2 text-blue-600 text-xs font-bold hover:bg-blue-50 rounded-lg transition border border-transparent hover:border-blue-100">
                      View All Tickets
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'users' && (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden animate-in zoom-in-95 duration-300">
              <div className="p-8 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="font-bold text-xl text-slate-800 tracking-tight">Active User Licenses</h3>
                  <p className="text-sm text-slate-400 mt-1">Manage and audit subscription access across the ecosystem</p>
                </div>
                <div className="flex gap-3">
                  <div className="relative flex-1 md:flex-none">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                    <input 
                      type="text" 
                      placeholder="Filter by name or email..." 
                      className="pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 w-full md:w-72 transition"
                    />
                  </div>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead className="bg-slate-50/50 text-slate-500 text-[10px] uppercase tracking-[0.15em] font-black border-b border-slate-100">
                    <tr>
                      <th className="px-8 py-5">User Profile</th>
                      <th className="px-8 py-5">Organization</th>
                      <th className="px-8 py-5 text-center">Tier</th>
                      <th className="px-8 py-5 text-center">Active SOPs</th>
                      <th className="px-8 py-5 text-right">Operational Logic</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {[
                      { name: "Alex Rivera", email: "alex@acme.com", company: "Acme Corp", tier: "Pro", sops: 18 },
                      { name: "Maria Chen", email: "maria@global.io", company: "Global Bank", tier: "MSSP", sops: 42 },
                      { name: "James Wilson", email: "j.wilson@techsol.com", company: "TechSolutions", tier: "Standard", sops: 8 }
                    ].map((user, i) => (
                      <tr key={i} className="hover:bg-slate-50/80 transition-colors group">
                        <td className="px-8 py-5">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 group-hover:bg-blue-100 group-hover:text-blue-600 transition">
                              <Users size={14} />
                            </div>
                            <div>
                              <div className="font-bold text-slate-800 text-sm">{user.name}</div>
                              <div className="text-xs text-slate-400 font-normal">{user.email}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-8 py-5 text-sm font-semibold text-slate-600 italic">"{user.company}"</td>
                        <td className="px-8 py-5 text-center">
                          <span className={`px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase ${user.tier === 'MSSP' ? 'bg-indigo-100 text-indigo-700' : 'bg-blue-100 text-blue-700'}`}>
                            {user.tier}
                          </span>
                        </td>
                        <td className="px-8 py-5 text-center font-black text-slate-700">{user.sops}</td>
                        <td className="px-8 py-5 text-right">
                          <button className="text-blue-600 hover:text-blue-800 font-bold text-xs flex items-center justify-end gap-1 ml-auto">
                            Manage Credentials <ChevronRight size={14} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'repository' && (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden animate-in slide-in-from-bottom-4 duration-500">
              <div className="p-8 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="font-bold text-xl text-slate-800 tracking-tight">Global SOP Repository</h3>
                  <p className="text-sm text-slate-400 mt-1">Unified database filtered by customer registration</p>
                </div>
                <div className="flex items-center gap-3">
                   <select className="bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20">
                    <option>All Registered Customers</option>
                    <option>Acme Corp</option>
                    <option>Global Bank</option>
                    <option>TechSolutions</option>
                  </select>
                  <button className="p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition">
                    <Search size={20} />
                  </button>
                </div>
              </div>
              <div className="py-24 px-8 text-center flex flex-col items-center">
                <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-6 border border-slate-100">
                  <Database size={32} className="text-slate-300" />
                </div>
                <h4 className="text-lg font-bold text-slate-800">No Historical Records Selected</h4>
                <p className="text-slate-400 max-w-sm mt-2 text-sm">
                  Select a registered customer from the dropdown above to view, filter, and audit their complete history of generated SOPs.
                </p>
                <div className="mt-8 flex gap-4">
                  <button className="px-6 py-2.5 bg-slate-100 text-slate-600 rounded-xl font-bold text-sm hover:bg-slate-200 transition">
                    Refresh Sync
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
