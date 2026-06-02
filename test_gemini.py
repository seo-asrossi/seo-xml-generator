import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

gender = "Men"
product = "Jackets & Coats"
brand = "HUGO BOSS"
is_sale = True
discount = "up to 40% off"
brief = "Winter sale category for premium menswear."
locale_list = ["en", "de", "fr"]

prompt = f"""
You are an international SEO specialist for a luxury fashion ecommerce brand.

Generate SEO metadata using the exact taxonomy rules below.

INPUTS:
Gender: {gender}
Product: {product}
Brand: {brand}
Is sale page: {is_sale}
Discount message: {discount}
SEO Brief: {brief}
Locales: {", ".join(locale_list)}

STRICT TAXONOMY:
1. For non-sale pages:
- page_title must follow: [Localized Gender's Product] | [Brand]
- headline must follow: [Localized Gender's Product]
- page_url must follow: [localized-gender]-[localized-product]

2. For sale pages:
- page_title must follow: [Localized Sale] | [Localized Gender's Product] [Localized Discount] | [Brand]
- headline must follow: [Localized Sale] | [Localized Gender's Product] [Localized Discount]
- page_url must follow: [localized-sale]-[localized-gender]-[localized-product]

LOCALIZATION:
- Localize gender, product, sale label and discount naturally for each locale.

URL RULES:
- lowercase
- hyphen-separated
- no accents
- no apostrophes
- no special characters
- no brand in URL
- remove filler words where needed
- do not transliterate Japanese or Korean URLs
- keep Japanese and Korean URLs in English

Return ONLY valid CSV.

Columns:
locale,page_title,page_url,headline
"""

response = model.generate_content(prompt)

print(response.text)