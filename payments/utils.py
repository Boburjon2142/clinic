import base64
from io import BytesIO


def qr_base64(data: str):
    try:
        import qrcode
        from PIL import Image  # noqa: F401
    except Exception:
        return ''
    qr = qrcode.QRCode(version=1, box_size=3, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64}"

