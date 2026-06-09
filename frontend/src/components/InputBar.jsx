import { useState } from 'react'

export default function InputBar({ onSend, disabled }) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || disabled) return
    onSend(input.trim())
    setInput('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 border-t border-green-200 bg-white p-3 shadow-[0_-8px_24px_rgba(20,83,45,0.06)] sm:p-4">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={disabled}
        placeholder={disabled ? 'Waiting for response...' : 'Type a category, species, description, or topic...'}
        className="min-w-0 flex-1 rounded-xl border border-green-300 bg-white px-4 py-3 text-green-950 placeholder-green-500 outline-none transition focus:border-green-700 focus:ring-2 focus:ring-green-200 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className="rounded-xl bg-green-800 px-5 py-3 font-semibold text-white transition hover:bg-green-900 disabled:bg-green-100 disabled:text-green-400 disabled:opacity-80"
      >
        Send
      </button>
    </form>
  )
}
