import Link from "next/link";
import { Activity, BarChart3, DatabaseZap, KeyRound, Network, Route, Server } from "lucide-react";

const nav = [
  { href: "/", label: "Overview", icon: Activity },
  { href: "/requests", label: "Requests", icon: DatabaseZap },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/providers", label: "Providers", icon: Server },
  { href: "/keys", label: "Keys", icon: KeyRound },
  { href: "/routing", label: "Routing", icon: Route },
  { href: "/cache", label: "Cache", icon: Network }
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">ModelRouterX</div>
        <nav className="nav">
          {nav.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.href} href={item.href}>
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}

