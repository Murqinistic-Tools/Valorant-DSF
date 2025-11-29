# Valorant DSF
## Or with full name Valorant Daily Store Fetcher

> **Secure, Modern, and Hybrid (Desktop + Web) Valorant Store Controller.**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688?style=flat-square&logo=fastapi)
![PyWebview](https://img.shields.io/badge/PyWebview-Desktop-orange?style=flat-square)
![Geist UI](https://img.shields.io/badge/Design-Geist%20UI-black?style=flat-square&logo=vercel)

Valorant DSF (Desktop & Web App) is a hybrid application that allows players to check their daily store. Whether as a desktop widget or on your mobile device via local network (LAN).

---

## 🌟 Features

### 🖥️ Desktop App (Native)
*   **Token Sniffer:** Automatic login via a popup window similar to Riot Client, no need to copy-paste tokens.
*   **Widget Design:** Stylish interface with 700x400 dimensions, occupying minimal screen space.
*   **Ghost Close:** The window hides immediately upon login, ensuring a seamless experience without showing white pages or errors.

### 📱 Web App (LAN)
*   **Mobile Access:** Access the server running on your PC from your phone (`https://192.168.x.x:8000`).
*   **Paste-Login:** Secure "Paste Link" method tailored for mobile where browser automation is restricted.
*   **HTTPS:** Encrypted communication using self-signed certificates.

### 🛡️ Security & Privacy
*   **Stateless:** Tokens are never saved to disk, they exist only in RAM.
*   **No Logs:** Sensitive data (Access Token, PUUID) is never printed to console or logs.

---

## 🛠️ Installation (Windows)

1.  **Prepare the Project:**
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    ```powershell
    pip install -r requirements.txt
    ```

3.  **🔐 SSL Certificate (CRITICAL):**
    Generate a certificate for the Web Server to enable HTTPS:
    ```powershell
    python setup_cert.py
    ```

---

## 🚀 Usage

Start the application with a single command. The CLI menu will guide you:

```powershell
python run.py
```

Options:
1.  **Desktop App:** Launches the native desktop widget.
2.  **Web Server:** Starts the local network server.

---

## 📦 Build (Create EXE)

To compile the application into a single `.exe` file:

```powershell
python build_desktop.py
```
*(Requirement: `pyinstaller` must be installed)*

---

## ⚖️ Legal Disclaimer

This project (ValoStore) is not an official product of Riot Games and is not endorsed by or affiliated with Riot Games or any person involved in the production or management of Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc.

**User Responsibility:**
This software is intended for educational and personal use only. The developer cannot be held responsible for any account restrictions (bans), data loss, or other issues that may arise from the use of this software. The user accepts that they use this software at their own risk.

**License:**
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
