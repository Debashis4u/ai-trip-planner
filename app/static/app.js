import React, { useState } from "https://esm.sh/react@18.3.1";
import { createRoot } from "https://esm.sh/react-dom@18.3.1/client";
import htm from "https://esm.sh/htm@3.1.1";

const html = htm.bind(React.createElement);

const examplePrompts = [
  "Plan a 3 day Kyoto trip focused on food and temples under 60000 INR",
  "I need a 5 day Bali itinerary with beaches, coworking spots, and a mid-range budget",
  "Plan a weekend in Coorg for two adults with rain-friendly activities and packing tips",
];

function Banner() {
  return html`
    <header className="app-banner">
      <div className="banner-container">
        <div className="banner-logo-section">
          <svg className="banner-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10 12h4m-2-2v4m7-9h-14c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-14c0-1.1-.9-2-2-2z"/>
            <path d="M8 7v8m8-8v8" />
          </svg>
          <h1 className="banner-title">Trip Planner</h1>
          <p className="banner-subtitle">AI-Powered Travel Itineraries</p>
        </div>
        <div className="banner-description">
          <p>Generate personalized trip plans powered by advanced LLM reasoning</p>
        </div>
      </div>
    </header>
  `;
}

function App() {
  const [message, setMessage] = useState(examplePrompts[0]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("/plan-trip", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error("Trip planning request failed.");
      }

      const data = await response.json();
      setResult(data);
    } catch (submitError) {
      setError(submitError.message || "Unable to generate a trip plan.");
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  }

  function renderObject(obj) {
    return JSON.stringify(obj, null, 2);
  }

  function renderSectionValue(key, value) {
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return html`<p>No items available.</p>`;
      }
      const isNumberedSection = key === "plan" || key === "itinerary";
      const ListTag = isNumberedSection ? "ol" : "ul";
      return html`
        <${ListTag} className=${`section-list ${isNumberedSection ? "section-list-numbered" : ""}`}>
          ${value.map((item, idx) => html`<li key=${idx}>${typeof item === "string" ? item : renderObject(item)}</li>`) }
        </${ListTag}>
      `;
    }

    if (value && typeof value === "object") {
      return html`<pre>${renderObject(value)}</pre>`;
    }

    if (typeof value === "string") {
      return html`<p>${value}</p>`;
    }

    if (typeof value === "number" || typeof value === "boolean") {
      return html`<p>${String(value)}</p>`;
    }

    return html`<p>Not available</p>`;
  }

  function formatSectionTitle(key) {
    return key
      .replace(/_/g, " ")
      .split(" ")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }

  function getSectionIcon(key) {
    const icons = {
      destination: "🗺️",
      budget: "💰",
      duration: "⏱️",
      weather: "🌤️",
      plan: "📋",
      accommodation: "🏨",
      transportation: "🚌",
      packing_list: "🎒",
      local_tips: "💡",
      itinerary: "📅",
    };
    return icons[key] || "✨";
  }

  return html`
    <${Banner} />
    <main className="page-shell">
      <section className="hero-panel">
        <div className="hero-content">
          <h2 className="section-title">Start Planning Your Adventure</h2>
          <p className="section-description">
            Describe your ideal trip and let AI handle the details—weather forecasts, budgets, accommodations, and packed recommendations all included.
          </p>
        </div>
        <div className="examples-section">
          <p className="examples-label">Try one of these examples:</p>
          <div className="example-row">
            ${examplePrompts.map(
              (prompt) => html`
                <button
                  key=${prompt}
                  type="button"
                  className="chip"
                  onClick=${() => setMessage(prompt)}
                  title=${prompt}
                >
                  ${prompt}
                </button>
              `,
            )}
          </div>
        </div>
      </section>

      <section className="workspace-grid">
        <form className="card composer-card" onSubmit=${handleSubmit}>
          <div className="card-header">
            <h3 className="card-title">Describe Your Trip</h3>
            <p className="card-subtitle">Tell us about your destination, budget, duration, and preferences</p>
          </div>
          <textarea
            id="message"
            className="composer-input"
            value=${message}
            onChange=${(event) => setMessage(event.target.value)}
            placeholder="Example: Plan a 5-day trip to Japan under $3000 with budget hotels, street food, and temples..."
            rows="10"
          />
          <div className="composer-footer">
            <div className="hint-section">
              <span className="hint-badge">Tips</span>
              <p className="hint">Include destination, dates, budget, group size, interests, and any special requirements.</p>
            </div>
            <button className="submit-button" type="submit" disabled=${isLoading || !message.trim()}>
              ${isLoading ? html`<span className="spinner"></span> Planning...` : html`<span className="button-icon">✈️</span> Generate Trip`}
            </button>
          </div>
          ${error
            ? html`<div className="error-banner" role="alert">
                <span className="error-icon">⚠️</span>
                <p>${error}</p>
              </div>`
            : null}
        </form>

        <section className="card result-card">
          <div className="result-header">
            <h2 className="card-title">Your Trip Plan</h2>
            <span className="status-pill ${result ? "ready" : "idle"}">
              <span className="status-dot"></span>
              ${result ? "Plan ready" : "Awaiting request"}
            </span>
          </div>

          ${result
            ? html`
                <div className="result-sections">
                  ${Object.entries(result).map(
                    ([key, value], idx) => html`
                      <article key=${key} className="result-section" style=${{ animationDelay: `${idx * 0.05}s` }}>
                        <div className="section-header">
                          <h3>${formatSectionTitle(key)}</h3>
                          <span className="section-icon">${getSectionIcon(key)}</span>
                        </div>
                        <div className="section-content">
                          ${renderSectionValue(key, value)}
                        </div>
                      </article>
                    `,
                  )}
                </div>
              `
            : html`
                <div className="empty-state">
                  <div className="empty-state-icon">📍</div>
                  <h3>No trip plan yet</h3>
                  <p>Describe your dream trip to the left and we'll generate a complete itinerary with recommendations.</p>
                </div>
              `}
        </section>
      </section>
    </main>
  `;
}

createRoot(document.getElementById("root")).render(html`<${App} />`);