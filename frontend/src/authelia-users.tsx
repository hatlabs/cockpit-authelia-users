import { createRoot } from "react-dom/client";
import "@patternfly/patternfly/patternfly.css";
import "./authelia-users.css";

function App() {
  return (
    <div className="pf-v6-c-page">
      <main className="pf-v6-c-page__main">
        <section className="pf-v6-c-page__main-section">
          <h1>Authelia Users</h1>
          <p>User management interface coming soon.</p>
        </section>
      </main>
    </div>
  );
}

const container = document.getElementById("root");
if (container) {
  const root = createRoot(container);
  root.render(<App />);
}
