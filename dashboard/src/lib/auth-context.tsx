"use client"

import React, { createContext, useContext, useState, useEffect, useCallback } from "react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface User {
    id: string
    email: string
    name: string | null
    role: string
    is_active: boolean
    created_at: string
}

interface AuthContextType {
    user: User | null
    token: string | null
    isLoading: boolean
    isAuthenticated: boolean
    login: (email: string, password: string) => Promise<void>
    register: (email: string, password: string, name?: string) => Promise<void>
    logout: () => void
    apiRequest: <T>(method: string, path: string, body?: unknown) => Promise<T>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [token, setToken] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    const apiRequest = useCallback(async <T,>(method: string, path: string, body?: unknown): Promise<T> => {
        const headers: Record<string, string> = { "Content-Type": "application/json" }
        const currentToken = token || (typeof window !== "undefined" ? localStorage.getItem("piee_token") : null)
        if (currentToken) headers["Authorization"] = `Bearer ${currentToken}`

        const res = await fetch(`${API_URL}${path}`, {
            method,
            headers,
            body: body ? JSON.stringify(body) : undefined,
        })

        if (!res.ok) {
            const error = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }))
            throw new Error(error.detail || `Request failed: ${res.status}`)
        }

        if (res.status === 204) return undefined as T
        return res.json()
    }, [token])

    // Restore session on mount
    useEffect(() => {
        const savedToken = localStorage.getItem("piee_token")
        if (savedToken) {
            setToken(savedToken)
            fetch(`${API_URL}/auth/me`, {
                headers: { Authorization: `Bearer ${savedToken}` },
            })
                .then((r) => {
                    if (r.ok) return r.json()
                    throw new Error("Invalid token")
                })
                .then((data) => {
                    setUser(data)
                    setIsLoading(false)
                })
                .catch(() => {
                    localStorage.removeItem("piee_token")
                    setToken(null)
                    setIsLoading(false)
                })
        } else {
            setIsLoading(false)
        }
    }, [])

    const login = async (email: string, password: string) => {
        const result = await apiRequest<{ access_token: string; expires_in: number }>(
            "POST", "/auth/login", { email, password }
        )
        setToken(result.access_token)
        localStorage.setItem("piee_token", result.access_token)

        const me = await fetch(`${API_URL}/auth/me`, {
            headers: { Authorization: `Bearer ${result.access_token}` },
        }).then((r) => r.json())
        setUser(me)
    }

    const register = async (email: string, password: string, name?: string) => {
        await apiRequest("POST", "/auth/register", { email, password, name })
        await login(email, password)
    }

    const logout = () => {
        setToken(null)
        setUser(null)
        localStorage.removeItem("piee_token")
    }

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                isLoading,
                isAuthenticated: !!user,
                login,
                register,
                logout,
                apiRequest,
            }}
        >
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error("useAuth must be used within AuthProvider")
    return ctx
}
