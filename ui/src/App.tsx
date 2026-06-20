import { useEffect, useState } from "react"
import type { Config } from "./types"
import Doctor from "./components/Doctor"
import Sidebar from "./components/Sidebar"


function App() {
    const _root_dir = new URLSearchParams(window.location.search).get("root_dir")
    const [cfg, setCfg] = useState<Config>()
    const [logs, setLogs] = useState<string[]>([])

    if (!_root_dir) {
        return (
            <div>
                <p>
                    The root directory not found.
                </p>
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
                <p>
                    Error parsing config
                </p>
            </div>
        )
    }

    const updateConfig = <K extends keyof Config>(key: K, value: Config[K], config: Config = cfg) => {
        setCfg(prevConfig => {
            if (!prevConfig) return prevConfig
            return { ...config, [key]: value }
        })
    }

    return (
        <div className="flex bg-slate-700 min-h-screen text-slate-300">
            <Sidebar cfg={cfg} updateConfig={updateConfig} />

            <main className="flex flex-1 flex-col p-8 gap-6 max-w-5xl mx-auto w-full">
                <header className="flex justify-between items-center border-b border-slate-800 pb-4">
                    <h1 className="font-bold text-8xl tracking-tight">CodeDoctor</h1>
                </header>

                <Doctor cfg={cfg} setLogs={setLogs} />

                <div className="p-4 flex-1 overflow-y-auto text-sm text-emerald-300 rounded-lg shadow-xl">
                    {logs.length === 0 ? (<p>No logs</p>) : (
                        logs.map((log, idx) => (
                            <div key={idx}>
                                <span>{new Date().toLocaleTimeString()}</span>
                                <span> </span>
                                <span>{log}</span>
                            </div>
                        ))
                    )}
                </div>
            </main >
        </div >
    )
}

export default App
