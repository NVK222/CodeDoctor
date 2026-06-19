import { useEffect, useState } from "react"
import { SSE } from "sse.js"

interface Config {
    search_dir: string,
    test_dir: string,
    strong_model: string,
    weak_model: string,
    max_retries: number,
    include_dot: boolean,
    ignore: Array<string>
}

function App() {
    const queryParams = new URLSearchParams(window.location.search)
    const root_dir = queryParams.get("root_dir")
    const [cfg, setCfg] = useState<Config>()
    const [doctorPrompt, setDoctorPrompt] = useState<string>("")
    const [isDoctorRunning, setIsDoctorRunning] = useState<boolean>(false)
    const [logs, setLogs] = useState<string[]>([])

    const handleRunDoctor = (e: React.SubmitEvent) => {
        e.preventDefault()
        setIsDoctorRunning(true)
        setLogs(["Connecting to API..."])

        let src = new SSE("http://localhost:8000/api/doctor", {
            headers: { "Content-Type": "application/json" },
            payload: `{"root_dir": "${root_dir}", "user_prompt": "${doctorPrompt}"}`,
        })

        src.addEventListener("done", (r) => {
            const payload = JSON.parse(r.data)
            setLogs((prevLogs) => [...prevLogs, `${payload}`])
            setIsDoctorRunning(false)
        })

        src.addEventListener("log", (r) => {
            const payload = JSON.parse(r.data)
            setLogs((prevLogs) => [...prevLogs, `${payload}`])
        })
    }

    if (!root_dir) {
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
            const apiURL = `http://localhost:8000/api/context?root_dir=${root_dir}`
            const data = await fetch(apiURL)
            const config: Config = await data.json()
            setCfg(config)
        }

        if (root_dir) {
            fetchProjectConfig()
        }
    }, [root_dir])


    return (
        <div className="flex bg-slate-700 min-h-screen text-slate-300">
            <aside className="max-w-1/4 bg-slate-900 text-white p-2 text-xl">
                <div>
                    <p>{decodeURIComponent(root_dir)}</p>
                </div>
                <hr />
                <h2 className="font-bold text-2xl py-8"> Config </h2>
                {!cfg ? <div><p>Config Not Found</p></div> : <div>
                    <p>Search Dir :  {cfg.search_dir}</p>
                    <p>Test Dir :  {cfg.test_dir}</p>
                    <p>Strong Model :  {cfg.strong_model}</p>
                    <p>Weak Model :  {cfg.weak_model}</p>
                    <p>Max Retries :  {cfg.max_retries}</p>
                    <p>Include Dot :  {String(cfg.include_dot)}</p>
                    <p>Ignore :  {cfg.ignore.join(", ")}</p>
                </div>}
            </aside >

            <main className="flex flex-1 flex-col p-8 gap-6 max-w-5xl mx-auto w-full">
                <header className="flex justify-between items-center border-b border-slate-800 pb-4">
                    <h1 className="font-bold text-8xl tracking-tight">CodeDoctor</h1>
                </header>

                <div>
                    <h2 className="font-bold text-2xl text-white py-4">Doctor</h2>
                    <form className="flex flex-col gap-1 border border-slate-700 rounded-2xl p-4 shadow-xl" onSubmit={handleRunDoctor}>
                        <label className="text-sm font-semibold text-slate-300">Custom instructions for doctor</label>
                        <textarea placeholder="Type your custom instructions" className="bg-slate-900 border border-slate-700 rounded-lg p-4 text-sm focus:outline-none focus:border-emerald-500 resize-none disabled:opacity-50 transition-colors" value={doctorPrompt} onChange={(e) => setDoctorPrompt(e.target.value)} disabled={isDoctorRunning} rows={2} />

                        <button type="submit" disabled={isDoctorRunning} className={`w-full py-4 rounded-lg text-sm font-semibold shadow-md transition-all ${isDoctorRunning ? "bg-slate-700 text-slate-300 cursor-not-allowed animate-pulse" : "bg-emerald-500 text-white font-bold tracking-wide"}`}>{isDoctorRunning ? "Running..." : "Execute"}</button>
                    </form>
                </div>

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
