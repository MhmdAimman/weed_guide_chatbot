import { useEffect, useRef } from 'react'
import Message from './Message'

export default function ChatWindow({ messages }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex-1 space-y-4 overflow-y-auto bg-white p-4 sm:p-8">
      {messages.map((msg, i) => (
        <Message key={i} role={msg.role} text={msg.text} />
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
