interface LogsProps {
    logs: string[]
}

export default function Logs({ logs }: LogsProps) {
    return (
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

    )
}
