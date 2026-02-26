from mission_control.ui.components.styles import STYLES
from mission_control.ui.components.sidebar import SIDEBAR
from mission_control.ui.components.main_content import MAIN_CONTENT
from mission_control.ui.components.modals import MODALS
from mission_control.ui.components.scripts import SCRIPTS

DASHBOARD_HTML = (
    r"""
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        <title>Mission Control</title>
    """
    + STYLES
    + r"""
      </head>
      <body>
    """
    + SIDEBAR
    + r"""
        <div class="sidebar-backdrop" id="sidebarBackdrop" onclick="closeMobileSidebar()"></div>
        <div class="main-wrapper">
          <header>
            <div class="header-left" style="display:flex; align-items:center; gap:10px;">
              <button class="mobile-menu-btn" onclick="toggleMobileSidebar()">☰</button>
              <div class="page-title">Mission Control</div>
            </div>
            <div class="header-right">
              <div class="subtle">0.0.0.0:7777</div>
              <button class="theme-toggle" onclick="toggleTheme()">Toggle theme</button>
              <div class="status-pill connected"><span class="pulse"></span>Live</div>
            </div>
          </header>
    """
    + MAIN_CONTENT
    + r"""
        </div>
    """
    + MODALS
    + SCRIPTS
    + r"""
      </body>
    </html>
    """
)
