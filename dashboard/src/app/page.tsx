"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { useAuth } from "@/lib/auth-context";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Slider } from "@/components/ui/slider";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  LayoutDashboard,
  Bot,
  Key,
  BarChart3,
  Settings,
  LogOut,
  Plus,
  Copy,
  Trash2,
  Check,
  AlertCircle,
  Zap,
  Shield,
  Globe,
  Server,
  Activity,
  Wallet,
  Hash,
  Loader2,
  User as UserIcon,
  ChevronDown,
  Terminal,
  Sparkles,
  Beaker,
  Send,
  MessageSquare,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/* ━━━ Auth Screen ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

function AuthScreen() {
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (isLogin) await login(email, password);
      else await register(email, password, name || undefined);
    } catch (err: any) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4 bg-muted/30">
      {/* Theme toggle top-right */}
      <div className="fixed top-4 right-4">
        <ThemeToggle />
      </div>

      <div className="w-full max-w-sm space-y-6">
        {/* Logo + Branding */}
        <div className="flex flex-col items-center gap-3">
          <Image src="/logo.png" alt="PIEE" width={64} height={64} className="rounded-2xl" />
          <div className="text-center">
            <h1 className="text-2xl font-bold tracking-tight">PIEE</h1>
            <p className="text-sm text-muted-foreground">Hybrid AI Infrastructure</p>
          </div>
        </div>

        <Card>
          <CardHeader className="pb-4">
            <CardTitle className="text-lg">{isLogin ? "Welcome back" : "Create account"}</CardTitle>
            <CardDescription>
              {isLogin ? "Sign in to access your dashboard" : "Get started with PIEE"}
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              {!isLogin && (
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    placeholder="Your name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Min 8 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                />
              </div>
              {error && (
                <div className="flex items-center gap-2 text-sm text-destructive bg-destructive/10 rounded-md p-3">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  {error}
                </div>
              )}
            </CardContent>

            <CardFooter className="flex flex-col gap-3">
              <Button type="submit" className="w-full" disabled={loading}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {isLogin ? "Sign In" : "Create Account"}
              </Button>
              <p className="text-sm text-muted-foreground">
                {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
                <button
                  type="button"
                  className="font-medium underline underline-offset-4 hover:text-foreground transition-colors"
                  onClick={() => {
                    setIsLogin(!isLogin);
                    setError("");
                  }}
                >
                  {isLogin ? "Sign up" : "Sign in"}
                </button>
              </p>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}

/* ━━━ Root ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

export default function DashboardPage() {
  const { user, isLoading, isAuthenticated, logout } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!isAuthenticated) return <AuthScreen />;

  return (
    <TooltipProvider delayDuration={0}>
      <DashboardShell user={user!} onLogout={logout} />
    </TooltipProvider>
  );
}

/* ━━━ Shell ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

interface ShellProps {
  user: { id: string; email: string; name: string | null; role: string };
  onLogout: () => void;
}

function DashboardShell({ user, onLogout }: ShellProps) {
  const [page, setPage] = useState("overview");

  const nav = [
    { id: "overview", icon: LayoutDashboard, label: "Overview" },
    { id: "sandbox", icon: Beaker, label: "Sandbox" },
    { id: "models", icon: Bot, label: "Models" },
    { id: "keys", icon: Key, label: "API Keys" },
    { id: "usage", icon: BarChart3, label: "Usage" },
    { id: "settings", icon: Settings, label: "Settings" },
  ];

  return (
    <div className="flex min-h-screen">
      {/* ── Sidebar ── */}
      <aside className="hidden md:flex w-60 flex-col border-r bg-card/50 fixed inset-y-0 left-0 z-40">
        {/* Brand */}
        <div className="flex items-center gap-2.5 px-5 py-5">
          <Image src="/logo.png" alt="PIEE" width={32} height={32} className="rounded-lg" />
          <div>
            <p className="text-sm font-semibold leading-none">PIEE</p>
            <p className="text-[10px] text-muted-foreground leading-none mt-0.5">
              AI Infrastructure
            </p>
          </div>
        </div>

        <Separator />

        {/* Nav */}
        <ScrollArea className="flex-1 py-3 px-3">
          <nav className="space-y-0.5">
            {nav.map((item) => (
              <button
                key={item.id}
                onClick={() => setPage(item.id)}
                className={`flex items-center gap-2.5 w-full px-3 py-2 rounded-md text-sm transition-colors ${page === item.id
                  ? "bg-primary text-primary-foreground font-medium"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
                  }`}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </button>
            ))}
          </nav>
        </ScrollArea>

        {/* Bottom section */}
        <div className="p-3 space-y-2 border-t">
          <div className="flex items-center justify-between px-2">
            <span className="text-xs text-muted-foreground">Theme</span>
            <ThemeToggle />
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2.5 w-full px-2.5 py-2 rounded-md hover:bg-accent transition-colors text-left">
                <Avatar className="h-7 w-7">
                  <AvatarFallback className="text-xs font-medium bg-muted">
                    {(user.name || user.email)[0].toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate leading-none">
                    {user.name || user.email.split("@")[0]}
                  </p>
                  <p className="text-[11px] text-muted-foreground truncate leading-none mt-0.5">
                    {user.email}
                  </p>
                </div>
                <ChevronDown className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" side="top" className="w-52">
              <DropdownMenuLabel className="font-normal">
                <p className="text-sm font-medium">{user.name || user.email.split("@")[0]}</p>
                <p className="text-xs text-muted-foreground">{user.role}</p>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="flex-1 md:ml-60">
        {/* Top bar for mobile */}
        <div className="sticky top-0 z-30 md:hidden flex items-center gap-3 border-b bg-background/95 backdrop-blur px-4 py-3">
          <Image src="/logo.png" alt="PIEE" width={28} height={28} className="rounded-lg" />
          <span className="text-sm font-semibold flex-1">PIEE</span>
          <ThemeToggle />
        </div>

        <div className="p-6 md:p-8 max-w-6xl mx-auto">
          {page === "overview" && <OverviewPage />}
          {page === "sandbox" && <SandboxPage />}
          {page === "models" && <ModelsPage />}
          {page === "keys" && <ApiKeysPage />}
          {page === "usage" && <UsagePage />}
          {page === "settings" && <SettingsPage user={user} />}
        </div>
      </main>
    </div>
  );
}

