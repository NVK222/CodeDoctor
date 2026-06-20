
import { useState } from "react"
import type { Config } from "../types"
import { SSE, type SSEvent } from "sse.js"
import Executor from "./Executor"

interface EngineerProps {
    cfg: Config,
    setLogs: React.Dispatch<React.SetStateAction<string[]>>
}

export default function Engineer({ cfg, setLogs }: EngineerProps) {
    const [engineerPrompt, setEngineerPrompt] = useState<string>("")
    const [isEngineerRunning, setIsEngineerRunning] = useState<boolean>(false)
    const handleRunEngineer = (e: React.SubmitEvent) => {
        e.preventDefault()
        setIsEngineerRunning(true)
        setLogs(["Connecting to API..."])

        let src = new SSE("http://localhost:8000/api/engineer", {
            headers: { "Content-Type": "application/json" },
            payload: JSON.stringify({
                user_prompt: engineerPrompt,
                root_dir: cfg.root_dir,
                search_dir: cfg.search_dir,
                test_dir: cfg.test_dir,
                strong_model: cfg.strong_model,
                weak_model: cfg.weak_model,
                max_retries: cfg.max_retries,
                ignore: cfg.ignore,
                include_dot: cfg.include_dot
            }),
        })

        src.addEventListener("done", (r: SSEvent) => {
            const payload = JSON.parse(r.data)
            setLogs((prevLogs) => [...prevLogs, `${payload}`])
            setIsEngineerRunning(false)
        })

        src.addEventListener("log", (r: SSEvent) => {
            const payload = JSON.parse(r.data)
            setLogs((prevLogs) => [...prevLogs, `${payload}`])
        })
    }

    return (
        <Executor name="Engineer" prompt={engineerPrompt} isPromptRequired={true} isRunning={isEngineerRunning} onSubmitHandler={handleRunEngineer} setPrompt={setEngineerPrompt} />
    )
}
