import basic

while True:
    text = input('DAUPS >>> ')
    if text.strip() == "": continue

    result, error = basic.run('<stdin>', text)

    if error: print(error.as_string())
