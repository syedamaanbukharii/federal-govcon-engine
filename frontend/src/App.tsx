import { useState, useEffect } from 'react';
import './index.css';

interface Metrics {
  total_companies: number;
  total_leads: number;
  active_opportunities: number;
}

interface Company {
  id: number;
  company_name: string;
  status: string;
  federal_activity_status: string;
  ai_reasoning?: string;
  is_joint_venture?: boolean;
  contact_name: string;
  contact_title: string;
  email: string;
  phone: string;
  naics: string;
  linkedin: string;
}

interface DashboardData {
  metrics: Metrics;
  recent_accounts: Company[];
}

function App() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/dashboard')
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching data:", err);
        setLoading(false);
      });
  }, []);

  const generateSalesNavString = async (companyName: string) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/sales-nav-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ company_name: companyName, service_line: "Software Development" })
      });
      const result = await response.json();
      
      navigator.clipboard.writeText(result.boolean_string);
      window.open(result.url, '_blank');
      
      alert(`Copied Search String to Clipboard!\n\nOpening Sales Navigator Lead Search for ${companyName}...`);
    } catch (e) {
      console.error(e);
      alert('Failed to generate Sales Navigator search.');
    }
  };

  const handleRunDiscovery = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/run-discovery', {
        method: 'POST'
      });
      const result = await response.json();
      alert(result.message);
      // Reload dashboard data
      window.location.reload();
    } catch (err) {
      console.error(err);
      alert("Failed to run discovery agent.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center gap-2">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                <span className="font-bold text-xl tracking-tight text-slate-900">GovCon Intelligence</span>
              </div>
            </div>
            <div className="flex items-center">
              <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">BETA</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-900">Active Federal Opportunities</h1>
          <p className="mt-1 text-sm text-slate-500">Live intelligence feed identifying federal contractors with highest probability of requiring Proposal, Tech, or Staffing support.</p>
        </div>

        {/* Metrics */}
        {loading ? (
          <div className="animate-pulse flex space-x-4 mb-8">
            <div className="flex-1 space-y-4 py-1">
              <div className="h-24 bg-slate-200 rounded"></div>
            </div>
            <div className="flex-1 space-y-4 py-1">
              <div className="h-24 bg-slate-200 rounded"></div>
            </div>
            <div className="flex-1 space-y-4 py-1">
              <div className="h-24 bg-slate-200 rounded"></div>
            </div>
          </div>
        ) : data ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-slate-200 p-6">
              <dt className="text-sm font-medium text-slate-500 truncate">Total Verified Accounts</dt>
              <dd className="mt-2 text-3xl font-semibold text-slate-900">{data.metrics.total_companies}</dd>
            </div>
            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-slate-200 p-6">
              <dt className="text-sm font-medium text-slate-500 truncate">Verified Contacts / Leads</dt>
              <dd className="mt-2 text-3xl font-semibold text-blue-600">{data.metrics.total_leads}</dd>
            </div>
            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-slate-200 p-6">
              <dt className="text-sm font-medium text-slate-500 truncate">Active Federal Pipeline</dt>
              <dd className="mt-2 text-3xl font-semibold text-emerald-600">{data.metrics.active_opportunities}</dd>
            </div>
          </div>
        ) : null}

        {/* Table */}
        <div className="bg-white shadow-sm rounded-lg border border-slate-200 overflow-hidden">
          <div className="px-4 py-5 sm:px-6 flex justify-between items-center bg-slate-50 border-b border-slate-200">
            <h3 className="text-lg leading-6 font-medium text-slate-900">Prioritized Targets</h3>
            <div className="flex gap-2">
              <button 
                onClick={async () => {
                  try {
                    const response = await fetch('http://127.0.0.1:8000/api/run-validation', { method: 'POST' });
                    const result = await response.json();
                    alert(result.message);
                    window.location.reload();
                  } catch (e) {
                    alert('Validation failed');
                  }
                }}
                className="inline-flex items-center px-4 py-2 border border-slate-300 text-sm font-medium rounded-md shadow-sm text-slate-700 bg-white hover:bg-slate-50">
                Run AI Validation
              </button>
              <button 
                onClick={handleRunDiscovery}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
                Run Discovery Agent
              </button>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-white">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Company</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Key Executive</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Contact Details</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Core NAICS</th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 whitespace-nowrap text-center text-sm text-slate-500">
                      Loading intelligence data...
                    </td>
                  </tr>
                ) : data && data.recent_accounts.length > 0 ? (
                  data.recent_accounts.map((company) => (
                    <tr key={company.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-slate-900 flex items-center gap-2">
                          {company.company_name}
                          {company.is_joint_venture && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                              Joint Venture
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-slate-500 max-w-xs truncate" title={company.ai_reasoning}>
                          {company.ai_reasoning || `ID: ${company.id}`}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-emerald-100 text-emerald-800">
                          {company.federal_activity_status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-slate-900 font-medium">{company.contact_name}</div>
                        <div className="text-xs text-slate-500">{company.contact_title}</div>
                        {company.linkedin && company.linkedin !== 'nan' && (
                          <a href={company.linkedin} target="_blank" rel="noreferrer" className="text-xs text-blue-600 hover:underline">LinkedIn</a>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-slate-900">{company.phone || "N/A"}</div>
                        <div className="text-xs text-slate-500">{company.email || "N/A"}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-xs text-slate-700 max-w-xs truncate" title={company.naics}>{company.naics}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button 
                          onClick={() => generateSalesNavString(company.company_name)}
                          className="text-blue-600 hover:text-blue-900 bg-blue-50 px-3 py-1 rounded border border-blue-200"
                        >
                          Sales Nav Search
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 whitespace-nowrap text-center text-sm text-slate-500">
                      No accounts found. Seed the database first.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
