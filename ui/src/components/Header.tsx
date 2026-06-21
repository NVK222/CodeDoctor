interface HeaderProps {
    isOnline: boolean
}

export default function Header({ isOnline }: HeaderProps) {
    return (
        <header className="flex justify-between items-center border-b border-slate-900 pb-4">
            <div>
                <div className="flex items-center gap-2.5">
                    <h1 className="font-extrabold text-2xl tracking-tight text-white">
                        CodeDoctor
                    </h1>
                    <span
                        className={`h-2 w-2 rounded-full transition-colors duration-300 shadow-md shrink-0 translate-y-0.75 ${
                            isOnline ? 'bg-emerald-500' : 'bg-rose-500'
                        }`}
                    />{' '}
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                    Automated codebase diagnostics
                </p>
            </div>
        </header>
    )
}
