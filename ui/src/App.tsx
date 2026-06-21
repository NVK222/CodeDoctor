import { useEffect, useState } from 'react'
import type { Config, LogEntry, Pane } from './types'
import Doctor from './components/Doctor'
import Sidebar from './components/Sidebar'
import Logs from './components/Logs'
import Engineer from './components/Engineer'

function App() {
    const _root_dir = new URLSearchParams(window.location.search).get(
        'root_dir'
    )
    const [cfg, setCfg] = useState<Config>()
    const [doctorLogs, setDoctorLogs] = useState<LogEntry[]>([])
    const [engineerLogs, setEngineerLogs] = useState<LogEntry[]>([])
    const [activePane, setActivePane] = useState<Pane>('doctor')

    if (!_root_dir) {
        return (
            <div>
                <p>The root directory not found.</p>
            </div>
        )
    }

    useEffect(() => {
        const fetchProjectConfig = async () => {
            const apiURL = `http://localhost:8000/api/context?root_dir=${_root_dir}`
            const data = await fetch(apiURL)
            const config: Config = await data.json()
            config.root_dir = _root_dir
            setCfg(config)
        }

        if (_root_dir) {
            fetchProjectConfig()
        }
    }, [_root_dir])

    if (!cfg) {
        return (
            <div>
                <p>Error parsing config</p>
            </div>
        )
    }

    const updateConfig = <K extends keyof Config>(
        key: K,
        value: Config[K],
        config: Config = cfg
    ) => {
        setCfg((prevConfig) => {
            if (!prevConfig) return prevConfig
            return { ...config, [key]: value }
        })
    }

    const clearDoctorLogs = () => {
        setDoctorLogs([])
    }

    const clearEngineerLogs = () => {
        setEngineerLogs([])
    }

    return (
        <div className="flex bg-slate-950 min-h-screen text-slate-300 selection:bg-slate-800/80">
            <Sidebar cfg={cfg} updateConfig={updateConfig} />

            <main className="flex flex-1 flex-col p-8 gap-6 max-w-5xl w-full">
                <header className="flex justify-between items-center border-b border-slate-900 pb-4">
                    <div>
                        <h1 className="font-extrabold text-2xl tracking-tight text-white">
                            CodeDoctor
                        </h1>
                        <p className="text-xs text-slate-500 mt-0.5">
                            Automated codebase diagnostics
                        </p>
                    </div>
                </header>

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
    )
}

export default App
