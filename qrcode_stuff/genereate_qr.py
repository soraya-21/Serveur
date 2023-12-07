# generate_qr.py
import qrcode
import sys

def generate_qr_code(user_id):
    frontend_url = f"https://votre-site-web.com/user/{user_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(frontend_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f"static/qrcodes/{user_id}.png")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_qr.py <user_id>")
        sys.exit(1)

    user_id = sys.argv[1]
    generate_qr_code(user_id)
