import { useEffect, useRef, useState } from "react";

const PANES = ["doctor", "engineer"] as const
type Panes = typeof PANES[number]

interface LogsProps {
    doctorLogs: string[]
    engineerLogs: string[],
}

interface PaneProps {
    logs: string[]
}

export default function Logs({ doctorLogs, engineerLogs }: LogsProps) {
    const [currentPaneName, setCurrentPaneName] = useState<Panes>("doctor")
    let logs: string[];
    switch (currentPaneName) {
        case "doctor":
            logs = doctorLogs
            break
        case "engineer":
            logs = engineerLogs
            break
        default:
            logs = []
    }

    return (
        <div className="flex flex-col h-96">
            <div className="flex gap-1 text-sm text-slate-300 bg-slate-800 rounded-lg">
                {PANES.map((_pane, idx) => (
                    <button className="p-1 px-4 border-r border-slate-500 cursor-pointer" key={idx} onClick={() => setCurrentPaneName(_pane)}>{_pane.toUpperCase()}</button>
                ))}
            </div>
            <Pane logs={logs} />
        </div>
    )
}

function Pane({ logs }: PaneProps) {
    const divRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (divRef.current) {
            divRef.current.scrollTo({
                top: divRef.current.scrollHeight,
                behavior: "smooth"
            })
        }
    }, [logs])

    return (
        <div ref={divRef} className="p-4 flex-1 overflow-y-auto text-sm rounded-lg shadow-xl">
            {logs.length === 0 ? (<p>No logs</p>) : (
                logs.map((log, idx) => (
                    <div key={idx}>
                        <span className="text-emerald-300">{new Date().toLocaleTimeString()}</span>
                        <span> </span>
                        <span className="text-slate-300">{log}</span>
                    </div>
                ))
            )}
        </div>
    )
}
