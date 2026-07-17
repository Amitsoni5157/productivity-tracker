"use client";

import { useState, useEffect } from "react";

interface Profile {
  id: string;
  name: string;
  profession: string;
}

interface AnalysisReport {
  success: boolean;
  analysis: {
    productive_hours: number;
    wasted_hours: number;
    rating: number;
  };
  final_report: string;
}

export default function Home() {
  // Profiles states
  const [profile, setProfile] = useState<Profile | null>(null);
  const [name, setName] = useState("");
  const [profession, setProfession] = useState("");

  // App states
  const [rawLog, setRawLog] = useState("");
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [profileLoading, setProfileLoading] = useState(false);

  // Check if profile exists in LocalStorage on load
  useEffect(() => {
    const savedProfile = localStorage.getItem("focus_ai_profile");
    if (savedProfile) {
      setProfile(JSON.parse(savedProfile));
    }
  }, []);

  // Handle Profile Creation
  const handleCreateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !profession) {
      setError("Please fill in both Name and Profession.");
      return;
    }

    setError("");
    setProfileLoading(true);

    try {
      const res = await fetch("http://localhost:8000/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, profession }),
      });
      const data = await res.json();

      if (data.success && data.profile) {
        const newProfile: Profile = data.profile;
        setProfile(newProfile);
        localStorage.setItem("focus_ai_profile", JSON.stringify(newProfile));
      } else {
        setError(data.detail || "Failed to create profile.");
      }
    } catch (err) {
      setError("Cannot connect to the backend server. Make sure FastAPI is running.");
    } finally {
      setProfileLoading(false);
    }
  };

  // Handle Log Analysis (LangGraph Agent call)
  const handleAnalyzeLogs = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile || !rawLog) {
      setError("Please enter your activity logs.");
      return;
    }

    setError("");
    setLoading(true);
    setReport(null);

    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile_id: profile.id,
          profession: profile.profession,
          raw_log: rawLog,
        }),
      });
      const data = await res.json();

      if (data.success) {
        setReport(data);
      } else {
        setError(data.detail || "Failed to analyze logs.");
      }
    } catch (err) {
      setError("Error calling the AI Agent. Please check the backend console.");
    } finally {
      setLoading(false);
    }
  };

  // Logout/Reset Profile
  const handleResetProfile = () => {
    localStorage.removeItem("focus_ai_profile");
    setProfile(null);
    setReport(null);
    setRawLog("");
    setName("");
    setProfession("");
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans select-none antialiased">
      {/* Top Header */}
      <header className="border-b border-zinc-900 bg-zinc-950/80 backdrop-blur-md py-4 px-6 sticky top-0 z-50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="h-4 w-4 rounded-full bg-emerald-500 animate-pulse"></span>
          <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-emerald-400 to-indigo-400 bg-clip-text text-transparent">
            FocusAI Dashboard
          </h1>
        </div>
        {profile && (
          <div className="flex items-center gap-4">
            <span className="text-sm text-zinc-400">
              User: <strong className="text-zinc-200">{profile.name}</strong> ({profile.profession})
            </span>
            <button
              onClick={handleResetProfile}
              className="text-xs text-rose-400 hover:text-rose-300 border border-rose-950 bg-rose-950/20 px-2.5 py-1.5 rounded transition-all"
            >
              Reset Account
            </button>
          </div>
        )}
      </header>

      {/* Main Grid */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-6 md:p-8 flex flex-col justify-center">
        {error && (
          <div className="mb-6 p-4 rounded bg-rose-950/40 border border-rose-900 text-rose-300 text-sm">
            ⚠️ {error}
          </div>
        )}

        {!profile ? (
          /* Profile Setup Screen */
          <div className="max-w-md w-full mx-auto bg-zinc-900/50 border border-zinc-800 rounded-xl p-8 backdrop-blur-md shadow-2xl">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-semibold mb-2">Configure Your Profile</h2>
              <p className="text-sm text-zinc-400">Tell us your profession to get personalized AI productivity insights.</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs uppercase tracking-wider text-zinc-400 mb-1">Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Amit Soni"
                  className="w-full bg-zinc-950 border border-zinc-850 rounded px-4 py-2.5 text-zinc-150 focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
              <div>
                <label className="block text-xs uppercase tracking-wider text-zinc-400 mb-1">Profession</label>
                <input
                  type="text"
                  value={profession}
                  onChange={(e) => setProfession(e.target.value)}
                  placeholder="e.g. Software Engineer, Student"
                  className="w-full bg-zinc-950 border border-zinc-850 rounded px-4 py-2.5 text-zinc-150 focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
              <button
                onClick={handleCreateProfile}
                disabled={profileLoading}
                className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 text-white font-medium rounded transition-colors mt-2"
              >
                {profileLoading ? "Creating Profile..." : "Get Started"}
              </button>
            </div>
          </div>
        ) : (
          /* Dashboard Main Workspace */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

            {/* Left Side: Input Logs Form */}
            <div className="lg:col-span-5 bg-zinc-900/40 border border-zinc-850 rounded-xl p-6 backdrop-blur-md">
              <h2 className="text-lg font-semibold mb-3">Today's Activity Logger</h2>
              <p className="text-xs text-zinc-400 mb-4 leading-relaxed">
                Describe your daily schedule naturally. Mention times and details of both productive tasks and distractions.
              </p>

              <form onSubmit={handleAnalyzeLogs} className="space-y-4">
                <textarea
                  value={rawLog}
                  onChange={(e) => setRawLog(e.target.value)}
                  placeholder="e.g.,&#10;10:00 to 12:30 - coding backend endpoints&#10;12:30 to 14:00 - scrolled Instagram&#10;14:00 to 18:00 - debugged LangGraph agents"
                  rows={8}
                  className="w-full bg-zinc-950/70 border border-zinc-850 rounded p-4 text-zinc-150 focus:outline-none focus:border-indigo-500 transition-colors text-sm font-mono leading-relaxed"
                />
                <button
                  type="submit"
                  disabled={loading || !rawLog}
                  className="w-full py-3 bg-gradient-to-r from-emerald-500 to-indigo-600 hover:from-emerald-400 hover:to-indigo-500 disabled:from-zinc-800 disabled:to-zinc-900 disabled:text-zinc-500 font-medium rounded transition-all shadow-md shadow-indigo-900/20"
                >
                  {loading ? "AI Agent is Analyzing..." : "Generate Analysis Report"}
                </button>
              </form>
            </div>

            {/* Right Side: Analysis Display */}
            <div className="lg:col-span-7 flex flex-col gap-6">
              {loading && (
                <div className="bg-zinc-900/20 border border-zinc-900 rounded-xl p-12 text-center flex flex-col items-center justify-center min-h-[300px]">
                  <div className="h-10 w-10 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mb-4"></div>
                  <h3 className="font-medium text-zinc-300">Evaluating your productivity...</h3>
                  <p className="text-xs text-zinc-500 mt-2">Triggering LangGraph workflow & running web search tools.</p>
                </div>
              )}

              {!loading && !report && (
                <div className="bg-zinc-900/20 border border-zinc-900 rounded-xl p-12 text-center min-h-[300px] flex flex-col justify-center items-center">
                  <div className="h-12 w-12 rounded-full bg-zinc-950 flex items-center justify-center mb-4 text-zinc-500">📊</div>
                  <h3 className="font-medium text-zinc-400">No Report Generated Yet</h3>
                  <p className="text-xs text-zinc-600 mt-2">Type your daily logs on the left and hit the button to trigger AI analysis.</p>
                </div>
              )}

              {!loading && report && (
                <div className="space-y-6">
                  {/* Dashboard Metrics Cards */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-zinc-900/50 border border-zinc-850 p-4 rounded-xl text-center">
                      <span className="text-[10px] uppercase text-zinc-500 tracking-wider">Productive Time</span>
                      <p className="text-xl font-bold text-emerald-400 mt-1">{report.analysis.productive_hours} hrs</p>
                    </div>
                    <div className="bg-zinc-900/50 border border-zinc-850 p-4 rounded-xl text-center">
                      <span className="text-[10px] uppercase text-zinc-500 tracking-wider">Wasted Time</span>
                      <p className="text-xl font-bold text-rose-400 mt-1">{report.analysis.wasted_hours} hrs</p>
                    </div>
                    <div className="bg-zinc-900/50 border border-zinc-850 p-4 rounded-xl text-center">
                      <span className="text-[10px] uppercase text-zinc-500 tracking-wider">Focus Rating</span>
                      <p className="text-xl font-bold text-indigo-400 mt-1">{report.analysis.rating}/100</p>
                    </div>
                  </div>

                  {/* Written Markdown Coach Report */}
                  <div className="bg-zinc-900/40 border border-zinc-850 rounded-xl p-6 md:p-8 backdrop-blur-md">
                    <div className="flex items-center justify-between border-b border-zinc-800 pb-3 mb-5">
                      <h3 className="font-semibold text-lg">AI Coach Deep Dive</h3>
                      <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-900 px-2.5 py-1 rounded-full font-medium">
                        Focus Log Saved
                      </span>
                    </div>
                    <div className="prose prose-invert max-w-none text-zinc-300 text-sm leading-relaxed whitespace-pre-wrap font-sans">
                      {report.final_report}
                    </div>
                  </div>
                </div>
              )}
            </div>

          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="py-6 px-6 border-t border-zinc-950 text-center text-xs text-zinc-600 bg-zinc-950/40 mt-auto">
        Powered by Next.js, FastAPI, LangGraph & Supabase PostgreSQL (pgvector).
      </footer>
    </div>
  );
}
