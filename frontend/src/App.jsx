import { useState } from 'react'
import ChatWindow from './components/ChatWindow'
import InputBar from './components/InputBar'
import { sendMessage } from './api'

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      text: 'Ask about weed identification, control methods, or lifecycles from the Las Animas County Weed Management Pocket Guide.\n\nExample: type "thistle", then type the specific species, then type "Control Methods".',
    },
  ])
  const [loading, setLoading] = useState(false)
  const [chatState, setChatState] = useState(null)

  const handleSend = async (text) => {
    setMessages((prev) => [...prev, { role: 'user', text }])
    setLoading(true)

    try {
      const data = await sendMessage(text, chatState)
      setMessages((prev) => [...prev, { role: 'bot', text: data.reply }])
      setChatState(data.state || null)
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'bot', text: 'Sorry, something went wrong. Please try again.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-screen min-h-screen bg-white text-green-950">
      <main className="flex h-screen w-full flex-col bg-white">
        <header className="border-b border-green-200 bg-white px-5 py-4 shadow-sm sm:px-8">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-green-700">Las Animas County</p>
          <h1 className="mt-1 text-2xl font-bold text-green-950 sm:text-3xl">Weed Guide Chatbot</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-green-800">
            Type a category, species name, plant description, or topic. The assistant answers only from the local pocket guide.
          </p>
        </header>

        <section className="flex min-h-0 flex-1 flex-col overflow-hidden bg-white">
          <ChatWindow messages={messages} />
          {loading && (
            <div className="bg-white px-5 pb-3 sm:px-8">
              <div className="inline-flex rounded-full bg-green-50 px-3 py-1 text-sm text-green-700 animate-pulse">
                Thinking...
              </div>
            </div>
          )}
          <InputBar onSend={handleSend} disabled={loading} />
        </section>
      </main>
    </div>
  )
}
