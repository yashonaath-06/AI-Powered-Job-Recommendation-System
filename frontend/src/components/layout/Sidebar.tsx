"use client";
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Upload, Target, BarChart3, Brain, FileText } from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/upload", label: "Upload Resume", icon: Upload },
  { href: "/recommendations", label: "Recommendations", icon: Target },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r bg-card transition-transform">
      <div className="flex h-16 items-center gap-2 border-b px-6">
        <Brain className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-lg font-bold text-foreground">JobMatch AI</h1>
          <p className="text-xs text-muted-foreground">Smart Recommendations</p>
        </div>
      </div>
      <nav className="space-y-1 p-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link key={item.href} href={item.href} className={cn("flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors", isActive ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent hover:text-accent-foreground")}>
              <item.icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="absolute bottom-0 left-0 right-0 border-t p-4">
        <div className="rounded-lg bg-muted p-3">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-primary" />
            <span className="text-xs font-medium">AI-Powered Engine</span>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">NLP + ML matching with semantic analysis</p>
        </div>
      </div>
    </aside>
  );
}