/* ━━━ Overview ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

function OverviewPage() {
  const [health, setHealth] = useState<any>(null);
  const [modelCount, setModelCount] = useState(0);
  const [balance, setBalance] = useState<any>(null);
  const { apiRequest } = useAuth();

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => { });
    fetch(`${API_URL}/v1/models`)
      .then((r) => r.json())
      .then((d) => setModelCount(d.data?.length || 0))
      .catch(() => { });
    apiRequest("GET", "/billing/balance")
      .then(setBalance)
      .catch(() => { });
  }, [apiRequest]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Overview</h1>
        <p className="text-sm text-muted-foreground mt-1">
          {health
            ? `Running in ${health.mode} mode • v${health.version}`
            : "Connecting to backend…"}
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={Activity}
          label="Status"
          value={health ? "Online" : "Offline"}
          sub={health ? `${health.mode} deployment` : "Cannot reach backend"}
        >
          {health && (
            <span className="inline-block h-2 w-2 rounded-full bg-green-500 status-pulse mr-1.5" />
          )}
          {!health && <span className="inline-block h-2 w-2 rounded-full bg-destructive mr-1.5" />}
        </StatCard>
        <StatCard icon={Bot} label="Models" value={String(modelCount)} sub="In registry" />
        <StatCard
          icon={Wallet}
          label="Balance"
          value={balance?.unlimited ? "Unlimited" : `$${balance?.balance?.toFixed(2) || "0.00"}`}
          sub={balance?.unlimited ? "Local mode" : "USD"}
        />
        <StatCard
          icon={Globe}
          label="Mode"
          value={health?.mode ? health.mode.charAt(0).toUpperCase() + health.mode.slice(1) : "—"}
          sub="Deployment"
        />
      </div>

      {/* Quick Start */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-base">Quick Start</CardTitle>
          </div>
          <CardDescription>Get started with the PIEE SDK in seconds</CardDescription>
        </CardHeader>
        <CardContent>
          <pre className="rounded-lg border bg-muted/50 p-4 text-[13px] leading-relaxed text-muted-foreground overflow-auto">
            {`import PIEE from "@piee/sdk";

const piee = new PIEE({
  baseURL: "${API_URL}",
  apiKey: "pk-your-api-key",
});

const response = await piee.chat.completions.create({
  model: "openai/gpt-4o",
  messages: [{ role: "user", content: "Hello, PIEE!" }],
});

console.log(response.choices[0].message.content);`}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  children,
}: {
  icon: any;
  label: string;
  value: string;
  sub: string;
  children?: React.ReactNode;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-semibold flex items-center">
          {children}
          {value}
        </div>
        <p className="text-xs text-muted-foreground mt-1">{sub}</p>
      </CardContent>
    </Card>
  );
}

