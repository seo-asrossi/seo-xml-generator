import streamlit as st
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

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

if "category_input_df" not in st.session_state:
    st.session_state.category_input_df = pd.DataFrame({
        "category_id": [""],
        "landing_page_name": [""],
        "gender": ["Men"],
        "product": [""]
    })

st.subheader("Category Inputs")
st.caption("Add up to 10 category IDs. Use one row per category. Max combination: 10 cat-ids in 3 languages.")

category_input_df = st.data_editor(
    st.session_state.category_input_df,
    key="category_input_editor",
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "category_id": st.column_config.TextColumn("Category ID"),
        "landing_page_name": st.column_config.TextColumn("Landing Page Name"),
        "gender": st.column_config.SelectboxColumn("Gender", options=["Men", "Women", "Kids"]),
        "product": st.column_config.TextColumn("Product")
    }
)

valid_categories = category_input_df[
    category_input_df["category_id"].astype(str).str.strip().ne("")
].copy()

valid_categories["category_id"] = valid_categories["category_id"].astype(str).str.strip()
valid_categories["landing_page_name"] = valid_categories["landing_page_name"].astype(str).str.strip()
valid_categories["gender"] = valid_categories["gender"].astype(str).str.strip()
valid_categories["product"] = valid_categories["product"].astype(str).str.strip()

if len(valid_categories) > 10:
    st.error("Please use a maximum of 10 category IDs per batch.")

brand = st.text_input("Brand", value="HUGO BOSS")

is_sale = st.checkbox("Sale page")

discount = ""
if is_sale:
    discount = st.text_input("Discount message", placeholder="e.g. up to 40% off")

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
    create_table = st.button("Create table")

    if create_table and len(valid_categories) <= 10:
        for _, cat in valid_categories.iterrows():
            rows.append({
                "category_id": cat["category_id"],
                "landing_page_name": cat["landing_page_name"],
                "gender": cat["gender"],
                "product": cat["product"],
                "sfcc_level": "default",
                "xml_lang": "",
                "action": "update",
                "page_description": "",
                "page_title": "",
                "page_url": "",
                "headline": ""
            })

elif target_level == "language":
    selected_languages = st.multiselect("Languages to update", LANGUAGES, default=["en"])

    if len(selected_languages) > 3:
        st.warning("This is a large batch. For easier QA, consider using up to 3 languages at a time.")

    create_table = st.button("Create table")

    if create_table and len(valid_categories) <= 10:
        for _, cat in valid_categories.iterrows():
            for lang in selected_languages:
                rows.append({
                    "category_id": cat["category_id"],
                    "landing_page_name": cat["landing_page_name"],
                    "gender": cat["gender"],
                    "product": cat["product"],
                    "sfcc_level": "language",
                    "xml_lang": lang,
                    "action": "update",
                    "page_description": "",
                    "page_title": "",
                    "page_url": "",
                    "headline": ""
                })

elif target_level == "country-language":
    selected_country_languages = st.multiselect(
        "Country-language locales to update",
        COUNTRY_LANGUAGES,
        default=["en-GB"]
    )

    if len(selected_country_languages) > 3:
        st.warning("This is a large batch. For easier QA, consider using up to 3 locales at a time.")

    create_table = st.button("Create table")

    if create_table and len(valid_categories) <= 10:
        for _, cat in valid_categories.iterrows():
            for locale in selected_country_languages:
                rows.append({
                    "category_id": cat["category_id"],
                    "landing_page_name": cat["landing_page_name"],
                    "gender": cat["gender"],
                    "product": cat["product"],
                    "sfcc_level": "country-language",
                    "xml_lang": locale,
                    "action": "update",
                    "page_description": "",
                    "page_title": "",
                    "page_url": "",
                    "headline": ""
                })

else:
    selected_languages = st.multiselect("Languages to update", LANGUAGES, default=["en"])

    selected_country_languages = st.multiselect(
        "Country-language overrides to clear",
        COUNTRY_LANGUAGES,
        default=["en-GB"]
    )

    if len(selected_languages) > 3:
        st.warning("This is a large batch. For easier QA, consider using up to 3 languages at a time.")

    create_table = st.button("Create table")

    if create_table and len(valid_categories) <= 10:
        for _, cat in valid_categories.iterrows():
            for lang in selected_languages:
                rows.append({
                    "category_id": cat["category_id"],
                    "landing_page_name": cat["landing_page_name"],
                    "gender": cat["gender"],
                    "product": cat["product"],
                    "sfcc_level": "language",
                    "xml_lang": lang,
                    "action": "update",
                    "page_description": "",
                    "page_title": "",
                    "page_url": "",
                    "headline": ""
                })

            for locale in selected_country_languages:
                rows.append({
                    "category_id": cat["category_id"],
                    "landing_page_name": cat["landing_page_name"],
                    "gender": cat["gender"],
                    "product": cat["product"],
                    "sfcc_level": "country-language",
                    "xml_lang": locale,
                    "action": "clear",
                    "page_description": "",
                    "page_title": "",
                    "page_url": "",
                    "headline": ""
                })

