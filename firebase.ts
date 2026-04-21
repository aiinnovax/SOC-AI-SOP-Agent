import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

/**
 * AIInnovax Firebase Configuration
 * REPLACE THE VALUES BELOW with the config you copied from the Firebase Console
 */
const firebaseConfig = {
  apiKey: "AIzaSyD4jTLlcwSlq9N3YuvBhPLCmnBtUyhRMfs",
  authDomain: "soc-ai-sop-agent.firebaseapp.com",
  projectId: "soc-ai-sop-agent",
  storageBucket: "soc-ai-sop-agent.firebasestorage.app",
  messagingSenderId: "785445958281",
  appId: "1:785445958281:web:c00b3a13cf79d481fa0c58"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Services
export const auth = getAuth(app);
export const db = getFirestore(app);

export default app;