/* ━━━ Models ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

function OllamaControls({ onSync }: { onSync: () => void }) {
  const { apiRequest } = useAuth();
  const [status, setStatus] = useState<any>(null);
  const [localModels, setLocalModels] = useState<any[]>([]);
  const [pullName, setPullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [pulling, setPulling] = useState(false);

  const checkStatus = async () => {
    try {
      const res: any = await apiRequest("GET", "/v1/ollama/status");
      setStatus(res);
      if (res.status === "online") loadLocalModels();
    } catch {
      setStatus({ status: "offline", message: "Failed to connect to PIEE backend" });
    }
  };

  const loadLocalModels = async () => {
    setLoading(true);
    try {
      const res: any = await apiRequest("GET", "/v1/ollama/models");
      if (res.status === "success") {
        setLocalModels(res.models);
      }
    } catch { }
    setLoading(false);
  };

  const [pullProgress, setPullProgress] = useState<string>("");

  const pullModel = async () => {
    if (!pullName) return;
    setPulling(true);
    setPullProgress("Starting pull...");
    try {
      const currentToken = typeof window !== "undefined" ? localStorage.getItem("piee_token") : null;
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (currentToken) headers["Authorization"] = `Bearer ${currentToken}`;

      const res = await fetch(`${API_URL}/v1/ollama/pull`, {
        method: "POST",
        headers,
        body: JSON.stringify({ name: pullName })
      });

      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter(Boolean);
        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            let progStr = data.status || "";
            if (data.total && data.completed) {
              const pct = Math.round((data.completed / data.total) * 100);
              progStr += ` (${pct}%)`;
            }
            if (data.error) {
              progStr = `Error: ${data.error}`;
            }
            setPullProgress(progStr);
          } catch {
            // pass
          }
        }
      }

      setPullProgress("Pull complete!");
      setTimeout(() => setPullProgress(""), 3000);
      loadLocalModels();
      setPullName("");
    } catch (e: any) {
      alert("Pull failed: " + e.message);
      setPullProgress("");
    }
    setPulling(false);
  };

  const syncModel = async (name: string) => {
    try {
      await apiRequest("POST", "/v1/ollama/sync", { name });
      onSync();
    } catch (e: any) {
      alert("Sync failed: " + e.message);
    }
  };

  useEffect(() => {
    checkStatus();
  }, []);

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Server className="h-5 w-5" />
          Ollama Provider
        </CardTitle>
        <CardDescription>
          Manage your local Ollama daemon directly
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm">
            Status:
            {status?.status === "online" ? (
              <Badge variant="secondary" className="bg-green-500/10 text-green-500 hover:bg-green-500/20">Online</Badge>
            ) : (
              <Badge variant="destructive">Offline</Badge>
            )}
            <span className="text-xs text-muted-foreground">{status?.message || "Checking..."}</span>
          </div>
          <Button variant="outline" size="sm" onClick={checkStatus}>
            Refresh
          </Button>
        </div>

        {status?.status === "online" && (
          <>
            <Separator />
            <div className="flex items-end gap-3">
              <div className="flex-1 space-y-2">
                <Label>Pull New Model</Label>
                <Input
                  placeholder="e.g. llama3, qwen2.5:0.5b..."
                  value={pullName}
                  onChange={e => setPullName(e.target.value)}
                  disabled={pulling}
                />
              </div>
              <Button onClick={pullModel} disabled={pulling || !pullName}>
                {pulling && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {pulling ? "Pulling..." : "Pull Model"}
              </Button>
            </div>
            {pullProgress && (
              <p className="text-xs text-muted-foreground animate-pulse">
                {Math.random() ? pullProgress : pullProgress /* Force text change re-render avoidance hack is not needed, string changes normally */}
              </p>
            )}

            <div className="space-y-2 mt-4">
              <Label>Installed Models</Label>
              <div className="border rounded-md overflow-hidden divide-y">
                {loading ? (
                  <div className="p-8 text-center text-sm text-muted-foreground">
                    <Loader2 className="h-5 w-5 animate-spin mx-auto mb-2" />
                    Loading local models...
                  </div>
                ) : localModels.length === 0 ? (
                  <div className="p-8 text-center text-sm text-muted-foreground">No local models found. Use the input above to pull one from the Ollama library.</div>
                ) : (
                  localModels.map((lm) => (
                    <div key={lm.name} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 bg-card gap-3">
                      <div className="flex items-center gap-3">
                        <Terminal className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="font-mono text-sm leading-none flex items-center gap-2">
                            {lm.name}
                            <Badge variant="outline" className="text-[10px] h-5 px-1.5">{Math.round(lm.size / 1024 / 1024 / 1024 * 10) / 10} GB</Badge>
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-2 shrink-0">
                        <div className="flex items-center gap-1.5 bg-muted/50 px-2.5 py-1 rounded-md text-xs font-mono text-muted-foreground border">
                          ollama run {lm.name}
                        </div>
                        <Button variant="secondary" size="sm" onClick={() => syncModel(lm.name)}>
                          Sync
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

function ModelsPage() {
  const [models, setModels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadModels = () => {
    fetch(`${API_URL}/v1/models`)
      .then((r) => r.json())
      .then((d) => {
        setModels(d.data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    loadModels();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Models</h1>
          <p className="text-sm text-muted-foreground mt-1">
            All registered models across providers
          </p>
        </div>
        <Badge variant="secondary">{models.length} models</Badge>
      </div>

      <OllamaControls onSync={loadModels} />

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Model ID</TableHead>
              <TableHead>Provider</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-12"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-12">
                  <Loader2 className="h-5 w-5 animate-spin mx-auto text-muted-foreground" />
                </TableCell>
              </TableRow>
            ) : models.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-12 text-muted-foreground">
                  No models registered. Start the backend to seed defaults.
                </TableCell>
              </TableRow>
            ) : (
              models.map((m) => (
                <TableRow key={m.id}>
                  <TableCell className="font-mono text-sm">{m.id}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{m.owned_by}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary" className="text-green-600 dark:text-green-400">
                      Active
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => {
                            navigator.clipboard.writeText(m.id);
                          }}
                        >
                          <Copy className="h-3.5 w-3.5" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Copy model ID</TooltipContent>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}

/* ━━━ API Keys ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

function ApiKeysPage() {
  const { apiRequest } = useAuth();
  const [keys, setKeys] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");
  const [creating, setCreating] = useState(false);
  const [newKey, setNewKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const loadKeys = async () => {
    try {
      const data: any = await apiRequest("GET", "/auth/api-keys");
      setKeys(data);
    } catch { }
    setLoading(false);
  };

  useEffect(() => {
    loadKeys();
  }, []);

  const createKey = async () => {
    if (!newKeyName.trim()) return;
    setCreating(true);
    try {
      const result: any = await apiRequest("POST", "/auth/api-keys", { name: newKeyName });
      setNewKey(result.key);
      setNewKeyName("");
      loadKeys();
    } catch (err: any) {
      alert(err.message);
    }
    setCreating(false);
  };

  const deleteKey = async (id: string) => {
    if (!confirm("Revoke this API key? This cannot be undone.")) return;
    try {
      await apiRequest("DELETE", `/auth/api-keys/${id}`);
      loadKeys();
    } catch { }
  };

  const copyKey = () => {
    if (newKey) navigator.clipboard.writeText(newKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">API Keys</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Create and manage authentication keys
          </p>
        </div>

        <Dialog
          open={showCreate}
          onOpenChange={(o) => {
            setShowCreate(o);
            if (!o) setNewKey(null);
          }}
        >
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="mr-1.5 h-4 w-4" />
              Create Key
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            {newKey ? (
              <>
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4" />
                    Key Created
                  </DialogTitle>
                  <DialogDescription>
                    Copy your key now — you won&apos;t see it again.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-3 py-2">
                  <div className="flex items-center gap-2">
                    <code className="flex-1 rounded-md border bg-muted/50 p-3 text-sm font-mono break-all select-all">
                      {newKey}
                    </code>
                    <Button variant="outline" size="icon" className="shrink-0" onClick={copyKey}>
                      {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </div>
                  <div className="flex items-start gap-2 text-sm text-muted-foreground bg-muted/50 rounded-md p-3 border">
                    <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                    <span>
                      Store this key in a secure location. It will not be displayed again after you
                      close this dialog.
                    </span>
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    className="w-full sm:w-auto"
                    onClick={() => {
                      setShowCreate(false);
                      setNewKey(null);
                    }}
                  >
                    Done
                  </Button>
                </DialogFooter>
              </>
            ) : (
              <>
                <DialogHeader>
                  <DialogTitle>Create API Key</DialogTitle>
                  <DialogDescription>
                    Generate a new key for PIEE API authentication.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-3 py-2">
                  <div className="space-y-2">
                    <Label htmlFor="keyName">Key Name</Label>
                    <Input
                      id="keyName"
                      placeholder="e.g. Production, Development, CI/CD"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && createKey()}
                    />
                    <p className="text-xs text-muted-foreground">
                      A descriptive name to help you identify this key
                    </p>
                  </div>
                </div>
                <DialogFooter className="gap-2 sm:gap-0">
                  <Button variant="outline" onClick={() => setShowCreate(false)}>
                    Cancel
                  </Button>
                  <Button onClick={createKey} disabled={creating || !newKeyName.trim()}>
                    {creating && <Loader2 className="mr-1.5 h-4 w-4 animate-spin" />}Create
                  </Button>
                </DialogFooter>
              </>
            )}
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Key</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Last Used</TableHead>
              <TableHead className="w-12"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-12">
                  <Loader2 className="h-5 w-5 animate-spin mx-auto text-muted-foreground" />
                </TableCell>
              </TableRow>
            ) : keys.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-16">
                  <Key className="h-8 w-8 mx-auto mb-3 text-muted-foreground/40" />
                  <p className="text-sm text-muted-foreground">No API keys yet</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Create your first key to start using the API
                  </p>
                </TableCell>
              </TableRow>
            ) : (
              keys.map((k) => (
                <TableRow key={k.id}>
                  <TableCell className="font-medium">{k.name}</TableCell>
                  <TableCell>
                    <code className="text-xs text-muted-foreground">{k.key_prefix}</code>
                  </TableCell>
                  <TableCell>
                    <Badge variant={k.is_active ? "secondary" : "destructive"}>
                      {k.is_active ? "Active" : "Revoked"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {new Date(k.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {k.last_used_at ? new Date(k.last_used_at).toLocaleDateString() : "Never"}
                  </TableCell>
                  <TableCell>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-muted-foreground hover:text-destructive"
                          onClick={() => deleteKey(k.id)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Revoke</TooltipContent>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Usage hint */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-base">Using Your Key</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <pre className="rounded-lg border bg-muted/50 p-4 text-[13px] leading-relaxed text-muted-foreground overflow-auto">
            {`// SDK
const piee = new PIEE({ apiKey: "pk-your-key" });

// Or fetch directly
fetch("${API_URL}/v1/chat/completions", {
  headers: { "X-API-Key": "pk-your-key" },
  ...
});`}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}

/* ━━━ Usage ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

function UsagePage() {
  const { apiRequest } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiRequest("GET", "/audit/usage?limit=50")
      .then(setStats)
      .catch(() => { })
      .finally(() => setLoading(false));
  }, [apiRequest]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Usage</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Monitor API requests, tokens, and costs
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          icon={Hash}
          label="Total Requests"
          value={stats?.total_requests?.toLocaleString() || "0"}
          sub="All time"
        />
        <StatCard
          icon={Zap}
          label="Total Tokens"
          value={stats?.total_tokens?.toLocaleString() || "0"}
          sub="Input + output"
        />
        <StatCard
          icon={Wallet}
          label="Total Cost"
          value={`$${stats?.total_cost?.toFixed(4) || "0.0000"}`}
          sub="Based on model pricing"
        />
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Recent Requests</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : stats?.breakdown?.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Tokens</TableHead>
                  <TableHead>Latency</TableHead>
                  <TableHead>Cost</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {stats.breakdown.slice(0, 20).map((r: any) => (
                  <TableRow key={r.id}>
                    <TableCell>
                      <Badge variant="outline">{r.request_type}</Badge>
                    </TableCell>
                    <TableCell>{r.total_tokens.toLocaleString()}</TableCell>
                    <TableCell>{r.latency_ms}ms</TableCell>
                    <TableCell>${r.cost.toFixed(6)}</TableCell>
                    <TableCell>
                      <Badge variant={r.status_code === 200 ? "secondary" : "destructive"}>
                        {r.status_code}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(r.created_at).toLocaleString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-16">
              <BarChart3 className="h-8 w-8 mx-auto mb-3 text-muted-foreground/40" />
              <p className="text-sm text-muted-foreground">No usage data yet</p>
              <p className="text-xs text-muted-foreground mt-1">
                Make API requests to see analytics here
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/* ━━━ Settings ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

function SettingsPage({
  user,
}: {
  user: { id: string; email: string; name: string | null; role: string };
}) {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => { });
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Account and deployment configuration</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <UserIcon className="h-4 w-4 text-muted-foreground" />
              <CardTitle className="text-base">Account</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <Row label="Email" value={user.email} mono />
            <Separator />
            <Row label="Role">
              <Badge variant="outline">{user.role}</Badge>
            </Row>
            <Separator />
            <Row label="User ID" value={user.id} mono muted />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Server className="h-4 w-4 text-muted-foreground" />
              <CardTitle className="text-base">Deployment</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <Row label="Mode">
              <Badge variant="secondary">{health?.mode?.toUpperCase() || "—"}</Badge>
            </Row>
            <Separator />
            <Row label="Version" value={health?.version || "—"} />
            <Separator />
            <Row label="API URL" value={API_URL} mono />
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-muted-foreground" />
              <CardTitle className="text-base">SDK Connection</CardTitle>
            </div>
            <CardDescription>Connect to this PIEE instance from your application</CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="rounded-lg border bg-muted/50 p-4 text-[13px] leading-relaxed text-muted-foreground overflow-auto">
              {`import PIEE from "@piee/sdk";

const piee = new PIEE({
  baseURL: "${API_URL}",
  apiKey: "pk-your-key",
});

// Works identically for local and cloud`}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Row({
  label,
  value,
  mono,
  muted,
  children,
}: {
  label: string;
  value?: string;
  mono?: boolean;
  muted?: boolean;
  children?: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-muted-foreground">{label}</span>
      {children || (
        <span
          className={`${mono ? "font-mono text-xs" : ""} ${muted ? "text-muted-foreground" : ""} truncate max-w-[60%] text-right`}
        >
          {value}
        </span>
      )}
    </div>
  );

}

/* ━━━ Sandbox ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

function SandboxPage() {
  const [apiKey, setApiKey] = useState("");
  const [models, setModels] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("You are a helpful AI assistant. Be clear, concise, and professional.");
  const [temperature, setTemperature] = useState([0.7]);
  const [maxTokens, setMaxTokens] = useState([2048]);
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(true);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    fetch(`${API_URL}/v1/models`)
      .then(r => r.json())
      .then(d => {
        setModels(d.data || []);
        if (d.data?.length > 0) setSelectedModel(d.data[0].id);
      })
      .catch(() => { });
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    if (!apiKey.trim()) { setError("Please provide an API key."); return; }
    if (!selectedModel) { setError("Please select a model."); return; }

    const apiMessages = [
      { role: "system", content: systemPrompt },
      ...messages,
      { role: "user", content: input },
    ];
    const displayMessages = [...messages, { role: "user", content: input }];
    setMessages(displayMessages);
    setInput("");
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/v1/chat/completions`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${apiKey}` },
        body: JSON.stringify({
          model: selectedModel,
          messages: apiMessages,
          stream: isStreaming,
          temperature: temperature[0],
          max_tokens: maxTokens[0],
        })
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error?.message || data.detail || "Request failed");
      }

      if (isStreaming) {
        if (!res.body) throw new Error("No response body");
        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let assistantContent = "";
        const withPlaceholder = [...displayMessages, { role: "assistant", content: "" }];
        setMessages(withPlaceholder);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          for (const line of decoder.decode(value, { stream: true }).split("\n").filter(Boolean)) {
            if (!line.startsWith("data: ")) continue;
            const dataStr = line.slice(6).trim();
            if (dataStr === "[DONE]") break;
            try {
              const chunk = JSON.parse(dataStr);
              if (chunk.error) throw new Error(chunk.error.message || "Stream error");
              const delta = chunk.choices?.[0]?.delta?.content;
              if (delta) {
                assistantContent += delta;
                setMessages([...displayMessages, { role: "assistant", content: assistantContent }]);
              }
            } catch { /* ignore parse errors on partial chunks */ }
          }
        }
      } else {
        const data = await res.json();
        if (data.choices?.[0]?.message) {
          setMessages([...displayMessages, data.choices[0].message]);
        } else {
          throw new Error("Invalid response format");
        }
      }
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setError("");
  };

  const visibleMessages = messages.filter(m => m.role !== "system");

  return (
    <div className="flex flex-col" style={{ height: "calc(100vh - 7rem)" }}>
      {/* ── Page Header ── */}
      <div className="flex items-center justify-between shrink-0 mb-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Sandbox</h1>
          <p className="text-sm text-muted-foreground mt-0.5">Test models interactively with full markdown rendering.</p>
        </div>
        <Button
          variant="ghost" size="sm"
          onClick={handleClearChat}
          disabled={messages.length === 0 && !error}
          className="text-muted-foreground hover:text-foreground"
        >
          <Trash2 className="h-4 w-4 mr-1.5" /> Clear
        </Button>
      </div>

      <div className="flex-1 min-h-0 flex gap-4">
        {/* ── Left: Config Sidebar ── */}
        <div className="w-72 shrink-0 flex flex-col gap-3 overflow-y-auto pr-1">
          <Card>
            <CardHeader className="px-4 py-3 pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                <Key className="h-3.5 w-3.5" /> Credentials
              </CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-4 space-y-3">
              <div className="space-y-1.5">
                <Label htmlFor="sb-apikey" className="text-xs">API Key</Label>
                <Input
                  id="sb-apikey"
                  type="password"
                  placeholder="pk-..."
                  value={apiKey}
                  onChange={(e) => { setApiKey(e.target.value); setError(""); }}
                  className="h-8 text-sm"
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="sb-model" className="text-xs">Model</Label>
                <select
                  id="sb-model"
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="flex h-8 w-full rounded-md border border-input bg-background px-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                >
                  {models.length === 0 && <option value="" disabled>Loading...</option>}
                  {models.map(m => <option key={m.id} value={m.id}>{m.id}</option>)}
                </select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="px-4 py-3 pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                <Settings className="h-3.5 w-3.5" /> Parameters
              </CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-4 space-y-4">
              <div className="space-y-1.5">
                <Label className="text-xs">System Prompt</Label>
                <Textarea
                  value={systemPrompt}
                  onChange={e => setSystemPrompt(e.target.value)}
                  rows={4}
                  placeholder="You are a helpful assistant..."
                  className="text-xs resize-none leading-relaxed"
                />
              </div>
              <Separator />
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label className="text-xs">Temperature</Label>
                  <span className="text-xs font-mono text-muted-foreground bg-muted px-1.5 py-0.5 rounded">{temperature[0].toFixed(1)}</span>
                </div>
                <Slider value={temperature} onValueChange={setTemperature} min={0} max={2} step={0.1} />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label className="text-xs">Max Tokens</Label>
                  <span className="text-xs font-mono text-muted-foreground bg-muted px-1.5 py-0.5 rounded">{maxTokens[0]}</span>
                </div>
                <Slider value={maxTokens} onValueChange={setMaxTokens} min={128} max={8192} step={128} />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-xs">Stream</Label>
                  <p className="text-[10px] text-muted-foreground">Token-by-token output</p>
                </div>
                <Switch id="sb-stream" checked={isStreaming} onCheckedChange={setIsStreaming} />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* ── Right: Chat Area ── */}
        <Card className="flex-1 flex flex-col min-h-0 overflow-hidden">
          {/* Messages */}
          <div className="flex-1 min-h-0 overflow-y-auto p-5 space-y-5">
            {visibleMessages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center gap-3 text-muted-foreground">
                <div className="h-14 w-14 rounded-2xl bg-primary/10 flex items-center justify-center">
                  <Sparkles className="h-7 w-7 text-primary" />
                </div>
                <div>
                  <p className="text-base font-medium text-foreground">Playground Ready</p>
                  <p className="text-sm mt-0.5">Fill in your API key and start a conversation.</p>
                </div>
              </div>
            ) : (
              visibleMessages.map((m, i) => (
                <div key={i} className={`flex gap-3 ${ m.role === "user" ? "flex-row-reverse" : "" }`}>
                  {/* Avatar */}
                  <div className={`shrink-0 h-8 w-8 rounded-full border flex items-center justify-center text-xs font-semibold ${
                    m.role === "user"
                      ? "bg-primary text-primary-foreground border-primary/50"
                      : "bg-muted text-muted-foreground border-border"
                  }`}>
                    {m.role === "user" ? <UserIcon className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                  </div>
                  {/* Bubble */}
                  <div className={`max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                    m.role === "user"
                      ? "bg-primary text-primary-foreground rounded-tr-sm"
                      : "bg-muted/50 border rounded-tl-sm"
                  }`}>
                    {m.role === "user" ? (
                      <span className="whitespace-pre-wrap">{m.content}</span>
                    ) : (
                      <div className="prose prose-sm dark:prose-invert max-w-none
                        prose-p:my-1 prose-p:leading-relaxed
                        prose-headings:font-semibold prose-headings:mt-3 prose-headings:mb-1
                        prose-code:text-[12px] prose-code:before:content-none prose-code:after:content-none
                        prose-code:bg-black/10 dark:prose-code:bg-white/10 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded
                        prose-pre:bg-black/10 dark:prose-pre:bg-white/5 prose-pre:rounded-lg prose-pre:p-3 prose-pre:my-2
                        prose-ul:my-1 prose-ol:my-1 prose-li:my-0
                        prose-blockquote:border-l-primary prose-blockquote:text-muted-foreground">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {m.content || "▋"}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
            {/* Typing indicator (non-streaming) */}
            {loading && !isStreaming && (
              <div className="flex gap-3">
                <div className="shrink-0 h-8 w-8 rounded-full border bg-muted flex items-center justify-center">
                  <Bot className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-muted/50 border flex items-center gap-1.5 shadow-sm">
                  <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground/60 animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground/60 animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground/60 animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            )}
            {error && (
              <div className="flex items-start gap-2 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-lg px-3 py-2">
                <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Bar */}
          <div className="shrink-0 border-t p-4 bg-background/80 backdrop-blur">
            <div className="relative">
              <Textarea
                ref={textareaRef}
                placeholder="Message the model… (Enter to send, Shift+Enter for newline)"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                rows={1}
                className="resize-none pr-12 min-h-[44px] max-h-40 text-sm leading-relaxed py-3 overflow-auto"
              />
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    size="icon"
                    onClick={handleSend}
                    disabled={loading || !input.trim()}
                    className="absolute right-2 bottom-2 h-8 w-8 rounded-lg"
                  >
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="top">Send (Enter)</TooltipContent>
              </Tooltip>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
