import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl

  // Only protect API routes — frontend routes handled client-side
  if (pathname.startsWith("/api")) {
    const authHeader = req.headers.get("authorization")
    if (!authHeader) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 })
    }
  }

  // Frontend routes: allow rendering, client handles auth redirect
  return NextResponse.next()
}
