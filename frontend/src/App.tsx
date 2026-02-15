import { useEffect, useState, useRef } from "react";
import { create } from "zustand";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { createFromOffer, createRequest, listRequests, listCommodityGroups, predictCommodityGroup, deleteAllRequests, updateRequestStatus, chatWithAsklio } from "./api";

// Icons as simple SVG components
const OverviewIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
  </svg>
);

const PlusIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

const ChartIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

const SettingsIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const SearchIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

const FilterIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
  </svg>
);

const UploadIcon = () => (
  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
  </svg>
);

const EyeIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
  </svg>
);

const XIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const SpinnerIcon = () => (
  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
);

// Types
interface ProcurementRequest {
  id: number;
  requestor_name: string;
  title: string;
  department: string;
  vendor_name: string;
  vendor_vat_id: string | null;
  commodity_group_id: string | null;
  commodity_group: { id: string; category: string; name: string } | null;
  total_cost: number;
  current_status: string;
  created_at: string;
  order_lines: Array<{ product?: string; description: string; unit_price: number; amount: number; unit?: string; total_price: number }>;
}

interface QueueItem {
  id: string;
  filename: string;
  status: "processing" | "completed" | "failed";
}

interface CommodityGroup {
  id: string;
  category: string;
  name: string;
}

// Zustand store
interface AppStore {
  requests: ProcurementRequest[];
  queue: QueueItem[];
  successMessage: string | null;
  setRequests: (requests: ProcurementRequest[]) => void;
  addToQueue: (item: QueueItem) => void;
  updateQueue: (id: string, status: QueueItem["status"]) => void;
  setSuccessMessage: (message: string | null) => void;
}

const useStore = create<AppStore>((set) => ({
  requests: [],
  queue: [],
  successMessage: null,
  setRequests: (requests) => set({ requests }),
  addToQueue: (item) => set((state) => ({ queue: [...state.queue, item] })),
  updateQueue: (id, status) =>
    set((state) => ({
      queue: state.queue.map((item) => (item.id === id ? { ...item, status } : item)),
    })),
  setSuccessMessage: (message) => set({ successMessage: message }),
}));

