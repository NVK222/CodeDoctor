import type React from "react"

interface ExecutorProps {
    name: string,
    onSubmitHandler: (e: React.SubmitEvent) => void,
    prompt: string,
    setPrompt: React.Dispatch<React.SetStateAction<string>>
    isRunning: boolean,
    isPromptRequired: boolean
}


export default function Executor({ name, onSubmitHandler, prompt, setPrompt, isRunning, isPromptRequired }: ExecutorProps) {
    return (
        <div>
            <h2 className="font-bold text-2xl text-white py-4">{name.toUpperCase()}</h2>
            <form className="flex flex-col gap-1 border border-slate-700 rounded-2xl p-4 shadow-xl" onSubmit={onSubmitHandler}>
                <label className="text-sm font-semibold text-slate-300">{`Custom instructions for ${name.toLowerCase()} ${!isPromptRequired ? "[OPTIONAL]" : ""}`}</label>
                <textarea placeholder="Type your custom instructions" className="bg-slate-900 border border-slate-700 rounded-lg p-4 text-sm focus:outline-none focus:border-emerald-500 resize-none disabled:opacity-50 transition-colors" value={prompt} onChange={(e) => setPrompt(e.target.value)} disabled={isRunning} rows={2} required={isPromptRequired} />

                <button type="submit" disabled={isRunning} className={`w-full py-4 rounded-lg text-sm font-semibold shadow-md transition-all ${isRunning ? "bg-slate-700 text-slate-300 cursor-not-allowed animate-pulse" : "bg-emerald-500 text-white font-bold tracking-wide"}`}>{isRunning ? "Running..." : "Execute"}</button>
            </form>
        </div >
    )
}
