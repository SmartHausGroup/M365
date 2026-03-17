# Website Integration Examples

## AI Workforce Directory (Next.js 14)

Use the provided `registry/ai_team.json` to render the AI team page.

```tsx
// app/team/ai-workforce/page.tsx
import aiTeam from '@/data/ai_team.json'

function groupBy<T, K extends keyof any>(list: T[], getKey: (item: T) => K): Record<K, T[]> {
  return list.reduce((acc, item) => {
    const k = getKey(item)
    ;(acc[k] ||= []).push(item)
    return acc
  }, {} as Record<K, T[]>)
}

export default function AIWorkforce() {
  const departments = groupBy(aiTeam as any[], (m: any) => m.department)
  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold mb-8">Meet Our AI Workforce</h1>
      <p className="text-xl mb-12 text-gray-600">
        Our 39 AI employees work 24/7 to deliver exceptional results.
      </p>
      {Object.entries(departments).map(([dept, members]) => (
        <section key={dept} className="mb-12">
          <h2 className="text-2xl font-semibold mb-4 capitalize">{dept.replace('-', ' ')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {(members as any[]).map((m) => (
              <div key={m.agent} className="rounded-lg border p-4">
                <div className="font-semibold">{m.name}</div>
                <div className="text-sm text-gray-600">{m.role}</div>
                <div className="mt-2 text-xs bg-gray-100 inline-block px-2 py-1 rounded">{m.agent}</div>
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}
```

## Approvals Dashboard (Next.js API route)

```ts
// app/api/approvals/query/route.ts
export async function GET(req: Request) {
  const url = new URL(req.url)
  const params = url.searchParams
  const qs = params.toString()
  const base = process.env.OPS_ADAPTER_URL || 'http://localhost:8080'
  const res = await fetch(`${base}/approvals/query?${qs}`, { cache: 'no-store' })
  return new Response(await res.text(), { status: res.status, headers: { 'Content-Type': 'application/json' } })
}
```

```tsx
// app/operations/approvals/page.tsx
'use client'
import { useEffect, useState } from 'react'

export default function ApprovalsDashboard() {
  const [approvals, setApprovals] = useState<any[]>([])
  const [filters, setFilters] = useState({ status: 'pending' } as any)

  useEffect(() => {
    const params = new URLSearchParams(filters as any)
    fetch(`/api/approvals/query?${params.toString()}`).then(async (r) => setApprovals((await r.json()).items || []))
  }, [filters])

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-4">
      <h1 className="text-3xl font-bold">Approval Management</h1>
      <div className="flex gap-2">
        <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="denied">Denied</option>
        </select>
      </div>
      <ul className="space-y-2">
        {approvals.map((a) => (
          <li key={a.id} className="border rounded p-3 flex items-center justify-between">
            <div>
              <div className="font-medium">{a.agent}/{a.action}</div>
              <div className="text-sm text-gray-600">Requested: {a.requested_at}</div>
            </div>
            <span className="text-xs uppercase bg-gray-100 px-2 py-1 rounded">{a.status}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
```

