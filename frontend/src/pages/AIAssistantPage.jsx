import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { Brain, Send, Loader2 } from 'lucide-react'
import Card from '../components/Card'
import axios from 'axios'

const AIAssistantPage = () => {
  const { id } = useParams()
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!question.trim() || loading) return

    const userMessage = { role: 'user', content: question }
    setMessages(prev => [...prev, userMessage])
    setQuestion('')
    setLoading(true)

    try {
      const response = await axios.post(`http://localhost:8000/api/cases/${id}/ai-assistant`, {
        question: question
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        success: response.data.success
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: 'Failed to get response from AI assistant. Please try again.',
        success: false
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const suggestedQuestions = [
    "What are the main security concerns in this case?",
    "What is the overall risk level and why?",
    "Summarize all findings in this investigation",
    "What suspicious patterns were detected?",
    "Which users or entities are high-risk?",
    "What actions should investigators take immediately?",
    "Explain the anomalies found in the data",
    "Are there any midnight activity violations?",
    "What high-value transactions were flagged?",
    "Show me the network connections analysis"
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Brain className="w-8 h-8 text-purple-500" />
        <div>
          <h1 className="text-2xl font-bold">AI Forensic Assistant</h1>
          <p className="text-sm text-gray-400">Ask questions about this case investigation</p>
        </div>
      </div>

      {/* Chat Messages */}
      <Card className="min-h-[500px] flex flex-col">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <Brain className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">AI Forensic Intelligence</h3>
              <p className="text-gray-400 mb-6">Ask me anything about this case investigation</p>
              
              <div className="text-left max-w-2xl mx-auto">
                <p className="text-sm text-gray-500 mb-3">Suggested questions:</p>
                <div className="space-y-2">
                  {suggestedQuestions.map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => setQuestion(q)}
                      className="block w-full text-left px-4 py-2 bg-dark-bg rounded-lg hover:bg-dark-hover transition-colors text-sm text-gray-300"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-3 ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-dark-bg text-gray-300 border border-dark-border'
                  }`}
                >
                  {msg.role === 'assistant' && (
                    <div className="flex items-center gap-2 mb-2">
                      <Brain className="w-4 h-4 text-purple-400" />
                      <span className="text-xs text-gray-500">AI Assistant</span>
                    </div>
                  )}
                  <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
                </div>
              </div>
            ))
          )}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-dark-bg rounded-lg px-4 py-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                  <span className="text-sm text-gray-400">Analyzing case data...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="border-t border-dark-border pt-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask about this case..."
              disabled={loading}
              className="flex-1 bg-dark-bg border border-dark-border rounded-lg px-4 py-3 focus:outline-none focus:border-purple-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!question.trim() || loading}
              className="btn-primary px-6 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Powered by Hugging Face (Free) • Responses are based on case analysis data
          </p>
        </form>
      </Card>

      {/* Info Card */}
      <Card>
        <h3 className="font-semibold mb-3">About AI Assistant</h3>
        <div className="text-sm text-gray-400 space-y-2">
          <p>• Interprets forensic analysis results and provides insights</p>
          <p>• Answers questions about risk scores, anomalies, and patterns</p>
          <p>• Summarizes case intelligence in plain language</p>
          <p>• Uses only the data from your case analysis (no external data)</p>
          <p>• Responses are AI-generated and should be verified by investigators</p>
        </div>
      </Card>
    </div>
  )
}

export default AIAssistantPage
