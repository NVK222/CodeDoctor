import { useState } from "react"
import type { Config } from "../types"


interface SidebarProps {
    cfg: Config,
    updateConfig: <K extends keyof Config>(key: K, value: Config[K], config?: Config) => void
}

export default function Sidebar({ cfg, updateConfig }: SidebarProps) {
    const [ignoreText, setIgnoreText] = useState<string>(cfg.ignore.join(", "))
    const handleOnBlur = (e: React.FocusEvent<HTMLInputElement, Element>) => {
        const newIgnore = e.target.value.split(",").map(item => item.trim()).filter(Boolean)
        updateConfig("ignore", newIgnore)
        setIgnoreText(newIgnore.join(", "))
    }

    const inputClass = "bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm text-slate-200 font-mono placeholder-slate-600 focus:outline-none focus:border-emerald-500/80 focus:ring-emerald-500/5 transition-all duration-200 w-full"
    const labelClass = "text-[12px] font-bold text-slate-400 uppercase tracking-wider"

    return (
        <aside className="w-72 shrink-0 bg-slate-900 p-5 text-xl border-r border-slate-800/80 flex flex-col gap-6 select-none">
            <div>
                <h2 className="font-bold text-lg text-white tracking-tight"> Configuration </h2>
                <p className="text-xs text-slate-500 mt-1">Adjust your settings here.</p>
            </div>

            <div className="h-px bg-slate-800/60 w-full" />


            <div className="flex flex-col flex-1 text-sm gap-4">
                <div className="flex flex-col gap-1.5">
                    <label className={labelClass} htmlFor="root_dir">Root Directory:  </label>
                    <div className="text-slate-500 tex-xs font-mono p-2 rounded-lg border border-dashed border-slate-800 cursor-not-allowed bg-slate-950/40">
                        {cfg.root_dir.split("/").pop()}
                    </div>
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className={labelClass} htmlFor="search_dir">Search Directory:  </label>
                    <input className={inputClass} id="search_dir" type="text" value={cfg.search_dir} onChange={(e) => updateConfig("search_dir", e.target.value)} />
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className={labelClass} htmlFor="test_dir">Test Directory:  </label>
                    <input className={inputClass} id="test_dir" type="text" value={cfg.test_dir} onChange={(e) => updateConfig("test_dir", e.target.value)} />
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className={labelClass} htmlFor="strong_model">Strong Model:  </label>
                    <input className={inputClass} id="strong_model" type="text" value={cfg.strong_model} onChange={(e) => updateConfig("strong_model", e.target.value)} />
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className={labelClass} htmlFor="weak_model">Weak Model:  </label>
                    <input className={inputClass} id="weak_model" type="text" value={cfg.weak_model} onChange={(e) => updateConfig("weak_model", e.target.value)} />
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className={labelClass} htmlFor="max_retries">Max Retries:  </label>
                    <input className={`${inputClass} [-moz-appearance:textfield] appearance-none `} id="max_retries" type="number" value={cfg.max_retries} onChange={(e) => updateConfig("max_retries", parseInt(e.target.value))} />
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className={labelClass} htmlFor="include">Include Dot:  </label>
                    <div className="flex gap-2 bg-slate-950 p-1 rounded-lg border border-slate-800">
                        <label className={`flex flex-1 gap-2 items-center justify-center py-1.5 rounded-md text-xs font-semibold cursor-pointer transition-all duration-150 ${cfg.include_dot ? "bg-slate-800 text-emerald-400 border border-slate-700/30" : "text-slate-500 hover:text-slate-300"}`}>
                            <input className="hidden" id="include" type="radio" value="true" checked={cfg.include_dot === true} onChange={(e) => updateConfig("include_dot", e.target.value === "true")} />True
                        </label>

                        <label className={`flex flex-1 gap-2 items-center justify-center py-1.5 rounded-md text-xs font-semibold cursor-pointer transition-all duration-150 ${!cfg.include_dot ? "bg-slate-800 text-emerald-400 border border-slate-700/30" : "text-slate-500 hover:text-slate-300"}`} >
                            <input className="hidden" id="include" type="radio" value="false" checked={cfg.include_dot === false} onChange={(e) => updateConfig("include_dot", e.target.value !== "false")} />False
                        </label>
                    </div>
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className={labelClass} htmlFor="ignore">Ignore:  </label>
                    <input className={inputClass} type="text" value={ignoreText} onChange={(e) => setIgnoreText(e.target.value)} onBlur={handleOnBlur} />
                </div>
            </div>
        </aside >
    )
}
