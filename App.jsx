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
  doc, 
  setDoc, 
  getDocs, 
  onSnapshot, 
  query, 
  timestamp 
} from "firebase/firestore";
import { 
  Shield, 
  Users, 
  FileText, 
  Activity, 
  Database, 
  LayoutDashboard, 
  ChevronRight, 
  AlertCircle,
  CheckCircle2,
  Bell,
  Search,
  Menu,
  Download,
  Settings
} from 'lucide-react';

/**
 * AIInnovax Firebase Configuration
 * REPLACE THE VALUES BELOW with the config you copied from the Firebase Console
 */
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Initialize Firebase services outside the component
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';

// Main Application Component
export default function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [customers, setCustomers] = useState([]);
  const [sops, setSops] = useState([]);
  const [loading, setLoading] = useState(true);

  // Auth Effect (Rule 3: Auth before queries)
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (error) {
        console.error("Auth error:", error);
      }
    };
    initAuth();

    const unsubscribe = onAuthStateChanged(auth, (u) => {
      setUser(u);
      if (u) setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Data Fetching Effect (Rule 1 & 2: Restricted Paths & No Complex Queries)
  useEffect(() => {
    if (!user) return;

    // Public collection path as per Rule 1
    const customersRef = collection(db, 'artifacts', appId, 'public', 'data', 'customers');
    const sopsRef = collection(db, 'artifacts', appId, 'public', 'data', 'sops');

    const unsubCustomers = onSnapshot(customersRef, (snapshot) => {
      const data = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setCustomers(data);
    }, (err) => console.error("Firestore customer error:", err));

    const unsubSops = onSnapshot(sopsRef, (snapshot) => {
      const data = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setSops(data);
    }, (err) => console.error("Firestore SOP error:", err));

    return () => {
      unsubCustomers();
      unsubSops();
    };
  }, [user]);

  // Sidebar Component
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
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
      <div>
        <p className="text-slate-500 text-sm font-medium">{title}</p>
        <h3 className="text-2xl font-bold mt-1">{value}</h3>
      </div>
      <div className={`${color} p-3 rounded-lg text-white`}>
        <Icon size={24} />
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="text-slate-500 font-medium">Initializing Mission Control...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex bg-slate-50 h-screen overflow-hidden font-sans text-slate-900">
      <Sidebar />
      
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-8 py-4 flex justify-between items-center sticky top-0 z-10">
          <h2 className="text-xl font-bold text-slate-800 capitalize">
            {activeTab.replace('-', ' ')}
          </h2>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Bell className="text-slate-400 cursor-pointer hover:text-slate-600" size={20} />
              <span className="absolute -top-1 -right-1 bg-red-500 w-2 h-2 rounded-full border-2 border-white"></span>
            </div>
            <div className="h-8 w-px bg-slate-200 mx-2"></div>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs border border-blue-200">
                AD
              </div>
              <span className="text-sm font-semibold">Admin</span>
            </div>
          </div>
        </header>

        <div className="p-8 max-w-7xl mx-auto">
          {activeTab === 'dashboard' && (
            <div className="space-y-8">
              {/* Metrics Grid */}
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
                {/* Notification Box */}
                <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                  <div className="p-4 border-b border-slate-100 flex justify-between items-center">
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
                      <div key={i} className="p-4 flex items-center justify-between hover:bg-slate-50 transition">
                        <div className="flex items-center gap-3">
                          <AlertCircle size={18} className="text-amber-500" />
                          <div>
                            <p className="text-sm font-semibold">{alert.user}</p>
                            <p className="text-xs text-slate-500">Subscription expiring in {alert.days} days</p>
                          </div>
                        </div>
                        <span className="px-2 py-1 bg-slate-100 text-slate-600 text-[10px] uppercase font-bold rounded">
                          {alert.tier}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Support Box */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                  <div className="p-4 border-b border-slate-100 flex justify-between items-center">
                    <h3 className="font-bold flex items-center gap-2">
                      <Search size={18} className="text-blue-600" />
                      Support Queue
                    </h3>
                  </div>
                  <div className="p-4 space-y-4">
                    {[
                      { name: "John Doe", customer: "Acme Corp", msg: "Issue with KQL export" },
                      { name: "Sarah Smith", customer: "Global Bank", msg: "License upgrade inquiry" }
                    ].map((ticket, i) => (
                      <div key={i} className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-xs font-bold text-blue-600">{ticket.customer}</span>
                          <span className="text-[10px] text-slate-400 italic">2h ago</span>
                        </div>
                        <p className="text-xs text-slate-700 font-medium">{ticket.msg}</p>
                        <p className="text-[10px] text-slate-400 mt-2">— {ticket.name}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'users' && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                <h3 className="font-bold text-lg">Registered User Licenses</h3>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                    <input 
                      type="text" 
                      placeholder="Search users..." 
                      className="pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 w-64"
                    />
                  </div>
                </div>
              </div>
              <table className="w-full text-left">
                <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider font-bold">
                  <tr>
                    <th className="px-6 py-4">User Details</th>
                    <th className="px-6 py-4">Company</th>
                    <th className="px-6 py-4">Subscription</th>
                    <th className="px-6 py-4">Active SOPs</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {[
                    { name: "Alex Rivera", email: "alex@acme.com", company: "Acme Corp", tier: "Pro", sops: 18 },
                    { name: "Maria Chen", email: "maria@global.io", company: "Global Bank", tier: "MSSP", sops: 42 }
                  ].map((user, i) => (
                    <tr key={i} className="hover:bg-slate-50 transition text-sm">
                      <td className="px-6 py-4">
                        <div className="font-semibold">{user.name}</div>
                        <div className="text-xs text-slate-400 font-normal">{user.email}</div>
                      </td>
                      <td className="px-6 py-4 font-medium">{user.company}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${user.tier === 'MSSP' ? 'bg-indigo-100 text-indigo-700' : 'bg-blue-100 text-blue-700'}`}>
                          {user.tier}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-bold">{user.sops}</td>
                      <td className="px-6 py-4 text-right">
                        <button className="text-blue-600 hover:underline font-semibold">Update License</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'repository' && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-lg">Global SOP Repository</h3>
                  <p className="text-sm text-slate-400">Unified database filtered by customer registration</p>
                </div>
                <select className="border border-slate-200 rounded-lg px-4 py-2 text-sm focus:outline-none">
                  <option>Filter by Customer...</option>
                  <option>Acme Corp</option>
                  <option>Global Bank</option>
                </select>
              </div>
              <div className="p-8 text-center text-slate-400">
                <FileText size={48} className="mx-auto mb-4 opacity-20" />
                <p>Select a customer to view and download historical SOP records.</p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
