export class OrderTrackingWebSocket {
  private ws: WebSocket | null = null
  private orderId: string
  private userId: string
  private messageHandlers: Map<string, Function[]> = new Map()
  private reconnectInterval = 3000
  private shouldReconnect = true

  constructor(orderId: string, userId: string) {
    this.orderId = orderId
    this.userId = userId
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `ws://localhost:8000/ws/order/${this.orderId}?user_id=${this.userId}`
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log("[v0] Order tracking WebSocket connected")
          this.shouldReconnect = true
          resolve()
        }

        this.ws.onmessage = (event) => {
          const message = JSON.parse(event.data)
          this.handleMessage(message)
        }

        this.ws.onerror = (error) => {
          console.error("[v0] WebSocket error:", error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log("[v0] WebSocket disconnected")
          if (this.shouldReconnect) {
            setTimeout(() => this.reconnect(), this.reconnectInterval)
          }
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private reconnect() {
    if (this.shouldReconnect) {
      this.connect().catch(() => {
        setTimeout(() => this.reconnect(), this.reconnectInterval)
      })
    }
  }

  on(messageType: string, handler: Function) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, [])
    }
    this.messageHandlers.get(messageType)!.push(handler)
  }

  private handleMessage(message: any) {
    const handlers = this.messageHandlers.get(message.type) || []
    handlers.forEach((handler) => handler(message))
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  getOrderStatus() {
    this.send({ type: "get_order_status" })
  }

  ping() {
    this.send({ type: "ping" })
  }

  disconnect() {
    this.shouldReconnect = false
    if (this.ws) {
      this.ws.close()
    }
  }
}

export class DeliveryTrackingWebSocket {
  private ws: WebSocket | null = null
  private deliveryAgentId: string
  private messageHandlers: Map<string, Function[]> = new Map()
  private reconnectInterval = 3000
  private shouldReconnect = true

  constructor(deliveryAgentId: string) {
    this.deliveryAgentId = deliveryAgentId
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `ws://localhost:8000/ws/delivery-tracking/${this.deliveryAgentId}`
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log("[v0] Delivery tracking WebSocket connected")
          resolve()
        }

        this.ws.onmessage = (event) => {
          const message = JSON.parse(event.data)
          this.handleMessage(message)
        }

        this.ws.onerror = (error) => {
          console.error("[v0] WebSocket error:", error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log("[v0] Delivery WebSocket disconnected")
          if (this.shouldReconnect) {
            setTimeout(() => this.reconnect(), this.reconnectInterval)
          }
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private reconnect() {
    if (this.shouldReconnect) {
      this.connect().catch(() => {
        setTimeout(() => this.reconnect(), this.reconnectInterval)
      })
    }
  }

  on(messageType: string, handler: Function) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, [])
    }
    this.messageHandlers.get(messageType)!.push(handler)
  }

  private handleMessage(message: any) {
    const handlers = this.messageHandlers.get(message.type) || []
    handlers.forEach((handler) => handler(message))
  }

  sendLocationUpdate(latitude: number, longitude: number, orderId: string) {
    this.send({
      type: "location_update",
      latitude,
      longitude,
      order_id: orderId,
    })
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  disconnect() {
    this.shouldReconnect = false
    if (this.ws) {
      this.ws.close()
    }
  }
}
