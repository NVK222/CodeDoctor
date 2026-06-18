import { useEffect, useState } from "react"

interface Config {
    search_dir: string,
    test_dir: string,
    strong_model: string,
    weak_model: string,
    max_retries: number,
    include_dot: boolean,
    ignore: Array<string>
}

function App() {
    const queryParams = new URLSearchParams(window.location.search)
    const root_dir = queryParams.get("root_dir")

    const [cfg, setCfg] = useState<Config>()

    if (!root_dir) {
        return (
            <div>
                <p>
                    The root directory not found.
                </p>
            </div>
        )
    }

    useEffect(() => {
        const fetchProjectConfig = async () => {
            const apiURL = `http://localhost:8000/api/context?root_dir=${root_dir}`
            const data = await fetch(apiURL)
            const config: Config = await data.json()
            setCfg(config)
        }

        if (root_dir) {
            fetchProjectConfig()
        }
    }, [root_dir])


    return (
        <div className="flex bg-slate-700 min-h-screen">
            <aside className="max-w-1/4 bg-slate-900 text-white p-2 text-xl">
                <div>
                    <p>{decodeURIComponent(root_dir)}</p>
                </div>
                <hr />
                <h2 className="font-bold text-2xl py-8"> Config </h2>
                {!cfg ? <div><p>Config Not Found</p></div> : <div>
                    <p>Search Dir :  {cfg.search_dir}</p>
                    <p>Test Dir :  {cfg.test_dir}</p>
                    <p>Strong Model :  {cfg.strong_model}</p>
                    <p>Weak Model :  {cfg.weak_model}</p>
                    <p>Max Retries :  {cfg.max_retries}</p>
                    <p>Include Dot :  {String(cfg.include_dot)}</p>
                    <p>Ignore :  {cfg.ignore.join(", ")}</p>
                </div>}

            </aside >
            <hr />
        </div >
    )
}

export default App
