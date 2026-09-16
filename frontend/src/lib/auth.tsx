"use client";

import { createContext, useContext, useEffect, useState } from "react";
import {
  fetchMe,
  login as apiLogin,
  loginWithGoogle as apiLoginWithGoogle,
  logout as apiLogout,
  register as apiRegister,
} from "@/lib/api";
import type { AuthUser } from "@/types/api";

const TOKEN_KEY = "roadfare_token";

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  loginWithGoogle: (idToken: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = window.localStorage.getItem(TOKEN_KEY);
    if (!storedToken) {
      // localStorage is a browser-only read with no server-side equivalent to derive
      // this from during render.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setIsLoading(false);
      return;
    }
    fetchMe(storedToken)
      .then((fetchedUser) => {
        setUser(fetchedUser);
        setToken(storedToken);
      })
      .catch(() => window.localStorage.removeItem(TOKEN_KEY))
      .finally(() => setIsLoading(false));
  }, []);

  async function login(username: string, password: string) {
    const { token: newToken, user: loggedInUser } = await apiLogin(username, password);
    window.localStorage.setItem(TOKEN_KEY, newToken);
    setToken(newToken);
    setUser(loggedInUser);
  }

  async function loginWithGoogle(idToken: string) {
    const { token: newToken, user: loggedInUser } = await apiLoginWithGoogle(idToken);
    window.localStorage.setItem(TOKEN_KEY, newToken);
    setToken(newToken);
    setUser(loggedInUser);
  }

  async function register(username: string, email: string, password: string) {
    const { token: newToken, user: newUser } = await apiRegister(username, email, password);
    window.localStorage.setItem(TOKEN_KEY, newToken);
    setToken(newToken);
    setUser(newUser);
  }

  async function logout() {
    const currentToken = window.localStorage.getItem(TOKEN_KEY);
    window.localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    if (currentToken) await apiLogout(currentToken).catch(() => {});
  }

  return (
    <AuthContext.Provider
      value={{ user, token, isLoading, login, loginWithGoogle, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
