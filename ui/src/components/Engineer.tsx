import { useRef, useState } from 'react'
import type { Config, LogEntry } from '../types'
import { SSE, type SSEvent } from 'sse.js'
import Executor from './Executor'

interface EngineerProps {
    cfg: Config
    setLogs: React.Dispatch<React.SetStateAction<LogEntry[]>>
    onExecute: () => void
}

export default function Engineer({ cfg, setLogs, onExecute }: EngineerProps) {
    const [engineerPrompt, setEngineerPrompt] = useState<string>('')
    const [isEngineerRunning, setIsEngineerRunning] = useState<boolean>(false)
    const sseRef = useRef<SSE | null>(null)
    const handleRunEngineer = (e: React.SubmitEvent) => {
        e.preventDefault()
        if (isEngineerRunning) return
        setIsEngineerRunning(true)
        onExecute()
        setLogs((prevLogs) => [
            ...prevLogs,
            {
                text: 'Connecting to API...',
                ts: new Date().toLocaleTimeString(),
            },
        ])

        const src = new SSE('http://localhost:8000/api/engineer', {
            headers: { 'Content-Type': 'application/json' },
            payload: JSON.stringify({
                user_prompt: engineerPrompt,
                root_dir: cfg.root_dir,
                search_dir: cfg.search_dir,
                test_dir: cfg.test_dir,
                strong_model: cfg.strong_model,
                weak_model: cfg.weak_model,
                max_retries: cfg.max_retries,
                ignore: cfg.ignore,
                include_dot: cfg.include_dot,
            }),
        })

        sseRef.current = src

        src.addEventListener('done', (r: SSEvent) => {
            const payload = JSON.parse(r.data)
            setLogs((prevLogs) => [
                ...prevLogs,
                { text: `${payload}`, ts: new Date().toLocaleTimeString() },
            ])
            src.close()
            setIsEngineerRunning(false)
        })

        src.addEventListener('log', (r: SSEvent) => {
            const payload = JSON.parse(r.data)
            setLogs((prevLogs) => [
                ...prevLogs,
                { text: `${payload}`, ts: new Date().toLocaleTimeString() },
            ])
        })

        src.addEventListener('error', () => {
            src.close()
            setIsEngineerRunning(false)
        })

        src.addEventListener('abort', () => {
            setIsEngineerRunning(false)
        })
    }

    const handleForceStopEngineer = (e: React.MouseEvent) => {
        e.preventDefault()
        e.stopPropagation()

        if (sseRef.current) {
            sseRef.current.close()
            sseRef.current = null
        }
        setIsEngineerRunning(false)
        setLogs((prevLogs) => [
            ...prevLogs,
            {
                text: 'The task was aborted',
                ts: new Date().toLocaleTimeString(),
            },
        ])
    }

    return (
        <Executor
            name="Engineer"
            prompt={engineerPrompt}
            isPromptRequired={true}
            isRunning={isEngineerRunning}
            onSubmitHandler={handleRunEngineer}
            setPrompt={setEngineerPrompt}
            handleForceStopAgent={handleForceStopEngineer}
        />
    )
}
