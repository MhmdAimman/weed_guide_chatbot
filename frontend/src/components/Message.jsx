export default function Message({ role, text }) {
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] whitespace-pre-wrap break-words rounded-2xl px-4 py-3 text-sm leading-6 shadow-lg sm:max-w-[75%] ${
          isUser
            ? 'rounded-br-sm bg-green-200 text-green-950 shadow-green-950/10'
            : 'prose prose-sm max-w-none rounded-bl-sm bg-green-900 text-white shadow-green-950/20 prose-headings:text-white prose-p:text-white prose-strong:text-white prose-li:text-white'
        }`}
      >
        {text}
      </div>
    </div>
  )
}
