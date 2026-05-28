import time
import requests
from playwright.sync_api import sync_playwright
import os

URL = os.getenv("LINK")

def enviar_telegram(mensaje):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    try:
        requests.get(
            f"https://api.telegram.org/bot{token}/sendMessage",
            params={"chat_id": chat_id, "text": mensaje}
        )
    except:
        pass


def revisar_stock(page):
    print(f"LINK recibido: '{URL}'")

    # Navegación
    page.goto(URL, wait_until="networkidle")
    print(page.url)
    print(page.content()[:500])

    # Espera humana
    page.wait_for_timeout(1500)

    # Movimiento humano
    page.mouse.move(200, 300, steps=25)

    # Screenshot para debug
    page.screenshot(path="page.png", full_page=True)
    time.sleep(2)

    html = page.content().lower()

    # Indicadores de NO stock
    no_stock = [
        "sold out", "out of stock", "notify me", "sold-out",
        "currently unavailable", "agotado", "soldout"
    ]
    if any(p in html for p in no_stock):
        return False

    # Indicadores de SÍ stock
    yes_stock = [
        "add to cart", "add-to-cart", "addtocart", "buy now",
        "comprar", "añadir", "add-to-bag", "add to bag",
        "add-to-basket", "add to basket"
    ]
    if any(p in html for p in yes_stock):
        return True

    # Botones reales
    try:
        botones = page.locator("button").all_text_contents()
        botones = [b.lower() for b in botones]
        if any(any(x in b for x in ["add", "buy", "cart", "bag", "basket", "comprar", "añadir"]) for b in botones):
            return True
    except:
        pass

    return False


os.environ["HOME"] = "/root"
os.makedirs("/root/.cache/ms-playwright", exist_ok=True)

with sync_playwright() as p:

    print("🟢 El script ha iniciado correctamente (Railway lo reinició).")
    enviar_telegram("🟢 El script ha iniciado correctamente (Railway lo reinició).")

    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled"
        ]
    )

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        device_scale_factor=1,
        is_mobile=False,
    )

    page = context.new_page()

    # Anti‑detección (ANTES de navegar)
    page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
    """)

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
