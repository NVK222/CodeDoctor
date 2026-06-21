import type React from 'react'

interface ExecutorProps {
    name: string
    onSubmitHandler: (e: React.SubmitEvent) => void
    prompt: string
    setPrompt: React.Dispatch<React.SetStateAction<string>>
    isRunning: boolean
    isPromptRequired: boolean
}

export default function Executor({
    name,
    onSubmitHandler,
    prompt,
    setPrompt,
    isRunning,
    isPromptRequired,
}: ExecutorProps) {
    return (
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 flex flex-col shadow-lg">
            <h2 className="font-bold text-sm text-white tracking-wide border-b border-slate-800 pb-2 flex items-center gap-2">
                <span
                    className={`h-1.5 w-1.5 rounded-full ${name === 'Doctor' ? 'bg-cyan-400' : 'bg-purple-400'}`}
                />
                {name.toUpperCase()}
            </h2>
            <form
                className="flex flex-col gap-3 mt-3"
                onSubmit={onSubmitHandler}
            >
                <div className="flex flex-col gap-1">
                    <label className="text-[12px] font-bold text-slate-500 uppercase tracking-wider">{`Custom instructions for ${name.toLowerCase()} ${!isPromptRequired ? '[OPTIONAL]' : ''}`}</label>
                    <textarea
                        placeholder={
                            isPromptRequired
                                ? 'Enter the instructions...'
                                : 'Enter any specific instructions...'
                        }
                        className="bg-slate-950 border border-slate-800 rounded-lg p-4 text-sm text-slate-300 font-sans focus:outline-none focus:border-emerald-500/50 resize-none disabled:opacity-40 transition-all duration-200"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        disabled={isRunning}
                        rows={2}
                        required={isPromptRequired}
                    />
                </div>

                <button
                    type="submit"
                    disabled={isRunning}
                    className={`w-full py-2.5 rounded-lg text-xs font-bold shadow-md transition-all duration-75 tracking-wider uppercase cursor-pointer ${isRunning ? 'bg-slate-800 text-slate-500 cursor-not-allowed animate-pulse border border-slate-700/30' : 'bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition-colors duration-200'}`}
                >
                    {isRunning ? 'Running...' : 'Execute'}
                </button>
            </form>
        </div>
    )
}
