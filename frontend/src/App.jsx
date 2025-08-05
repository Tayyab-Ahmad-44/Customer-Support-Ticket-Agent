import React, { useState, useEffect } from 'react';
import {
  Send,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Ticket,
  FileText,
  Clock,
  Tag,
  User
} from 'lucide-react';


const SupportTicketApp = () => {
  const [activeSection, setActiveSection] = useState('query');
  const [formData, setFormData] = useState({ subject: '', description: '' });
  const [response, setResponse] = useState(null);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [escalationLogs, setEscalationLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);


  useEffect(() => {
    if (activeSection === 'escalation') fetchEscalationLogs();
  }, [activeSection]);


  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.subject || !formData.description) return alert('Fill all fields');
    setSubmitLoading(true);
    setResponse(null);


    try {
      const res = await fetch('https://d8927acef3f1.ngrok-free.app/query', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      setResponse(data);
      if (data.status === 'success') setFormData({ subject: '', description: '' });
    } catch (err) {
      console.error('Submit error:', err);
      setResponse({ status: 'error', message: 'Failed to submit ticket.' });
    } finally {
      setSubmitLoading(false);
    }
  };


  const fetchEscalationLogs = async () => {
    setLoading(true);
    setError(null);
    console.log('Fetching escalation logs...');
    
    try {
      const res = await fetch('https://d8927acef3f1.ngrok-free.app/escalation-logs', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        }
      });
      
      console.log('Response status:', res.status);
      console.log('Response ok:', res.ok);
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      console.log('Escalation Logs Response:', data);
      
      setTimeout(() => {
        setEscalationLogs(Array.isArray(data) ? data : []);
        setLoading(false);
      }, 400);
    } catch (err) {
      console.error('Fetch escalation logs error:', err);
      setError(`Failed to load escalation logs: ${err.message}`);
      setEscalationLogs([]);
      setLoading(false);
    }
  };


  const getCategoryColor = (category) => {
    const colors = {
      'urgent': 'bg-red-100 text-red-800 border-red-200',
      'high': 'bg-orange-100 text-orange-800 border-orange-200',
      'medium': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'low': 'bg-green-100 text-green-800 border-green-200',
      'default': 'bg-teal-100 text-teal-800 border-teal-200'
    };
    return colors[category?.toLowerCase()] || colors.default;
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-cyan-50 to-teal-100">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-72 h-72 bg-teal-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse"></div>
        <div className="absolute top-40 right-20 w-64 h-64 bg-cyan-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse delay-2000"></div>
        <div className="absolute bottom-20 left-40 w-80 h-80 bg-emerald-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse delay-4000"></div>
      </div>

      <div className="relative z-10 p-6">
        <div className="max-w-4xl mx-auto">
          <header className="mb-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full mb-4 shadow-lg">
              <Ticket className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent mb-2">
              Support Hub
            </h1>
            <p className="text-gray-600 text-lg">Your gateway to exceptional support</p>
          </header>

          <div className="flex justify-center mb-8">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-2 shadow-lg border border-white/20">
              <button
                onClick={() => setActiveSection('query')}
                className={`flex items-center px-6 py-3 rounded-xl font-medium transition-all duration-300 ${
                  activeSection === 'query'
                    ? 'bg-gradient-to-r from-teal-500 to-cyan-500 text-white shadow-lg transform scale-105'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                }`}
              >
                <Send className="w-5 h-5 mr-2" />
                Submit Ticket
              </button>
              <button
                onClick={() => setActiveSection('escalation')}
                className={`flex items-center px-6 py-3 rounded-xl font-medium transition-all duration-300 ${
                  activeSection === 'escalation'
                    ? 'bg-gradient-to-r from-teal-500 to-cyan-500 text-white shadow-lg transform scale-105'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                }`}
              >
                <FileText className="w-5 h-5 mr-2" />
                Escalation Logs
              </button>
            </div>
          </div>

          {activeSection === 'query' && (
            <div className="max-w-2xl mx-auto">
              <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 overflow-hidden">
                <div className="bg-gradient-to-r from-teal-500 to-cyan-500 p-6">
                  <h2 className="text-2xl font-bold text-white flex items-center">
                    <Ticket className="w-6 h-6 mr-3" />
                    Create New Ticket
                  </h2>
                  <p className="text-teal-100 mt-2">Tell us how we can help you today</p>
                </div>

                <div className="p-8 space-y-6">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-gray-700 flex items-center">
                      <User className="w-4 h-4 mr-2 text-teal-500" />
                      Subject
                    </label>
                    <input
                      type="text"
                      name="subject"
                      value={formData.subject}
                      onChange={handleInputChange}
                      placeholder="Brief description of your issue..."
                      required
                      className="w-full border-2 border-gray-200 px-4 py-3 rounded-xl focus:border-teal-500 focus:ring-4 focus:ring-teal-100 transition-all duration-300 bg-gray-50 focus:bg-white"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-gray-700 flex items-center">
                      <FileText className="w-4 h-4 mr-2 text-teal-500" />
                      Description
                    </label>
                    <textarea
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      placeholder="Please provide detailed information about your issue..."
                      required
                      rows={5}
                      className="w-full border-2 border-gray-200 px-4 py-3 rounded-xl focus:border-teal-500 focus:ring-4 focus:ring-teal-100 transition-all duration-300 bg-gray-50 focus:bg-white resize-none"
                    />
                  </div>

                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={submitLoading}
                    className="w-full bg-gradient-to-r from-teal-500 to-cyan-500 text-white font-semibold py-4 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center"
                  >
                    {submitLoading ? (
                      <>
                        <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                        Submitting...
                      </>
                    ) : (
                      <>
                        <Send className="w-5 h-5 mr-2" />
                        Submit Ticket
                      </>
                    )}
                  </button>


                  {response && (
                    <div
                      className={`p-4 rounded-xl border-l-4 flex items-start space-x-3 ${
                        response.status === 'success'
                          ? 'bg-green-50 border-green-400 text-green-800'
                          : 'bg-red-50 border-red-400 text-red-800'
                      }`}
                    >


                      {response.status === 'success' ? (
                        <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                      )}
                      <p className="font-medium">{response.message}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}


          {activeSection === 'escalation' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                  <FileText className="w-6 h-6 mr-3 text-teal-500" />
                  Escalation Logs
                </h2>
                <button
                  onClick={fetchEscalationLogs}
                  className="flex items-center px-4 py-2 bg-gradient-to-r from-teal-500 to-cyan-500 text-white rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-300"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
              </div>

              {error && (
                <div className="p-4 rounded-xl border-l-4 bg-red-50 border-red-400 text-red-800 flex items-start space-x-3">
                  <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-medium">Error loading escalation logs</p>
                    <p className="text-sm mt-1">{error}</p>
                    <p className="text-xs mt-2 text-red-600">Check the browser console for more details.</p>
                  </div>
                </div>
              )}

              {loading ? (
                <div className="flex justify-center items-center py-16">
                  <div className="text-center">
                    <RefreshCw className="w-8 h-8 text-teal-500 mx-auto mb-4 animate-spin" />
                    <p className="text-gray-600 font-medium">Loading escalation logs...</p>
                  </div>
                </div>
              ) : escalationLogs.length === 0 && !error ? (
                <div className="text-center py-16">
                  <div className="w-24 h-24 bg-gradient-to-r from-teal-100 to-cyan-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <FileText className="w-12 h-12 text-teal-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">No Escalations Found</h3>
                  <p className="text-gray-500">All tickets are being handled smoothly!</p>
                </div>
              ) : (
                <div className="grid gap-6">
                  {escalationLogs.map((log, i) => (
                    <div
                      key={i}
                      className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
                    >
                      <div className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <h3 className="text-xl font-bold text-gray-800 flex-1 pr-4">
                            {log.subject}
                          </h3>
                          <span
                            className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getCategoryColor(
                              log.category
                            )}`}
                          >
                            <Tag className="w-3 h-3 mr-1" />
                            {log.category || 'General'}
                          </span>
                        </div>


                        <p className="text-gray-700 mb-4 leading-relaxed">{log.description}</p>


                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center text-gray-500">
                            <Clock className="w-4 h-4 mr-1" />
                            Attempts: <span className="font-semibold ml-1">{log.review_attempts}</span>
                          </div>
                          <div className="flex items-center space-x-4">
                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                            <span className="text-gray-600 font-medium">Active</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};


export default SupportTicketApp;
