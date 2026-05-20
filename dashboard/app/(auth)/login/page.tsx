export default function LoginPage() {
  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 24 }}>
      <section className="card" style={{ width: "100%", maxWidth: 380 }}>
        <h1 className="page-title">ModelRouterX</h1>
        <p className="muted">Sign in to manage routing, keys, cache, and observability.</p>
        <div className="grid" style={{ marginTop: 18 }}>
          <input className="input" placeholder="Email" />
          <input className="input" placeholder="Password" type="password" />
          <button className="button primary">Sign in</button>
        </div>
      </section>
    </main>
  );
}

