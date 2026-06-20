import { useEffect, useState } from "react"
import type { Config, LogEntry } from "./types"
import Doctor from "./components/Doctor"
import Sidebar from "./components/Sidebar"
import Logs from "./components/Logs"
import Engineer from "./components/Engineer"


function App() {
    const _root_dir = new URLSearchParams(window.location.search).get("root_dir")
    const [cfg, setCfg] = useState<Config>()
    const [doctorLogs, setDoctorLogs] = useState<LogEntry[]>([])
    const [engineerLogs, setEngineerLogs] = useState<LogEntry[]>([])

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
                    <h1 className="font-bold text-4xl tracking-tight">CodeDoctor</h1>
                </header>

                <Doctor cfg={cfg} setLogs={setDoctorLogs} />
                <Engineer cfg={cfg} setLogs={setEngineerLogs} />

                <Logs doctorLogs={doctorLogs} engineerLogs={engineerLogs} />
            </main >
        </div >
    )
}

export default App
