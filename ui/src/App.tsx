import { useEffect, useState } from 'react'
import type { Config, LogEntry, Pane } from './types'
import Doctor from './components/Doctor'
import Sidebar from './components/Sidebar'
import Logs from './components/Logs'
import Engineer from './components/Engineer'
import Header from './components/Header'
import ErrorScreen from './components/ErrorScreen'

function App() {
    const _root_dir = new URLSearchParams(window.location.search).get(
        'root_dir'
    )
    const [cfg, setCfg] = useState<Config>()
    const [doctorLogs, setDoctorLogs] = useState<LogEntry[]>([])
    const [engineerLogs, setEngineerLogs] = useState<LogEntry[]>([])
    const [activePane, setActivePane] = useState<Pane>('doctor')
    const [isOnline, setIsOnline] = useState<boolean>(true)
    const [cfgError, setCfgError] = useState<boolean>(false)

    useEffect(() => {
        const checkHealth = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/health')
                if (response.ok) setIsOnline(true)
                else setIsOnline(false)
            } catch {
                setIsOnline(false)
            }
        }
        checkHealth()
        const interval = setInterval(checkHealth, 5000)
        return () => clearInterval(interval)
    }, [])

    useEffect(() => {
        const fetchProjectConfig = async () => {
            if (!_root_dir) return
            try {
                const apiURL = `http://localhost:8000/api/context?root_dir=${_root_dir}`
                const data = await fetch(apiURL)
                if (!data.ok) {
                    const error = await data.json().catch(() => {})
                    throw new Error(
                        error.detail || `HTTP Error: ${data.status}`
                    )
                }
                const config: Config = await data.json()
                config.root_dir = _root_dir
                setCfg(config)
            } catch {
                setCfgError(true)
            }
        }

        if (_root_dir) {
            fetchProjectConfig()
        }
    }, [_root_dir])

    if (!_root_dir) {
        return (
            <ErrorScreen
                title="Root directory Missing"
                description="CodeDoctor requires a root_dir query parameter to index repository files"
                hint="uv run gui /path/to/root"
            />
        )
    }

    if (cfgError) {
        return (
            <ErrorScreen
                title="Missing pyproject.toml"
                description="pyproject.toml was not found at the specified root_dir"
                hint="uv run gui . /path/to/root"
            />
        )
    }

    if (!cfg) {
        return (
            <div className="flex flex-col items-center justify-center bg-slate-950 min-h-screen font-mono text-sm text-slate-500 space-y-3 select-none">
                <div className="w-5 h-5 border-2 border-slate-800 border-t-emerald-500 rounded-full animate-spin"></div>
                <p>Indexing project workspace configuration context...</p>
            </div>
        )
    }
    const updateConfig = <K extends keyof Config>(key: K, value: Config[K]) => {
        setCfg((prevConfig) => {
            if (!prevConfig) return prevConfig
            return { ...prevConfig, [key]: value }
        })
    }

    const clearDoctorLogs = () => {
        setDoctorLogs([])
    }

    const clearEngineerLogs = () => {
        setEngineerLogs([])
    }

    return (
        <div className="flex flex-col bg-slate-950 min-h-screen text-slate-300 selection:bg-slate-800/80">
            {!isOnline && (
                <div className="bg-rose-950/80 border-b border-rose-900/50 text-rose-300 px-4 py-2 text-center text-sm font-semibold font-mono animate-pulse">
                    CodeDoctor Backend offline. Please run{' '}
                    <code className="bg-slate-950 p-1 rounded text-rose-400">
                        uv run fastapi dev
                    </code>
                </div>
            )}

            <div
                className={`flex transition-all duration-200 ${!isOnline ? 'pointer-events-none select-none opacity-40 grayscale-25' : ''}`}
            >
                <Sidebar cfg={cfg} updateConfig={updateConfig} />

                <main className="flex flex-1 flex-col p-8 gap-6 max-w-5xl w-full">
                    <Header isOnline={isOnline} />
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <Doctor
                            cfg={cfg}
                            setLogs={setDoctorLogs}
                            onExecute={() => setActivePane('doctor')}
                        />
                        <Engineer
                            cfg={cfg}
                            setLogs={setEngineerLogs}
                            onExecute={() => setActivePane('engineer')}
                        />
                    </div>

                    <Logs
                        doctorLogs={doctorLogs}
                        engineerLogs={engineerLogs}
                        activePane={activePane}
                        setActivePane={setActivePane}
                        onDoctorClear={clearDoctorLogs}
                        onEngineerClear={clearEngineerLogs}
                    />
                </main>
            </div>
        </div>
    )
}

export default App
