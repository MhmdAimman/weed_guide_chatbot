export async function sendMessage(message, state) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, state }),
  })
  if (!res.ok) throw new Error('API request failed')
  return res.json()
}
