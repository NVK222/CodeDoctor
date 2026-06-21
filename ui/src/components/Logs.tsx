import { useEffect, useRef } from 'react'
import { allPanes, type LogEntry, type Pane } from '../types'

interface LogsProps {
    doctorLogs: LogEntry[]
    engineerLogs: LogEntry[]
    activePane: Pane
    setActivePane: React.Dispatch<React.SetStateAction<Pane>>
    onDoctorClear: () => void
    onEngineerClear: () => void
}

interface PaneProps {
    logs: LogEntry[]
}

export default function Logs({
    doctorLogs,
    engineerLogs,
    activePane,
    setActivePane,
    onDoctorClear,
    onEngineerClear,
}: LogsProps) {
    let logs: LogEntry[]
    switch (activePane) {
        case 'doctor':
            logs = doctorLogs
            break
        case 'engineer':
            logs = engineerLogs
            break
        default:
            logs = []
    }

    const handleClearLogs = () => {
        switch (activePane) {
            case 'doctor':
                onDoctorClear()
                break
            case 'engineer':
                onEngineerClear()
                break
            default:
                break
        }
    }

    return (
        <div className="flex flex-col h-96 bg-black border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
            <div className="flex justify-between items-center bg-slate-900/80 px-4 py-2 border-b border-slate-800/80 backdrop-blur-sm">
                <div className="flex items-center gap-3">
                    <div className="flex gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800/60 text-xs text-mono">
                        {allPanes.map((_pane, idx) => {
                            const isActive = activePane === _pane
                            return (
                                <button
                                    className={`px-4 py-1 rounded-md font-bold transition-all duration-75 cursor-pointer ${
                                        isActive
                                            ? 'bg-slate-800 text-emerald-400 shadow-sm border border-slate-750/50'
                                            : 'text-slate-500 hover:text-slate-300'
                                    }`}
                                    key={idx}
                                    onClick={() => setActivePane(_pane)}
                                >
                                    {_pane.toUpperCase()}
                                </button>
                            )
                        })}
                    </div>

                    <button
                        onClick={() => handleClearLogs()}
                        title={`Clear ${activePane} logs`}
                        className="p-1.5 px-2 rounded-lg text-xs font-semibold font-mono border border-slate-800 bg-slate-900 hover:bg-rose-950/30 hover:border-rose-900/50 text-slate-400 hover:text-rose-400 cursor-pointer transition-all duration-150 flex items-center gap-2"
                    >
                        <svg
                            className="w-3.5 h-3.5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-4v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                            />
                        </svg>
                    </button>
                </div>
                <div className="flex gap-1.5 opacity-60">
                    <span className="h-2.5 w-2.5 rounded-full bg-rose-500/70"></span>
                    <span className="h-2.5 w-2.5 rounded-full bg-amber-500/70"></span>
                    <span className="h-2.5 w-2.5 rounded-full bg-emerald-500/70"></span>
                </div>{' '}
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
                behavior: 'smooth',
            })
        }
    }, [logs])

    return (
        <div
            ref={divRef}
            className="p-4 flex-1 overflow-y-auto text-mono space-y-1.5 bg-slate-950 scrollbar-thin selection:bg-emerald-900/50"
        >
            {logs.length === 0 ? (
                <p className="text-slate-600 italic select-none">No logs</p>
            ) : (
                logs.map((log, idx) => (
                    <div
                        key={idx}
                        className="flex items-start gap-3 border-l border-slate-800 pl-2 hover:bg-slate-900/30 py-0.5 rounded transition-colors"
                    >
                        <span className="text-emerald-400/90 select-none text-[12px] tracking-light font-sans">
                            {log.ts}
                        </span>
                        <span> </span>
                        <span className="text-slate-500 whitespace-pre-wrap leading-relaxed">
                            {log.text}
                        </span>
                    </div>
                ))
            )}
        </div>
    )
}
