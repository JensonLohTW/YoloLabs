
try:
    import paddle
    print(f"paddle: {paddle.__version__}")
except ImportError:
    print("paddle: not installed")

try:
    import paddleocr
    print(f"paddleocr: {paddleocr.VERSION}") # paddleocr sometimes uses VERSION
    if not hasattr(paddleocr, 'VERSION'):
        import pkg_resources
        print(f"paddleocr: {pkg_resources.get_distribution('paddleocr').version}")
except Exception as e:
    print(f"paddleocr error: {e}")

try:
    import paddlex
    print(f"paddlex: {paddlex.__version__}")
except ImportError:
    print("paddlex: not installed")
except Exception as e:
    print(f"paddlex error: {e}")
