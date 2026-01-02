/**
 * AI Search Enhancer Bookmarklet
 * Scrapes search results and displays AI-powered summary
 */

(function() {
  'use strict';

  const API_URL = 'http://localhost:5000';

  // Detect which search engine we're on
  function detectEngine() {
    const hostname = window.location.hostname;
    if (hostname.includes('google.com')) return 'google';
    if (hostname.includes('bing.com')) return 'bing';
    if (hostname.includes('duckduckgo.com')) return 'duckduckgo';
    return 'unknown';
  }

  // Extract query from URL
  function extractQuery() {
    const url = new URL(window.location.href);
    return url.searchParams.get('q') || url.searchParams.get('query') || '';
  }

  // Scrape Google results
  function scrapeGoogle() {
    const results = [];
    const items = document.querySelectorAll('div.g, div[data-hveid]');

    items.forEach(item => {
      const titleEl = item.querySelector('h3');
      const linkEl = item.querySelector('a');
      const snippetEl = item.querySelector('div[data-sncf], div.VwiC3b, span.st');

      if (titleEl && linkEl && snippetEl) {
        results.push({
          title: titleEl.textContent.trim(),
          url: linkEl.href,
          snippet: snippetEl.textContent.trim()
        });
      }
    });

    return results.slice(0, 10);
  }

  // Scrape Bing results
  function scrapeBing() {
    const results = [];
    const items = document.querySelectorAll('li.b_algo');

    items.forEach(item => {
      const titleEl = item.querySelector('h2 a');
      const snippetEl = item.querySelector('p, div.b_caption p');

      if (titleEl && snippetEl) {
        results.push({
          title: titleEl.textContent.trim(),
          url: titleEl.href,
          snippet: snippetEl.textContent.trim()
        });
      }
    });

    return results.slice(0, 10);
  }

  // Scrape DuckDuckGo results
  function scrapeDuckDuckGo() {
    const results = [];
    const items = document.querySelectorAll('article[data-testid="result"]');

    items.forEach(item => {
      const titleEl = item.querySelector('h2 a, [data-testid="result-title-a"]');
      const snippetEl = item.querySelector('[data-result="snippet"]');

      if (titleEl && snippetEl) {
        results.push({
          title: titleEl.textContent.trim(),
          url: titleEl.href,
          snippet: snippetEl.textContent.trim()
        });
      }
    });

    return results.slice(0, 10);
  }

  // Scrape results based on engine
  function scrapeResults(engine) {
    switch (engine) {
      case 'google':
        return scrapeGoogle();
      case 'bing':
        return scrapeBing();
      case 'duckduckgo':
        return scrapeDuckDuckGo();
      default:
        return [];
    }
  }

  // Send to server
  async function getSummary(query, results) {
    try {
      const response = await fetch(`${API_URL}/summarize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, results })
      });

      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Create and show UI
  function showUI(state, data = {}) {
    // Remove existing overlay
    const existing = document.getElementById('ai-search-overlay');
    if (existing) existing.remove();

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'ai-search-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.7);
      z-index: 999999;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      backdrop-filter: blur(4px);
    `;

    // Create modal
    const modal = document.createElement('div');
    modal.style.cssText = `
      background: white;
      border-radius: 16px;
      width: 700px;
      max-width: 90%;
      max-height: 80vh;
      overflow: hidden;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
      display: flex;
      flex-direction: column;
    `;

    // Header
    const header = document.createElement('div');
    header.style.cssText = `
      padding: 24px;
      border-bottom: 1px solid #e0e0e0;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    `;

    const title = document.createElement('h2');
    title.textContent = '🤖 AI Search Summary';
    title.style.cssText = 'margin: 0; font-size: 24px; font-weight: 600;';

    const closeBtn = document.createElement('button');
    closeBtn.textContent = '×';
    closeBtn.style.cssText = `
      background: none;
      border: none;
      color: white;
      font-size: 32px;
      cursor: pointer;
      padding: 0;
      width: 32px;
      height: 32px;
      line-height: 32px;
      opacity: 0.8;
      transition: opacity 0.2s;
    `;
    closeBtn.onmouseover = () => closeBtn.style.opacity = '1';
    closeBtn.onmouseout = () => closeBtn.style.opacity = '0.8';
    closeBtn.onclick = () => overlay.remove();

    header.appendChild(title);
    header.appendChild(closeBtn);

    // Content
    const content = document.createElement('div');
    content.style.cssText = `
      padding: 24px;
      overflow-y: auto;
      flex: 1;
    `;

    if (state === 'loading') {
      content.innerHTML = `
        <div style="text-align: center; padding: 40px;">
          <div style="
            width: 50px;
            height: 50px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
          "></div>
          <p style="color: #666; font-size: 16px;">Analyzing search results with AI...</p>
          <p style="color: #999; font-size: 14px;">This may take a few seconds</p>
        </div>
        <style>
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        </style>
      `;
    } else if (state === 'error') {
      content.innerHTML = `
        <div style="
          padding: 20px;
          background: #fee;
          border-left: 4px solid #f44;
          border-radius: 4px;
        ">
          <h3 style="margin: 0 0 10px 0; color: #c33;">❌ Error</h3>
          <p style="margin: 0; color: #666;">${data.error}</p>
          <p style="margin: 10px 0 0 0; font-size: 14px; color: #999;">
            Make sure Ollama is running: <code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">ollama serve</code>
          </p>
        </div>
      `;
    } else if (state === 'success') {
      const queryInfo = document.createElement('div');
      queryInfo.style.cssText = `
        padding: 12px;
        background: #f8f9fa;
        border-radius: 8px;
        margin-bottom: 20px;
      `;
      queryInfo.innerHTML = `
        <div style="font-size: 14px; color: #666; margin-bottom: 4px;">Search Query:</div>
        <div style="font-size: 16px; font-weight: 500; color: #333;">"${data.query}"</div>
      `;

      const summary = document.createElement('div');
      summary.style.cssText = `
        line-height: 1.8;
        color: #333;
        font-size: 15px;
      `;
      summary.textContent = data.summary;

      const footer = document.createElement('div');
      footer.style.cssText = `
        margin-top: 20px;
        padding-top: 16px;
        border-top: 1px solid #e0e0e0;
        font-size: 13px;
        color: #999;
        display: flex;
        justify-content: space-between;
      `;
      footer.innerHTML = `
        <span>📊 Analyzed ${data.num_results} results</span>
        <span>🤖 Model: ${data.model}</span>
      `;

      content.appendChild(queryInfo);
      content.appendChild(summary);
      content.appendChild(footer);
    }

    modal.appendChild(header);
    modal.appendChild(content);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    // Close on overlay click
    overlay.onclick = (e) => {
      if (e.target === overlay) overlay.remove();
    };

    // Close on ESC key
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        overlay.remove();
        document.removeEventListener('keydown', handleEscape);
      }
    };
    document.addEventListener('keydown', handleEscape);
  }

  // Main execution
  async function main() {
    const engine = detectEngine();

    if (engine === 'unknown') {
      showUI('error', {
        error: 'Unsupported search engine. This bookmarklet works with Google, Bing, and DuckDuckGo.'
      });
      return;
    }

    const query = extractQuery();
    if (!query) {
      showUI('error', {
        error: 'Could not detect search query. Make sure you are on a search results page.'
      });
      return;
    }

    const results = scrapeResults(engine);
    if (results.length === 0) {
      showUI('error', {
        error: 'Could not extract search results. The page structure may have changed.'
      });
      return;
    }

    showUI('loading');

    const response = await getSummary(query, results);

    if (response.success) {
      showUI('success', response);
    } else {
      showUI('error', response);
    }
  }

  main();
})();
