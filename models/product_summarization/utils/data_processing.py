def product_introduction_processing(row):
    """
    '텍스트' 컬럼에 저장된 JSON-like 문자열을 파싱해 상품소개 문구를 생성하는 함수
    """
    if not row['텍스트'] or row['텍스트'] == "":
        return ""

    text = eval(row['텍스트'])  # string -> dict 변환
    text_title = ' '.join(text['divs'])
    text_contents = [item for item in text['contents'] if "SSG.COM" not in item]
    text_contents = ' '.join(text_contents)
    product_introduction = text_title + text_contents
    return product_introduction
