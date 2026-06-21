export interface Config {
    root_dir: string
    search_dir: string
    test_dir: string
    strong_model: string
    weak_model: string
    max_retries: number
    include_dot: boolean
    ignore: string[]
}

export interface LogEntry {
    text: string
    ts: string
}

export const allPanes = ['doctor', 'engineer'] as const
export type Pane = (typeof allPanes)[number]
