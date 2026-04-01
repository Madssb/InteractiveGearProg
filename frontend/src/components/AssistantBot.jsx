import triggerReplies from '@/data/bot-triggers.json';
import replies from '@/data/replies.json';
import '@/styles/assistant-bot.css';
import { useState } from 'react';

function randomReply() {
  return replies[Math.floor(Math.random() * replies.length)];
}

function pickReply(message) {
  const normalizedMessage = message.toLowerCase();

  for (const [phrase, reply] of Object.entries(triggerReplies)) {
    if (normalizedMessage.includes(phrase)) return reply;
  }

  return randomReply();
}

export default function AssistantBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [draft, setDraft] = useState('');
  const [messages, setMessages] = useState([
    {
      author: 'bot',
      text: 'Hello. I am the assistant bot. My strengths are enthusiasm and unpredictability.'
    }
  ]);

  function handleSend() {
    const trimmed = draft.trim();
    if (!trimmed) return;

    setMessages(prev => [
      ...prev,
      { author: 'user', text: trimmed },
      { author: 'bot', text: pickReply(trimmed) }
    ]);
    setDraft('');
  }

  function handleSubmit(event) {
    event.preventDefault();
    handleSend();
  }

  return (
    <>
      <button
        id="assistant-launcher"
        type="button"
        onClick={() => setIsOpen(true)}
        aria-haspopup="dialog"
        aria-expanded={isOpen}
      >
        open botlor
      </button>

      {isOpen && (
        <section
          className="assistant-bot"
          role="dialog"
          aria-modal="false"
          aria-label="Assistant bot"
        >
          <header className="assistant-bot__header">
            <div>
              <strong>Botlor</strong>
              <p>trained by bruce sailor himself</p>
            </div>
            <button
              className="assistant-bot__close"
              type="button"
              onClick={() => setIsOpen(false)}
              aria-label="Close assistant bot"
            >
              x
            </button>
          </header>

          <div className="assistant-bot__messages">
            {messages.map((message, index) => (
              <article
                key={`${message.author}-${index}`}
                className={`assistant-bot__message assistant-bot__message--${message.author}`}
              >
                <span className="assistant-bot__label">
                  {message.author === 'bot' ? 'Bot' : 'You'}
                </span>
                <p>{message.text}</p>
              </article>
            ))}
          </div>

          <form className="assistant-bot__composer" onSubmit={handleSubmit}>
            <input
              type="text"
              value={draft}
              onChange={event => setDraft(event.target.value)}
              placeholder="Ask for useless advice..."
              aria-label="Message assistant bot"
            />
            <button type="submit">Send</button>
          </form>
        </section>
      )}
    </>
  );
}
