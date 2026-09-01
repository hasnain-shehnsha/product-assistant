import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import App from './App'

// Mock WebSocket API globally
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = 1; // OPEN
    global.mockWsInstance = this;
  }
  send(data) {
    if (this.onmessage) {
      this.onmessage({ data: JSON.stringify({ chunk: "This is a mocked bot response from the backend." }) });
      this.onmessage({ data: JSON.stringify({ done: true }) });
    }
  }
  close() {}
}
global.WebSocket = MockWebSocket;
global.HTMLElement.prototype.scrollIntoView = vi.fn();

describe('App', () => {
  beforeEach(() => {
    global.mockWsInstance = null;
  })

  it('renders the header correctly', () => {
    render(<App />)
    expect(screen.getByText('Product Assistant')).toBeInTheDocument()
  })

  it('renders the sidebar with new chat button and history', () => {
    render(<App />)
    expect(screen.getByRole('button', { name: /\+ New Chat/i })).toBeInTheDocument()
    expect(screen.getByText('Current Conversation')).toBeInTheDocument()
  })

  it('renders the initial bot message', () => {
    render(<App />)
    expect(screen.getByText(/Hello! I am your premium product assistant/i)).toBeInTheDocument()
  })

  it('renders the input field and send button', () => {
    render(<App />)
    expect(screen.getByPlaceholderText(/Ask about our products/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Send/i })).toBeInTheDocument()
  })

  it('can type and send a message', async () => {
    render(<App />)
    
    const input = screen.getByPlaceholderText(/Ask about our products/i)
    const sendBtn = screen.getByRole('button', { name: /Send/i })

    fireEvent.change(input, { target: { value: 'Show me some laptops' } })
    fireEvent.click(sendBtn)

    // User message should appear immediately
    expect(screen.getByText('Show me some laptops')).toBeInTheDocument()

    // Wait for bot response to appear (mocked WebSocket sends it immediately on 'send')
    await waitFor(() => {
      expect(screen.getByText('This is a mocked bot response from the backend.')).toBeInTheDocument()
    })
  })
})