if rows:
    st.session_state.df = pd.DataFrame(rows)

if st.session_state.df is not None:
    df = st.session_state.df

    st.subheader("SEO Copy / XML Preparation Table")

    update_df = df[df["action"] == "update"].copy()

    if target_level == "default":
        update_df["ai_locale"] = "default"
    else:
        update_df["ai_locale"] = update_df["xml_lang"]

    total_ai_rows = len(update_df)

    if total_ai_rows > 30:
        st.warning(f"This will generate {total_ai_rows} AI rows. Consider splitting the batch for easier QA.")

    if st.button("Generate AI SEO Copy"):
        categories_for_prompt = update_df[
            ["category_id", "landing_page_name", "gender", "product", "ai_locale"]
        ].rename(columns={"ai_locale": "locale"})

        categories_csv = categories_for_prompt.to_csv(index=False)

        prompt = f"""
You are an international SEO specialist for a luxury fashion ecommerce brand.

Generate SEO-optimised metadata for every category_id + locale combination in the CSV below.

CATEGORY INPUTS CSV:
{categories_csv}

GLOBAL INPUTS:
Brand: {brand}
Is sale page: {is_sale}
Discount message: {discount}
SEO Brief: {brief}

STRICT TAXONOMY:
1. For non-sale pages:
- page_title must follow: [Localized Premium Gender's Product] | [Brand]
- headline must follow: [Localized Product for Gender]
- page_url must follow: [localized-gender]-[localized-product]

2. For sale pages:
- page_title must follow: [Localized Sale] | [Localized Gender's Product] [Localized Discount] | [Brand]
- headline must follow: [Localized Sale]: [Localized Gender's Product]
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
- keep Japanese and Korean URLs in English

META DESCRIPTION:
- max 155 characters
- commercial and premium tone
- mention the product category
- mention the brand
- if sale page, mention the discount

Return ONLY valid JSON.
Do not wrap the JSON in markdown.
Do not add explanations.

The JSON must be an array of objects.

Each object must contain:
- category_id
- locale
- page_description
- page_title
- page_url
- headline
"""

        try:
            response = model.generate_content(prompt)
            json_text = response.text.strip()
            json_text = json_text.replace("```json", "").replace("```", "").strip()

            ai_data = json.loads(json_text)
            ai_df = pd.DataFrame(ai_data)

            required_columns = [
                "category_id",
                "locale",
                "page_description",
                "page_title",
                "page_url",
                "headline"
            ]

            missing_columns = [col for col in required_columns if col not in ai_df.columns]

            if missing_columns:
                st.error(f"AI output is missing required columns: {missing_columns}")
                st.code(json_text)
            else:
                ai_df["category_id"] = ai_df["category_id"].astype(str)
                ai_df["locale"] = ai_df["locale"].astype(str)

                for index, row in df.iterrows():
                    if row["action"] == "update":
                        locale_key = row["xml_lang"] if row["xml_lang"] else "default"
                        category_key = str(row["category_id"])

                        match = ai_df[
                            (ai_df["category_id"] == category_key) &
                            (ai_df["locale"] == locale_key)
                        ]

                        if not match.empty:
                            df.at[index, "page_description"] = match.iloc[0]["page_description"]
                            df.at[index, "page_title"] = match.iloc[0]["page_title"]
                            df.at[index, "page_url"] = match.iloc[0]["page_url"]
                            df.at[index, "headline"] = match.iloc[0]["headline"]

                st.session_state.df = df
                st.success("AI SEO copy generated.")

        except Exception as e:
            st.error("The AI output could not be processed. Please try again or reduce the batch size.")
            st.exception(e)

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

        xml += '    <page-attributes>\n'

        for _, row in group.iterrows():
            lang_attr = f' xml:lang="{row["xml_lang"]}"' if row["xml_lang"] else ""
            value = "" if row["action"] == "clear" else escape_xml(row["page_description"])
            xml += f'      <page-description{lang_attr}>{value}</page-description>\n'

        for _, row in group.iterrows():
            lang_attr = f' xml:lang="{row["xml_lang"]}"' if row["xml_lang"] else ""
            value = "" if row["action"] == "clear" else escape_xml(row["page_title"])
            xml += f'      <page-title{lang_attr}>{value}</page-title>\n'

        for _, row in group.iterrows():
            lang_attr = f' xml:lang="{row["xml_lang"]}"' if row["xml_lang"] else ""
            value = "" if row["action"] == "clear" else escape_xml(row["page_url"])
            xml += f'      <page-url{lang_attr}>{value}</page-url>\n'

        xml += '    </page-attributes>\n'

        xml += '    <custom-attributes>\n'

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