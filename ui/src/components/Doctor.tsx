import { useState } from 'react'
import type { Config, LogEntry } from '../types'
import { SSE, type SSEvent } from 'sse.js'
import Executor from './Executor'

interface DoctorProps {
    cfg: Config
    setLogs: React.Dispatch<React.SetStateAction<LogEntry[]>>
}

export default function Doctor({ cfg, setLogs }: DoctorProps) {
    const [doctorPrompt, setDoctorPrompt] = useState<string>('')
    const [isDoctorRunning, setIsDoctorRunning] = useState<boolean>(false)
    const handleRunDoctor = (e: React.SubmitEvent) => {
        e.preventDefault()
        setIsDoctorRunning(true)
        setLogs((prevLogs) => [
            ...prevLogs,
            {
                text: 'Connecting to API...',
                ts: new Date().toLocaleTimeString(),
            },
        ])

        let src = new SSE('http://localhost:8000/api/doctor', {
            headers: { 'Content-Type': 'application/json' },
            payload: JSON.stringify({
                user_prompt: doctorPrompt,
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

        src.addEventListener('done', (r: SSEvent) => {
            const payload = JSON.parse(r.data)
            setLogs((prevLogs) => [
                ...prevLogs,
                { text: `${payload}`, ts: new Date().toLocaleTimeString() },
            ])
            setIsDoctorRunning(false)
        })

        src.addEventListener('log', (r: SSEvent) => {
            const payload = JSON.parse(r.data)
            setLogs((prevLogs) => [
                ...prevLogs,
                { text: `${payload}`, ts: new Date().toLocaleTimeString() },
            ])
        })
    }

    return (
        <Executor
            name="Doctor"
            prompt={doctorPrompt}
            isPromptRequired={false}
            isRunning={isDoctorRunning}
            onSubmitHandler={handleRunDoctor}
            setPrompt={setDoctorPrompt}
        />
    )
}
