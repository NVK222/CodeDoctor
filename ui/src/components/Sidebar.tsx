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
    return (
        <aside className="max-w-1/4 bg-slate-900 text-white p-2 text-xl">
            <h2 className="font-bold text-2xl py-8"> Config </h2>
            {!cfg ? <div><p>Config Not Found</p></div> : <div className="flex flex-col flex-1 text-sm gap-4">
                <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider" htmlFor="root_dir">Root Directory:  </label>
                    <input className="bg-slate-800 border-slate-900 text-slate-500 cursor-not-allowed opacity-60 p-2 text-sm" id="root_dir" type="text" value={cfg.root_dir} disabled={true} />
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider" htmlFor="search_dir">Search Directory:  </label>
                    <input className="bg-slate-700 border border-slate-800 p-2 text-sm" id="search_dir" type="text" value={cfg.search_dir} onChange={(e) => updateConfig("search_dir", e.target.value)} />
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider" htmlFor="test_dir">Test Directory:  </label>
                    <input className="bg-slate-700 border border-slate-800 p-2 text-sm" id="test_dir" type="text" value={cfg.test_dir} onChange={(e) => updateConfig("test_dir", e.target.value)} />
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider" htmlFor="strong_model">Strong Model:  </label>
                    <input className="bg-slate-700 border border-slate-800 p-2 text-sm" id="strong_model" type="text" value={cfg.strong_model} onChange={(e) => updateConfig("strong_model", e.target.value)} />
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider" htmlFor="weak_model">Weak Model:  </label>
                    <input className="bg-slate-700 border border-slate-800 p-2 text-sm" id="weak_model" type="text" value={cfg.weak_model} onChange={(e) => updateConfig("weak_model", e.target.value)} />
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider" htmlFor="max_retries">Max Retries:  </label>
                    <input className="bg-slate-700 border border-slate-800 p-2 text-sm" id="max_retries" type="number" value={cfg.max_retries} onChange={(e) => updateConfig("max_retries", parseInt(e.target.value))} />
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider" htmlFor="include">Include Dot:  </label>
                    <div className="flex gap-1.5 justify-around bg-slate-700 p-2">
                        <div className="flex gap-2">
                            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider" >True</label>
                            <input id="include" type="radio" value="true" checked={cfg.include_dot === true} onChange={(e) => updateConfig("include_dot", e.target.value === "true")} />
                        </div>
                        <div className="flex gap-2">
                            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider" >False</label>
                            <input id="include" type="radio" value="false" checked={cfg.include_dot === false} onChange={(e) => updateConfig("include_dot", e.target.value !== "false")} />

                        </div>
                    </div>
                </div>
                <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider" htmlFor="ignore">Ignore:  </label>
                    <input className="bg-slate-700 border border-slate-800 p-2 text-sm" type="text" value={ignoreText} onChange={(e) => setIgnoreText(e.target.value)} onBlur={handleOnBlur} />
                </div>
            </div>}
        </aside >
    )
}
