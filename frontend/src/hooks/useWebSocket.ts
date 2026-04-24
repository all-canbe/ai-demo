import { useCallback, useEffect, useRef, useState } from 'react'
import { useAppDispatch, useAppSelector } from '@/app/hooks'
import { addMessage, updateStreamingMessage, setIsStreaming } from '@/features/chat/chatSlice'

interface WebSocketMessage {
  type: 'chat_start' | 'chat_chunk' | 'chat_end' | 'error' | 'ping' | 'pong'
  data?: any
}

const useWebSocket = () => {
  const dispatch = useAppDispatch()
  const { accessToken } = useAppSelector((state) => state.auth)
  const wsRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 10
  const baseReconnectDelay = 1000

  const getWebSocketUrl = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    return `${protocol}//${host}/ws/chat?token=${accessToken}`
  }

  const handleOpen = useCallback(() => {
    console.log('WebSocket connected')
    setIsConnected(true)
    setIsConnecting(false)
    reconnectAttemptsRef.current = 0
  }, [])

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data)
        
        switch (message.type) {
          case 'chat_start':
            dispatch(setIsStreaming(true))
            break
          case 'chat_chunk':
            if (message.data?.messageId && message.data?.content) {
              dispatch(updateStreamingMessage({
                id: message.data.messageId,
                content: message.data.content,
              }))
            }
            break
          case 'chat_end':
            dispatch(setIsStreaming(false))
            if (message.data?.message) {
              dispatch(addMessage(message.data.message))
            }
            break
          case 'error':
            console.error('WebSocket error:', message.data)
            dispatch(setIsStreaming(false))
            break
          case 'pong':
            break
          default:
            console.log('Unknown WebSocket message type:', message.type)
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    },
    [dispatch]
  )

  const handleClose = useCallback(() => {
    console.log('WebSocket disconnected')
    setIsConnected(false)
    if (accessToken && reconnectAttemptsRef.current < maxReconnectAttempts) {
      const delay = baseReconnectDelay * Math.pow(2, reconnectAttemptsRef.current)
      reconnectAttemptsRef.current++
      console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`)
      setTimeout(connect, delay)
    }
  }, [accessToken, connect])

  const handleError = useCallback((error: Event) => {
    console.error('WebSocket error:', error)
    setIsConnecting(false)
  }, [])

  const connect = useCallback(() => {
    if (!accessToken) {
      console.warn('No access token available, cannot connect WebSocket')
      return
    }

    if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
      console.log('WebSocket already connected or connecting')
      return
    }

    setIsConnecting(true)
    try {
      const wsUrl = getWebSocketUrl()
      wsRef.current = new WebSocket(wsUrl)

      wsRef.current.onopen = handleOpen
      wsRef.current.onmessage = handleMessage
      wsRef.current.onclose = handleClose
      wsRef.current.onerror = handleError
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setIsConnecting(false)
    }
  }, [accessToken, handleOpen, handleMessage, handleClose, handleError])

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
      setIsConnected(false)
    }
  }, [])

  const sendMessage = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket not connected, cannot send message')
    }
  }, [])

  const sendPing = useCallback(() => {
    sendMessage({ type: 'ping' })
  }, [sendMessage])

  useEffect(() => {
    if (accessToken) {
      connect()
    } else {
      disconnect()
    }

    return () => {
      disconnect()
    }
  }, [accessToken, connect, disconnect])

  useEffect(() => {
    let pingInterval: NodeJS.Timeout
    if (isConnected) {
      pingInterval = setInterval(sendPing, 30000)
    }

    return () => {
      if (pingInterval) {
        clearInterval(pingInterval)
      }
    }
  }, [isConnected, sendPing])

  return {
    connect,
    disconnect,
    sendMessage,
    isConnected,
    isConnecting,
  }
}

export default useWebSocket
