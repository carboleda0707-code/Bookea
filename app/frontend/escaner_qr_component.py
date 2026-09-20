import streamlit.components.v1 as components

def render_escaner_qr_html():
    """Retorna el componente HTML/JS para escanear QR usando la cámara."""
    html_code = """
    <div style="text-align: center; font-family: sans-serif;">
        <div id="reader" style="width: 100%; max-width: 350px; margin: auto;"></div>
        <div id="result" style="margin-top: 10px; font-weight: bold; color: green;"></div>
    </div>

    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        function onScanSuccess(decodedText, decodedResult) {
            document.getElementById('result').innerText = "¡Detectado: " + decodedText + "!";
            const baseUrl = window.parent.location.href.split('?')[0];
            window.parent.location.href = baseUrl + "?codigo_scanned=" + encodeURIComponent(decodedText);
        }

        let html5QrCode = new Html5QrcodeScanner(
            "reader", { fps: 10, qrbox: 200 }, false);
        html5QrCode.render(onScanSuccess);
    </script>
    """
    return components.html(html_code, height=420)