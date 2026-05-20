import streamlit as st
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
import io

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(page_title="SEO XML Generator", layout="wide")
st.title("SEO XML Generator for SFCC")

LANGUAGES = ["en", "de", "fr", "it", "es", "pt", "nl", "pl", "da", "sv", "ja", "ko"]

COUNTRY_LANGUAGES = [
    "en-GB", "en-IE",
    "de-DE", "de-AT", "de-CH",
    "fr-FR", "fr-BE", "fr-CH",
    "it-IT", "it-CH",
    "es-ES",
    "pt-PT",
    "nl-NL", "nl-BE",
    "pl-PL",
    "da-DK",
    "sv-SE",
    "ja-JP",
    "ko-KR"
]

if "df" not in st.session_state:
    st.session_state.df = None

category_id = st.text_input("Category ID", placeholder="e.g. 25300")

category_name = st.text_input(
    "Category / Landing Page Name",
    placeholder="e.g. Men's Trousers & Shorts"
)

gender = st.selectbox("Gender", ["Men", "Women", "Kids"])

product = st.text_input("Product", placeholder="e.g. Jackets & Coats")

brand = st.text_input("Brand", value="HUGO BOSS")

is_sale = st.checkbox("Sale page")

discount = ""

if is_sale:
    discount = st.text_input(
        "Discount message",
        placeholder="e.g. up to 40% off"
    )

brief = st.text_area(
    "SEO Brief",
    placeholder="Explain the SEO change, target keyword, context, restrictions, etc."
)

target_level = st.selectbox(
    "SFCC action type",
    [
        "default",
        "language",
        "country-language",
        "language + clear country-language overrides"
    ]
)

rows = []

if target_level == "default":
    if st.button("Create table"):
        rows.append({
            "category_id": category_id,
            "sfcc_level": "default",
            "xml_lang": "",
            "action": "update",
            "page_title": "",
            "page_description": "",
            "page_url": "",
            "headline": ""
        })

elif target_level == "language":
    selected_languages = st.multiselect(
        "Languages to update",
        LANGUAGES,
        default=["en"]
    )

    if st.button("Create table"):
        for lang in selected_languages:
            rows.append({
                "category_id": category_id,
                "sfcc_level": "language",
                "xml_lang": lang,
                "action": "update",
                "page_title": "",
                "page_description": "",
                "page_url": "",
                "headline": ""
            })

elif target_level == "country-language":
    selected_country_languages = st.multiselect(
        "Country-language locales to update",
        COUNTRY_LANGUAGES,
        default=["en-GB"]
    )

    if st.button("Create table"):
        for locale in selected_country_languages:
            rows.append({
                "category_id": category_id,
                "sfcc_level": "country-language",
                "xml_lang": locale,
                "action": "update",
                "page_title": "",
                "page_description": "",
                "page_url": "",
                "headline": ""
            })

else:
    selected_languages = st.multiselect(
        "Languages to update",
        LANGUAGES,
        default=["en"]
    )

    selected_country_languages = st.multiselect(
        "Country-language overrides to clear",
        COUNTRY_LANGUAGES,
        default=["en-GB"]
    )

    if st.button("Create table"):
        for lang in selected_languages:
            rows.append({
                "category_id": category_id,
                "sfcc_level": "language",
                "xml_lang": lang,
                "action": "update",
                "page_title": "",
                "page_description": "",
                "page_url": "",
                "headline": ""
            })

        for locale in selected_country_languages:
            rows.append({
                "category_id": category_id,
                "sfcc_level": "country-language",
                "xml_lang": locale,
                "action": "clear",
                "page_title": "",
                "page_description": "",
                "page_url": "",
                "headline": ""
            })

if rows:
    st.session_state.df = pd.DataFrame(rows)

if st.session_state.df is not None:
    df = st.session_state.df

    st.subheader("SEO Copy / XML Preparation Table")

    update_locales = df[df["action"] == "update"]["xml_lang"].tolist()

    if target_level == "default":
        update_locales = ["default"]

    if st.button("Generate AI SEO Copy"):
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
Locales: {", ".join(update_locales)}

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
- If locale is default, generate English copy.
- Sale examples:
  - en: Sale
  - pt: Saldos
  - it: Saldi
  - fr: Soldes
  - es: Rebajas
  - de: Sale
  - nl: Sale
  - pl: Sale
  - da: Sale
  - sv: Sale
  - ja: パブリックセール
  - ko: Sale

