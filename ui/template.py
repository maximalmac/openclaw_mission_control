from mission_control.ui.components.styles import STYLES
from mission_control.ui.components.sidebar import SIDEBAR
from mission_control.ui.components.main_content import MAIN_CONTENT
from mission_control.ui.components.modals import MODALS
from mission_control.ui.components.scripts import SCRIPTS

DASHBOARD_HTML = (
    r"""
    <html>
      <head>
        <title>Mission Control</title>
    """
    + STYLES
    + r"""
      </head>
      <body>
    """
    + SIDEBAR
    + r"""
        <div class="main-wrapper">
          <header>
            <div class="header-left">
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
