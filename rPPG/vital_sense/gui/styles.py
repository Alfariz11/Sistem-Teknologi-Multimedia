class AppColors:
    BG_DARK = "#121212"
    PANEL_BG = "#1E1E1E"
    BORDER = "#333333"
    
    ACCENT = "#00BCD4" # Cyan
    ACCENT_HOVER = "#26C6DA"
    
    TEXT_MAIN = "#FFFFFF"
    TEXT_DIM = "#AAAAAA"
    
    # Status
    STATUS_OK = "#4CAF50" # Green
    STATUS_WARN = "#FFC107" # Amber
    STATUS_BAD = "#F44336" # Red

def get_status_color(bpm):
    if bpm < 50 or bpm > 120:
        return AppColors.STATUS_BAD
    elif bpm < 60 or bpm > 100:
        return AppColors.STATUS_WARN
    else:
        return AppColors.STATUS_OK

class AppStyles:
    MAIN = f"""
        QMainWindow {{
            background-color: {AppColors.BG_DARK};
        }}
        QWidget {{
            color: {AppColors.TEXT_MAIN};
            font-family: 'Segoe UI', sans-serif;
        }}
    """
    
    PANEL = f"""
        background-color: {AppColors.PANEL_BG};
        border-radius: 12px;
        border: 1px solid {AppColors.BORDER};
    """
    
    TITLE = f"""
        color: {AppColors.ACCENT};
        font-size: 20px;
        font-weight: bold;
    """
    
    BTN_MAIN = f"""
        QPushButton {{
            background-color: {AppColors.ACCENT};
            color: #000;
            border-radius: 6px;
            padding: 10px;
            font-weight: bold;
            border: none;
        }}
        QPushButton:hover {{
            background-color: {AppColors.ACCENT_HOVER};
        }}
    """
    
    BTN_SEC = f"""
        QPushButton {{
            background-color: transparent;
            color: {AppColors.ACCENT};
            border: 1px solid {AppColors.ACCENT};
            border-radius: 6px;
            padding: 10px;
        }}
        QPushButton:hover {{
            background-color: rgba(0, 188, 212, 0.1);
        }}
    """
