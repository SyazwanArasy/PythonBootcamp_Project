import streamlit as st
import streamlit.components.v1 as components

def render_topnav():
    st.markdown("""
    <style>
    .topnav-wrapper {
        display: flex;
        gap: 12px;
        align-items: center;
        position: fixed;
        top: 60px;
        left: var(--topnav-offset, 21rem);
        right: 0;
        z-index: 999;
        background-color: #1e1e1e;
        padding: 12px 24px;
        transition: left 0.2s ease;
    }
    .topnav-spacer {
        height: 60px;
    }
    .topnav-link {
        background-color: #2b2b2b;
        border-radius: 20px;
        padding: 8px 20px;
        color: white;
        text-decoration: none;
        font-size: 14px;
        font-weight: 600;
        transition: background-color 0.15s ease;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .topnav-link:hover {
        background-color: #3a3a3a;
    }
    .topnav-link svg {
        width: 16px;
        height: 16px;
        stroke: white;
    }
    </style>
    <div class="topnav-wrapper">
        <a class="topnav-link" href="/" target="_self">
            <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            Home
        </a>
        <a class="topnav-link" href="/history" target="_self">
            <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v5h5"/><path d="M3.05 13A9 9 0 1 0 6 5.3L3 8"/><path d="M12 7v5l4 2"/></svg>
            History
        </a>
        <a class="topnav-link" href="/analytics" target="_self">
            <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
            Analytics
        </a>
        </div>
    <div class="topnav-spacer"></div>
    """, unsafe_allow_html=True)

    # The script must run via components.html (a real iframe), since
    # <script> tags inside st.markdown are silently ignored by the browser
    components.html("""
    <script>
    (function() {
        function updateOffset() {
            const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
            const root = window.parent.document.documentElement;
            if (sidebar && sidebar.getAttribute('aria-expanded') === 'false') {
                root.style.setProperty('--topnav-offset', '0px');
            } else {
                root.style.setProperty('--topnav-offset', '21rem');
            }
        }

        updateOffset();

        // Disconnect any observer left over from a PREVIOUS page's iframe
        // (which gets destroyed on navigation, but its old flag/reference
        // survives on window.parent since that page itself doesn't reload)
        if (window.parent.__topnavObserver) {
            window.parent.__topnavObserver.disconnect();
        }

        const observer = new MutationObserver(updateOffset);
        observer.observe(window.parent.document.body, {
            attributes: true,
            subtree: true,
            attributeFilter: ['aria-expanded']
        });

        // Store this NEW observer so the NEXT page's iframe can clean it
        // up properly when it loads, instead of leaving orphaned observers
        window.parent.__topnavObserver = observer;
    })();
    </script>
    """, height=0)