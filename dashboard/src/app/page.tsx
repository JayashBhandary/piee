"use client";

import { useState, useEffect } from "react";
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
                className={`flex items-center gap-2.5 w-full px-3 py-2 rounded-md text-sm transition-colors ${
                  page === item.id
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
      .catch(() => {});
    fetch(`${API_URL}/v1/models`)
      .then((r) => r.json())
      .then((d) => setModelCount(d.data?.length || 0))
      .catch(() => {});
    apiRequest("GET", "/billing/balance")
      .then(setBalance)
      .catch(() => {});
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

function ModelsPage() {
  const [models, setModels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/v1/models`)
      .then((r) => r.json())
      .then((d) => {
        setModels(d.data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
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
    } catch {}
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
    } catch {}
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
      .catch(() => {})
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
      .catch(() => {});
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
