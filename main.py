import time
import requests
from playwright.sync_api import sync_playwright
import os

URL = "LINK"

# -----------------------------
# Función para enviar mensajes a Telegram
# -----------------------------
def enviar_telegram(mensaje):
    token = "TELEGRAM_TOKEN"  # Usa variables de entorno en Railway
    chat_id = "TELEGRAM_CHAT_ID"  # Usa variables de entorno en Railway

    try:
        requests.get(
            f"https://api.telegram.org/bot{token}/sendMessage",
            params={"chat_id": chat_id, "text": mensaje}
        )
    except:
        pass


# -----------------------------
# Función robusta para revisar stock
# -----------------------------
def revisar_stock(page):
    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(5000)

    # SOLO PARA DEBUG: screenshot (Railway la guarda en el contenedor)
    page.screenshot(path="page.png", full_page=True)
    time.sleep(2)

    html = page.content().lower()

    # 1) Indicadores de NO stock
    no_stock = [
        "sold out",
        "out of stock",
        "notify me",
        "sold-out",
        "currently unavailable",
        "agotado",
        "soldout"
    ]

    for palabra in no_stock:
        if palabra in html:
            return False

    # 2) Indicadores de SÍ stock
    yes_stock = [
        "add to cart",
        "add-to-cart",
        "addtocart",
        "buy now",
        "comprar",
        "añadir",
        "add-to-bag",
        "add to bag",
        "add-to-basket",
        "add to basket"
    ]

    for palabra in yes_stock:
        if palabra in html:
            return True

    # 3) Detección por botones reales
    try:
        botones = page.locator("button").all_text_contents()
        botones = [b.lower() for b in botones]

        for b in botones:
            if any(x in b for x in ["add", "buy", "cart", "bag", "basket", "comprar", "añadir"]):
                return True
    except:
        pass

    # 4) Si no encontramos nada claro → NO hay stock
    return False

os.environ["HOME"] = "/root"
os.makedirs("/root/.cache/ms-playwright", exist_ok=True)    

# -----------------------------
# PROCESO PRINCIPAL
# -----------------------------
with sync_playwright() as p:

    print("🟢 El script ha iniciado correctamente (Railway lo reinició).")
    enviar_telegram("🟢 El script ha iniciado correctamente (Railway lo reinició).")

    browser = p.chromium.launch(
        headless=True,   # IMPORTANTE: Railway lo ejecuta en modo headful virtual
        args=[ 
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled"
        ]
    )

    context = browser.new_context()
    page = context.new_page()

    while True:
        try:
            disponible = revisar_stock(page)

            if disponible:
                enviar_telegram("🔥 ¡EL PRODUCTO ESTÁ DISPONIBLE EN PANINI!")
                print("🔥 ¡EL PRODUCTO ESTÁ DISPONIBLE EN PANINI!")
                time.sleep(120)
            else:
                print("No está disponible. Revisando de nuevo en 30 segundos...")
                time.sleep(30)

        except Exception as e:
            enviar_telegram(f"🔴 Error en el script: {e}")
            print(f"🔴 Error en el script: {e}")
            time.sleep(60)
