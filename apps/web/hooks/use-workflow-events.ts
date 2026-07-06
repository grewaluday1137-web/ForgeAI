"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import { getWorkflowEvents } from "@/services/workflows"

export interface LiveEvent {
  event: string
  data: Record<string, unknown>
  receivedAt: string
}

const WS_URL = typeof window !== "undefined"
  ? `ws://${window.location.hostname}:8000/api/v1/ws`
  : "ws://localhost:8000/api/v1/ws"

export function useWorkflowEvents(workflowId: string | null) {
  const [events, setEvents] = useState<LiveEvent[]>([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const connect = useCallback(() => {
    if (!workflowId) return
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
    }

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data) as { event: string; data: Record<string, unknown> }
        // Filter to only events relevant to this workflow
        const data = msg.data || {}
        const msgWorkflowId = data.workflow_id as string | undefined
        if (!msgWorkflowId || msgWorkflowId === workflowId) {
          setEvents((prev) => [
            ...prev,
            { event: msg.event, data: msg.data, receivedAt: new Date().toISOString() },
          ])
        }
      } catch {
        // ignore malformed messages
      }
    }

    ws.onclose = () => {
      setConnected(false)
      // Auto-reconnect after 3s
      reconnectTimer.current = setTimeout(connect, 3000)
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [workflowId])

  useEffect(() => {
    let mounted = true

    // Fetch historical events first
    if (workflowId) {
      getWorkflowEvents(workflowId).then((res) => {
        if (!mounted) return
        const historical = res.events.map((evt) => ({
          event: `agent.${evt.agent_type.toLowerCase()}.${evt.level.toLowerCase()}`,
          data: {
            message: evt.message,
            ...evt.metadata,
          },
          receivedAt: evt.created_at,
        }))
        setEvents(historical)
        
        // Connect websocket after fetching history to avoid gaps
        connect()
      }).catch(console.error)
    }

    return () => {
      mounted = false
      if (wsRef.current) wsRef.current.close()
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
    }
  }, [workflowId, connect])

  const clearEvents = useCallback(() => setEvents([]), [])

  return { events, connected, clearEvents }
}
