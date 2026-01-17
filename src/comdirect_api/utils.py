import datetime
import io


def timestamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S%f")


def is_valid_tan(tan: str) -> bool:
    return isinstance(tan, str) and len(tan) == 6 and tan.isdigit()


def default_photo_tan_callback(png_bytes: bytes) -> str:
    from PIL import Image

    Image.open(io.BytesIO(png_bytes)).show()
    tan = input("Enter Photo-TAN: ")
    if not is_valid_tan(tan):
        raise ValueError("Invalid Photo-TAN")
    return tan


def default_sms_tan_callback() -> str:
    tan = input("Enter SMS-TAN: ")
    if not is_valid_tan(tan):
        raise ValueError("Invalid SMS-TAN")
    return tan


def default_push_tan_callback() -> str:
    input("Confirm push-TAN and press ENTER")
    return "123456"
