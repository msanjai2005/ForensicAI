import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Search, Filter } from 'lucide-react'
import Card from '../components/Card'
import Badge from '../components/Badge'
import Loader from '../components/Loader'
import { getTimeline } from '../api/cases'

const TimelinePage = () => {
  const { id } = useParams()
  const [allEvents, setAllEvents] = useState([])
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    source: '',
    search: '',
    dateFrom: '',
    dateTo: ''
  })

  useEffect(() => {
    loadTimeline()
  }, [id])

  useEffect(() => {
    applyFilters()
  }, [filters, allEvents])

  const loadTimeline = async () => {
    try {
      const data = await getTimeline(id)
      setAllEvents(data.events || [])
      setEvents(data.events || [])
    } catch (error) {
      console.error('Failed to load timeline:', error)
      setAllEvents([])
      setEvents([])
    } finally {
      setLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = [...allEvents]

    // Filter by source
    if (filters.source) {
      filtered = filtered.filter(e => e.source === filters.source)
    }

    // Filter by date range
    if (filters.dateFrom) {
      const fromDate = new Date(filters.dateFrom)
      filtered = filtered.filter(e => new Date(e.timestamp) >= fromDate)
    }
    if (filters.dateTo) {
      const toDate = new Date(filters.dateTo)
      toDate.setHours(23, 59, 59)
      filtered = filtered.filter(e => new Date(e.timestamp) <= toDate)
    }

    // Filter by search - search across all fields including metadata
    if (filters.search) {
      const search = filters.search.toLowerCase()
      filtered = filtered.filter(e => {
        // Search in basic fields
        const basicMatch = 
          e.user_id?.toLowerCase().includes(search) ||
          e.event_type?.toLowerCase().includes(search) ||
          e.source?.toLowerCase().includes(search) ||
          e.receiver?.toLowerCase().includes(search) ||
          e.amount?.toString().includes(search) ||
          e.timestamp?.toLowerCase().includes(search) ||
          e.message_text?.toLowerCase().includes(search) ||
          e.language?.toLowerCase().includes(search)
        
        // Search in metadata JSON
        const metadataMatch = e.metadata && e.metadata !== '{}' && 
          e.metadata.toLowerCase().includes(search)
        
        return basicMatch || metadataMatch
      })
    }

    setEvents(filtered)
  }

  const getEventColor = (type) => {
    const colors = {
      message: 'info',
      transaction: 'success',
      call: 'purple',
      suspicious: 'danger'
    }
    return colors[type] || 'default'
  }

  if (loading) return <Loader size="lg" />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Timeline</h1>

      <Card>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Source</label>
            <select
              value={filters.source}
              onChange={(e) => setFilters({ ...filters, source: e.target.value })}
              className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            >
              <option value="">All Sources</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="calls">Calls</option>
              <option value="whatsapp_call">WhatsApp Call</option>
              <option value="transactions">Transactions</option>
              <option value="locations">Locations</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Date From</label>
            <input
              type="date"
              value={filters.dateFrom}
              onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
              className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Date To</label>
            <input
              type="date"
              value={filters.dateTo}
              onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
              className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                placeholder="Search events..."
                className="w-full bg-dark-bg border border-dark-border rounded-lg pl-10 pr-4 py-2 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>
        <button onClick={applyFilters} className="btn-primary mt-4 flex items-center gap-2">
          <Filter className="w-4 h-4" />
          Apply Filters ({events.length} results)
        </button>
      </Card>

      <div className="space-y-4">
        {events.length === 0 ? (
          <Card>
            <p className="text-center text-gray-400 py-8">No events found</p>
          </Card>
        ) : (
          events.map((event, idx) => {
            // Parse metadata if it's a string
            let metadata = event.metadata
            if (typeof metadata === 'string') {
              try {
                metadata = JSON.parse(metadata)
              } catch (e) {
                metadata = {}
              }
            }
            
            return (
              <Card key={idx} className={event.event_type === 'suspicious' ? 'border-red-500' : ''}>
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-3">
                    <Badge variant={getEventColor(event.event_type)}>{event.event_type}</Badge>
                    <span className="text-sm text-gray-400">{new Date(event.timestamp).toLocaleString()}</span>
                  </div>
                  <span className="text-sm font-medium">{event.actor_id || event.user_id}</span>
                </div>
                <div className="space-y-1">
                  <p className="text-gray-300">User: {event.actor_id || event.user_id || 'Unknown'}</p>
                  <p className="text-gray-300">Source: {event.source_type || event.source || 'Unknown'}</p>
                  {event.amount && <p className="text-gray-300">Amount: ${event.amount}</p>}
                  {event.target_id && event.target_id !== 'None' && event.target_id !== 'nan' && (
                    <p className="text-gray-300">Receiver: {event.target_id}</p>
                  )}
                  {event.message_text && <p className="text-gray-300">Message: {event.message_text}</p>}
                </div>
                {metadata && Object.keys(metadata).length > 0 && (
                  <div className="mt-3 p-3 bg-dark-bg rounded-lg">
                    <div className="text-xs text-gray-400 space-y-1">
                      {Object.entries(metadata).map(([key, value]) => (
                        <div key={key}>
                          <span className="text-gray-500">{key}:</span> {JSON.stringify(value)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            )
          })
        )}
      </div>
    </div>
  )
}

export default TimelinePage
