import { useEffect, useRef, useState } from "react";
import type { LogEntry } from "../types";

const PANES = ["doctor", "engineer"] as const
type Panes = typeof PANES[number]

interface LogsProps {
    doctorLogs: LogEntry[]
    engineerLogs: LogEntry[],
}

interface PaneProps {
    logs: LogEntry[]
}

export default function Logs({ doctorLogs, engineerLogs }: LogsProps) {
    const [currentPaneName, setCurrentPaneName] = useState<Panes>("doctor")
    let logs: LogEntry[];
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
                        <span className="text-emerald-300">{log.ts}</span>
                        <span> </span>
                        <span className="text-slate-300">{log.text}</span>
                    </div>
                ))
            )}
        </div>
    )
}
