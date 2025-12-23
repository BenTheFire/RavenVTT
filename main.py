import sys
import os
import datetime
from PyQt6.QtWidgets import QApplication
from ui.main_application_window import MainApplicationWindow
from ui.eula_dialog import EulaDialog
from utils.security import encrypt_data

EULA_ACCEPTED_PATH = 'resources/data/eula.accepted'
EULA_FILE_PATH = 'resources/EULA'
LICENSE_FILE_PATH = 'resources/LICENSE'


def check_and_show_eula():
    """Checks if the EULA has been accepted and shows the dialog if not."""
    if os.path.exists(EULA_ACCEPTED_PATH):
        return True

    dialog = EulaDialog(eula_path=EULA_FILE_PATH, license_path=LICENSE_FILE_PATH)
    if dialog.exec():
        # User accepted
        os.makedirs(os.path.dirname(EULA_ACCEPTED_PATH), exist_ok=True)
        timestamp = datetime.datetime.now().isoformat().encode('utf-8')
        encrypted_timestamp = encrypt_data(timestamp)
        with open(EULA_ACCEPTED_PATH, 'wb') as f:
            f.write(encrypted_timestamp)
        return True
    else:
        # User rejected
        return False


def main():
    app = QApplication(sys.argv)

    if not check_and_show_eula():
        sys.exit(0) # Exit gracefully if user rejects EULA

    window = MainApplicationWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