export default function App() {
  const [activeTab, setActiveTab] = useState<"overview" | "new" | "analytics" | "settings">("new");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRequest, setSelectedRequest] = useState<ProcurementRequest | null>(null);
  const [commodityGroups, setCommodityGroups] = useState<CommodityGroup[]>([]);
  
  // Form states for New Request tab
  const [manualForm, setManualForm] = useState({
    title: "",
    requestor_name: "Moritz Neupert",
    vendor_name: "",
    department: "Marketing",
    total_cost: "",
    vendor_vat_id: "",
    commodity_group_id: "",
  });
  
  // Settings state
  const [settings, setSettings] = useState({
    apiKey: "",
    extractionPrompt: "",
  });
  
  const [dragActive, setDragActive] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const redirectTimeoutRef = useRef<number | null>(null);
  
  // Chat state
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([]);
  const [chatInput, setChatInput] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);
  
  // Debounce ref for title prediction
  const titleDebounceRef = useRef<number | null>(null);
  
  const { requests, queue, successMessage, setRequests, addToQueue, updateQueue, setSuccessMessage } = useStore();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [requestsData, groupsData] = await Promise.all([
          listRequests(),
          listCommodityGroups(),
        ]);
        setRequests(requestsData);
        setCommodityGroups(groupsData);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
    };
    fetchData();
  }, [setRequests]);

  // Close modal on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSelectedRequest(null);
      }
    };
    
    if (selectedRequest) {
      window.addEventListener('keydown', handleEscape);
      return () => window.removeEventListener('keydown', handleEscape);
    }
  }, [selectedRequest]);

  // Cleanup redirect timeout on unmount
  useEffect(() => {
    return () => {
      if (redirectTimeoutRef.current) {
        clearTimeout(redirectTimeoutRef.current);
      }
    };
  }, []);

  const handleFileUpload = async (file: File) => {
    const queueId = `${Date.now()}-${file.name}`;
    addToQueue({ id: queueId, filename: file.name, status: "processing" });
    
    try {
      await createFromOffer(file);
      updateQueue(queueId, "completed");
      setSuccessMessage("You will be forwarded to the updated overview of your procurement intake");
      
      // Refresh requests
      const updatedRequests = await listRequests();
      setRequests(updatedRequests);
      
      // Auto-redirect to overview after 3 seconds
      // Clear any existing timeout first
      if (redirectTimeoutRef.current) {
        clearTimeout(redirectTimeoutRef.current);
      }
      redirectTimeoutRef.current = window.setTimeout(() => {
        setActiveTab("overview");
        setSuccessMessage(null);
        redirectTimeoutRef.current = null;
      }, 3000);
    } catch (error) {
      updateQueue(queueId, "failed");
      console.error("Upload failed:", error);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Form validation
    if (!manualForm.title.trim() || 
        !manualForm.requestor_name.trim() || 
        !manualForm.vendor_name.trim() || 
        !manualForm.department.trim() || 
        !manualForm.total_cost || 
        parseFloat(manualForm.total_cost) <= 0) {
      alert("Request cannot be created, due to missing information");
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Create a single order line from form data
      const orderLine = {
        description: manualForm.title,
        unit_price: parseFloat(manualForm.total_cost),
        amount: 1,
      };
      
      await createRequest({
        ...manualForm,
        order_lines: [orderLine],
      });
      
      setSuccessMessage("Request created successfully!");
      
      // Reset form with prefilled values
      setManualForm({
        title: "",
        requestor_name: "Moritz Neupert",
        vendor_name: "",
        department: "Marketing",
        total_cost: "",
        vendor_vat_id: "",
        commodity_group_id: "",
      });
      
      // Refresh requests
      const updatedRequests = await listRequests();
      setRequests(updatedRequests);
    } catch (error) {
      console.error("Failed to create request:", error);
      alert("Failed to create request. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle title change with debounced commodity prediction
  const handleTitleChange = (newTitle: string) => {
    setManualForm({ ...manualForm, title: newTitle });
    
    // Clear existing timeout
    if (titleDebounceRef.current) {
      clearTimeout(titleDebounceRef.current);
    }
    
    // Set new timeout for prediction
    if (newTitle.trim().length > 0) {
      titleDebounceRef.current = window.setTimeout(async () => {
        try {
          const result = await predictCommodityGroup(newTitle);
          setManualForm(prev => ({ ...prev, commodity_group_id: result.commodity_group_id }));
        } catch (error) {
          console.error("Failed to predict commodity group:", error);
        }
      }, 500);
    }
  };

  // Handle Clear History
  const handleClearHistory = async () => {
    if (!confirm("Are you sure you want to delete all procurement requests? This action cannot be undone.")) {
      return;
    }
    
    try {
      await deleteAllRequests();
      setSuccessMessage("All requests deleted successfully!");
      const updatedRequests = await listRequests();
      setRequests(updatedRequests);
    } catch (error) {
      console.error("Failed to delete requests:", error);
      alert("Failed to delete requests. Please try again.");
    }
  };

  // Handle chat submission
  const handleChatSubmit = async () => {
    if (!chatInput.trim()) return;
    
    const userMessage = chatInput.trim();
    setChatInput("");
    setChatMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setIsChatLoading(true);
    
    try {
      const response = await chatWithAsklio(userMessage);
      setChatMessages(prev => [...prev, { role: "assistant", content: response.reply }]);
    } catch (error) {
      console.error("Chat failed:", error);
      setChatMessages(prev => [...prev, { role: "assistant", content: "Sorry, I'm having trouble connecting right now. Please try again." }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  // Filter requests based on search query
  const filteredRequests = requests.filter((r) =>
    r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.vendor_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.department.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Dashboard metrics
  const totalSpend = requests.reduce((sum, r) => sum + Number(r.total_cost), 0);
  const totalRequests = requests.length;
  const openRequests = requests.filter((r) => r.current_status === "Open").length;
  const uniqueVendors = new Set(requests.map((r) => r.vendor_name)).size;

  // Analytics data
  const spendByVendor = Object.entries(
    requests.reduce((acc, r) => {
      acc[r.vendor_name] = (acc[r.vendor_name] || 0) + Number(r.total_cost);
      return acc;
    }, {} as Record<string, number>)
  )
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);

  const spendByDepartment = Object.entries(
    requests.reduce((acc, r) => {
      acc[r.department] = (acc[r.department] || 0) + Number(r.total_cost);
      return acc;
    }, {} as Record<string, number>)
  ).map(([name, value]) => ({ name, value }));

  const statusDistribution = Object.entries(
    requests.reduce((acc, r) => {
      acc[r.current_status] = (acc[r.current_status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>)
  ).map(([name, value]) => ({ name, value }));

  const COLORS = ["#7C3AED", "#A78BFA", "#C4B5FD", "#DDD6FE", "#EDE9FE"];

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "open":
        return "bg-green-100 text-green-800";
      case "in progress":
        return "bg-blue-100 text-blue-800";
      case "closed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="min-h-screen bg-[#F8F7FF]">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* AskLio Logo - Crescent Moon + Text */}
              <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" fill="black" stroke="black"/>
              </svg>
              <div>
                <h1 className="text-3xl font-bold text-black">askLio</h1>
                <p className="text-sm text-gray-600 mt-1">Efficient Request Management</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Success Banner */}
      {successMessage && (
        <div className="bg-green-50 border-l-4 border-green-400 p-4">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-green-700">{successMessage}</p>
              </div>
            </div>
            <button
              onClick={() => setSuccessMessage(null)}
              className="text-green-500 hover:text-green-700"
            >
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: "new", label: "New Request", icon: <PlusIcon /> },
              { id: "overview", label: "Overview", icon: <OverviewIcon /> },
              { id: "analytics", label: "Analytics", icon: <ChartIcon /> },
              { id: "settings", label: "Settings", icon: <SettingsIcon /> },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as "overview" | "new" | "analytics" | "settings")}
                className={`
                  flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${
                    activeTab === tab.id
                      ? "border-black text-black"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }
                `}
              >
                {tab.icon}
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* Dashboard Cards */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <span className="text-2xl">€</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Spend</dt>
                        <dd className="text-lg font-semibold text-gray-900">€{totalSpend.toFixed(2)}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <span className="text-2xl">📋</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Requests</dt>
                        <dd className="text-lg font-semibold text-gray-900">{totalRequests}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                        <span className="text-2xl">✓</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Open Requests</dt>
                        <dd className="text-lg font-semibold text-gray-900">{openRequests}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                        <span className="text-2xl">🏢</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Vendors</dt>
                        <dd className="text-lg font-semibold text-gray-900">{uniqueVendors}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Processing Queue */}
            {queue.filter((q) => q.status === "processing").length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-blue-900 mb-3">Processing Queue</h3>
                <div className="space-y-2">
                  {queue
                    .filter((q) => q.status === "processing")
                    .map((item) => (
                      <div key={item.id} className="flex items-center gap-2 text-sm text-blue-700">
                        <SpinnerIcon />
                        <span>Processing {item.filename}...</span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Recent Requests */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Requests</h3>
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <input
                        type="text"
                        placeholder="Search..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                      />
                      <div className="absolute left-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
                        <SearchIcon />
                      </div>
                    </div>
                    <button className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                      <FilterIcon />
                    </button>
                    <button 
                      onClick={handleClearHistory}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
                    >
                      Clear History
                    </button>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Request Details
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Vendor
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Cost
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {filteredRequests.map((request) => (
                        <>
                          <tr key={request.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4">
                              <div className="text-sm font-medium text-gray-900">{request.title}</div>
                              <div className="text-sm text-gray-500">ID: {request.id}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {request.vendor_name}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              €{Number(request.total_cost).toFixed(2)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <select
                                value={request.current_status}
                                onChange={async (e) => {
                                  try {
                                    await updateRequestStatus(request.id, e.target.value, "User");
                                    const updatedRequests = await listRequests();
                                    setRequests(updatedRequests);
                                    setSuccessMessage("Status updated successfully!");
                                  } catch (error) {
                                    console.error("Failed to update status:", error);
                                    alert("Failed to update status");
                                  }
                                }}
                                className={`px-2 py-1 text-xs leading-5 font-semibold rounded-full border-0 ${getStatusColor(
                                  request.current_status
                                )}`}
                              >
                                <option value="Open">Open</option>
                                <option value="In Progress">In Progress</option>
                                <option value="Closed">Closed</option>
                              </select>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              <button
                                onClick={() => setSelectedRequest(request)}
                                className="inline-flex items-center px-3 py-1.5 border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 transition-colors text-sm font-medium"
                              >
                                <EyeIcon />
                                <span className="ml-1.5">View</span>
                              </button>
                            </td>
                          </tr>
                        </>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* New Request Tab */}
        {activeTab === "new" && (
          <div className="space-y-6">
            {/* File Upload Zone */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Offer Document</h3>
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                  dragActive
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-300 hover:border-blue-400"
                }`}
              >
                <div className="flex flex-col items-center">
                  <div className="text-blue-500 mb-4">
                    <UploadIcon />
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    Drag and drop your offer document here
                  </p>
                  <p className="text-xs text-gray-500 mb-4">or</p>
                  <label className="cursor-pointer">
                    <span className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                      Browse Files
                    </span>
                    <input
                      type="file"
                      className="hidden"
                      accept=".txt,.pdf"
                      onChange={(e) => {
                        if (e.target.files?.[0]) {
                          handleFileUpload(e.target.files[0]);
                        }
                      }}
                    />
                  </label>
                  <p className="text-xs text-gray-500 mt-2">PDF or TXT files only</p>
                </div>
              </div>
            </div>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-[#F8F7FF] text-gray-500">OR ENTER MANUALLY</span>
              </div>
            </div>

            {/* Manual Form */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create Request Manually</h3>
              <form onSubmit={handleManualSubmit} className="space-y-4">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Title *
                    </label>
                    <input
                      type="text"
                      required
                      value={manualForm.title}
                      onChange={(e) => handleTitleChange(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Requestor *
                    </label>
                    <input
                      type="text"
                      required
                      value={manualForm.requestor_name}
                      onChange={(e) =>
                        setManualForm({ ...manualForm, requestor_name: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Vendor Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={manualForm.vendor_name}
                      onChange={(e) =>
                        setManualForm({ ...manualForm, vendor_name: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Department *
                    </label>
                    <input
                      type="text"
                      required
                      value={manualForm.department}
                      onChange={(e) =>
                        setManualForm({ ...manualForm, department: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Total Cost (€) *
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={manualForm.total_cost}
                      onChange={(e) =>
                        setManualForm({ ...manualForm, total_cost: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">VAT ID</label>
                    <input
                      type="text"
                      value={manualForm.vendor_vat_id}
                      onChange={(e) =>
                        setManualForm({ ...manualForm, vendor_vat_id: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Commodity Group
                    </label>
                    <select
                      value={manualForm.commodity_group_id}
                      onChange={(e) =>
                        setManualForm({ ...manualForm, commodity_group_id: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Select a commodity group</option>
                      {commodityGroups.map((group) => (
                        <option key={group.id} value={group.id}>
                          {group.name} ({group.category})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                  >
                    {isSubmitting ? "Submitting..." : "Submit Request"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === "analytics" && (
          <div className="space-y-6">
            {/* Dashboard Cards */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <span className="text-2xl">€</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Spend</dt>
                        <dd className="text-lg font-semibold text-gray-900">€{totalSpend.toFixed(2)}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <span className="text-2xl">📋</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Requests</dt>
                        <dd className="text-lg font-semibold text-gray-900">{totalRequests}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                        <span className="text-2xl">✓</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Open Requests</dt>
                        <dd className="text-lg font-semibold text-gray-900">{openRequests}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                        <span className="text-2xl">🏢</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Vendors</dt>
                        <dd className="text-lg font-semibold text-gray-900">{uniqueVendors}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Spend by Vendor</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={spendByVendor}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#7C3AED" name="Spend (€)" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Spend by Department</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={spendByDepartment}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => entry.name}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {spendByDepartment.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Request Status Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={statusDistribution}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" fill="#A78BFA" name="Count" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === "settings" && (
          <div className="space-y-6">
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Settings</h3>
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    value={settings.apiKey}
                    onChange={(e) => setSettings({ ...settings, apiKey: e.target.value })}
                    placeholder="sk-..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Data Extraction Prompt
                  </label>
                  <textarea
                    rows={6}
                    value={settings.extractionPrompt}
                    onChange={(e) =>
                      setSettings({ ...settings, extractionPrompt: e.target.value })
                    }
                    placeholder="Enter your custom data extraction prompt..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={() => {
                      setSuccessMessage("Settings saved successfully!");
                    }}
                    className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 font-medium"
                  >
                    Save Settings
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>

      {/* Request Profile Modal */}
      {selectedRequest && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedRequest(null)}
        >
          <div 
            className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <h2 className="text-xl font-bold text-gray-900">{selectedRequest.title}</h2>
                  <span
                    className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(
                      selectedRequest.current_status
                    )}`}
                  >
                    {selectedRequest.current_status}
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-1">Request ID: {selectedRequest.id}</p>
              </div>
              <button
                onClick={() => setSelectedRequest(null)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <XIcon />
              </button>
            </div>

            {/* Modal Body */}
            <div className="px-6 py-6 space-y-6">
              {/* Metadata Section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Request Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Requestor Name</span>
                    <p className="mt-1 text-sm font-medium text-gray-900">{selectedRequest.requestor_name}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor Name</span>
                    <p className="mt-1 text-sm font-medium text-gray-900">{selectedRequest.vendor_name}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">VAT ID</span>
                    <p className="mt-1 text-sm font-medium text-gray-900">{selectedRequest.vendor_vat_id || "-"}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Department</span>
                    <p className="mt-1 text-sm font-medium text-gray-900">{selectedRequest.department}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Commodity Group</span>
                    <p className="mt-1 text-sm font-medium text-gray-900">
                      {selectedRequest.commodity_group ? 
                        `${selectedRequest.commodity_group.name} (${selectedRequest.commodity_group.category})` : 
                        "-"}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Total Cost</span>
                    <p className="mt-1 text-sm font-medium text-gray-900">€{Number(selectedRequest.total_cost).toFixed(2)}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4 md:col-span-2">
                    <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Created At</span>
                    <p className="mt-1 text-sm font-medium text-gray-900">
                      {new Date(selectedRequest.created_at).toLocaleString('en-US', { 
                        dateStyle: 'medium', 
                        timeStyle: 'short' 
                      })}
                    </p>
                  </div>
                </div>
              </div>

              {/* Order Lines Section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Lines</h3>
                <div className="overflow-x-auto border border-gray-200 rounded-lg">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-blue-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-blue-700 uppercase tracking-wider">Product</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-blue-700 uppercase tracking-wider">Description</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-blue-700 uppercase tracking-wider">Unit Price</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-blue-700 uppercase tracking-wider">Amount</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-blue-700 uppercase tracking-wider">Unit</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-blue-700 uppercase tracking-wider">Total Price</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {selectedRequest.order_lines.map((line, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-900">{line.product || "-"}</td>
                          <td className="px-4 py-3 text-sm text-gray-900">{line.description}</td>
                          <td className="px-4 py-3 text-sm text-gray-900 text-right">€{Number(line.unit_price).toFixed(2)}</td>
                          <td className="px-4 py-3 text-sm text-gray-900 text-right">{line.amount}</td>
                          <td className="px-4 py-3 text-sm text-gray-900">{line.unit || "-"}</td>
                          <td className="px-4 py-3 text-sm font-medium text-gray-900 text-right">
                            €{Number(line.total_price).toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end">
              <button
                onClick={() => setSelectedRequest(null)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AskLio Chat Widget */}
      <div className="fixed bottom-6 right-6 z-50">
        {!isChatOpen ? (
          <button
            onClick={() => setIsChatOpen(true)}
            className="bg-black text-white rounded-full p-4 shadow-lg hover:bg-gray-800 transition-all"
            title="Chat with AskLio"
          >
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" fill="currentColor" stroke="currentColor"/>
            </svg>
          </button>
        ) : (
          <div className="bg-white rounded-lg shadow-2xl w-96 h-[500px] flex flex-col">
            {/* Chat Header */}
            <div className="bg-black text-white p-4 rounded-t-lg flex items-center justify-between">
              <div className="flex items-center gap-2">
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" fill="white" stroke="white"/>
                </svg>
                <span className="font-semibold">AskLio</span>
              </div>
              <button
                onClick={() => setIsChatOpen(false)}
                className="text-white hover:text-gray-300"
              >
                <XIcon />
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {chatMessages.length === 0 && (
                <div className="text-center text-gray-500 py-8">
                  <p className="text-sm">Hi! I'm AskLio, your procurement assistant.</p>
                  <p className="text-sm mt-2">Ask me about your requests or procurement policies!</p>
                </div>
              )}
              {chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      msg.role === "user"
                        ? "bg-black text-white"
                        : "bg-gray-100 text-gray-900"
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}
              {isChatLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-3">
                    <SpinnerIcon />
                  </div>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleChatSubmit()}
                  placeholder="Type your message..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-black focus:border-black text-sm"
                  disabled={isChatLoading}
                />
                <button
                  onClick={handleChatSubmit}
                  disabled={isChatLoading || !chatInput.trim()}
                  className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
