interface ErrorScreenProps {
    title: string
    description: string
    hint?: string
}

export default function ErrorScreen({
    title,
    description,
    hint,
}: ErrorScreenProps) {
    return (
        <div className="flex flex-col items-center justify-center bg-slate-950 min-h-screen text-slate-300 p-6 font-sans select-none">
            <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl text-center space-y-5">
                <div className="mx-auto w-12 h-12 rounded-full bg-rose-950/50 border border-rose-800/40 flex items-center justify-center text-rose-400 font-mono text-xl font-bold animate-pulse">
                    !
                </div>

                <div className="space-y-2">
                    <h1 className="text-xl font-bold tracking-tight text-slate-100 font-mono">
                        {title}
                    </h1>
                    <p className="text-sm text-slate-400 leading-relaxed">
                        {description}
                    </p>
                </div>

                {hint && (
                    <div className="space-y-2 pt-2">
                        <p className="text-xs text-slate-500 font-mono text-left uppercase tracking-wider pl-1">
                            Recommended Action:
                        </p>
                        <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-left font-mono text-xs text-rose-400/90 flex items-center justify-between group">
                            <code className="whitespace-pre-wrap select-text break-all">
                                {hint}
                            </code>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