URL RULES:
- lowercase
- hyphen-separated
- no accents
- no apostrophes
- no special characters
- no brand in URL
- remove filler words where needed

META DESCRIPTION:
- max 155 characters
- commercial and premium tone
- mention the product category
- mention the brand
- if sale page, mention the discount

Return ONLY valid CSV.
Do not wrap the CSV in markdown.
Do not add explanations.

Columns:
locale,page_title,page_description,page_url,headline
"""

        response = model.generate_content(prompt)
        csv_text = response.text.strip()

        ai_df = pd.read_csv(io.StringIO(csv_text))

        for index, row in df.iterrows():
            if row["action"] == "update":
                locale_key = row["xml_lang"] if row["xml_lang"] else "default"
                match = ai_df[ai_df["locale"] == locale_key]

                if not match.empty:
                    df.at[index, "page_title"] = match.iloc[0]["page_title"]
                    df.at[index, "page_description"] = match.iloc[0]["page_description"]
                    df.at[index, "page_url"] = match.iloc[0]["page_url"]
                    df.at[index, "headline"] = match.iloc[0]["headline"]

        st.session_state.df = df
        st.success("AI SEO copy generated.")

    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        num_rows="dynamic"
    )

    st.session_state.df = edited_df

    st.subheader("Preview")
    st.dataframe(st.session_state.df, use_container_width=True)

def escape_xml(value):
    if pd.isna(value):
        return ""

    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def generate_xml(df, catalog_id="hb-eu"):
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += f'<catalog xmlns="http://www.demandware.com/xml/impex/catalog/2006-10-31" catalog-id="{catalog_id}">\n\n'

    for category_id, group in df.groupby("category_id"):
        xml += f'  <category category-id="{category_id}">\n'

        # PAGE ATTRIBUTES
        xml += '    <page-attributes>\n'

        # 1. All page descriptions first
        for _, row in group.iterrows():
            lang_attr = f' xml:lang="{row["xml_lang"]}"' if row["xml_lang"] else ""
            value = "" if row["action"] == "clear" else escape_xml(row["page_description"])
            xml += f'      <page-description{lang_attr}>{value}</page-description>\n'

        # 2. Then all page titles
        for _, row in group.iterrows():
            lang_attr = f' xml:lang="{row["xml_lang"]}"' if row["xml_lang"] else ""
            value = "" if row["action"] == "clear" else escape_xml(row["page_title"])
            xml += f'      <page-title{lang_attr}>{value}</page-title>\n'

        # 3. Then all page URLs
        for _, row in group.iterrows():
            lang_attr = f' xml:lang="{row["xml_lang"]}"' if row["xml_lang"] else ""
            value = "" if row["action"] == "clear" else escape_xml(row["page_url"])
            xml += f'      <page-url{lang_attr}>{value}</page-url>\n'

        xml += '    </page-attributes>\n'

        # CUSTOM ATTRIBUTES
        xml += '    <custom-attributes>\n'

        # 4. Then all headlines
        for _, row in group.iterrows():
            lang_attr = f' xml:lang="{row["xml_lang"]}"' if row["xml_lang"] else ""
            value = "" if row["action"] == "clear" else escape_xml(row["headline"])
            xml += f'      <custom-attribute attribute-id="headline"{lang_attr}>{value}</custom-attribute>\n'

        xml += '    </custom-attributes>\n'
        xml += '  </category>\n\n'

    xml += '</catalog>'
    return xml

st.divider()

if st.session_state.df is not None:
    if st.button("Generate XML"):
        xml_output = generate_xml(st.session_state.df)

        st.subheader("XML Output")
        st.code(xml_output, language="xml")

        st.download_button(
            label="Download XML",
            data=xml_output,
            file_name="seo_metadata_import.xml",
            mime="application/xml"
        )