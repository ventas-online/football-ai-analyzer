import base64
import io
import json
import os
import re
import uuid
from pathlib import Path

import qrcode
import streamlit as st

st.set_page_config(page_title="Catálogo Fácil", page_icon="🛍️", layout="wide")

st.title("🛍️ Catálogo Fácil")
st.caption("Crea un catálogo de productos, genera descripciones con IA y prepara un QR para compartirlo.")

# Session state
if "products" not in st.session_state:
    st.session_state.products = []
if "catalog_id" not in st.session_state:
    st.session_state.catalog_id = uuid.uuid4().hex[:8]


def ai_description(name, brand, category, features, tone):
    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    if not api_key:
        return None, "Añade OPENAI_API_KEY en Streamlit Secrets para activar la IA."
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = f"""Crea una descripción comercial breve y atractiva en español para un producto.
Nombre: {name}
Marca: {brand or 'No indicada'}
Categoría: {category or 'No indicada'}
Características: {features or 'No indicadas'}
Tono: {tone}
No inventes características que no estén proporcionadas. Devuelve solo la descripción, sin título ni comillas."""
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        return response.output_text.strip(), None
    except Exception as exc:
        return None, f"No se pudo generar la descripción: {exc}"


def make_qr(url):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image()
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


with st.sidebar:
    st.header("⚙️ Mi catálogo")
    business = st.text_input("Nombre del negocio", "Mi tienda")
    catalog_url = st.text_input("URL pública del catálogo", "")
    st.caption("La URL se usa para generar el QR. En la versión pública será la dirección de tu catálogo.")

st.subheader("1. Añade productos")
with st.form("product_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Nombre del producto *")
        brand = st.text_input("Marca")
        category = st.text_input("Categoría")
        price = st.number_input("Precio de venta", min_value=0.0, step=0.01)
    with col2:
        image_url = st.text_input("URL de la imagen (opcional)")
        features = st.text_area("Características / información del producto")
        description = st.text_area("Descripción (opcional)")
        tone = st.selectbox("Tono para IA", ["profesional", "elegante", "cercano", "directo"])
    add = st.form_submit_button("➕ Añadir producto", type="primary")

if add:
    if not name.strip():
        st.error("Escribe el nombre del producto.")
    else:
        if not description.strip():
            with st.spinner("🤖 Generando descripción con IA..."):
                generated, error = ai_description(name, brand, category, features, tone)
            if generated:
                description = generated
            elif error:
                st.warning(error)
        st.session_state.products.append({
            "id": uuid.uuid4().hex[:10],
            "name": name.strip(),
            "brand": brand.strip(),
            "category": category.strip(),
            "price": float(price),
            "image_url": image_url.strip(),
            "features": features.strip(),
            "description": description.strip(),
        })
        st.success(f"{name} añadido al catálogo.")

st.subheader("2. Productos")
if not st.session_state.products:
    st.info("Todavía no tienes productos. Añade el primero arriba.")
else:
    for product in st.session_state.products:
        with st.container(border=True):
            cols = st.columns([1, 3, 1, 1])
            with cols[0]:
                if product["image_url"]:
                    st.image(product["image_url"], width=100)
                else:
                    st.write("📦")
            with cols[1]:
                st.markdown(f"**{product['name']}**")
                if product["brand"]:
                    st.caption(product["brand"])
                st.write(product["description"] or "Sin descripción")
            with cols[2]:
                st.metric("Precio", f"${product['price']:.2f}")
            with cols[3]:
                if st.button("🗑️", key=f"delete_{product['id']}"):
                    st.session_state.products = [p for p in st.session_state.products if p["id"] != product["id"]]
                    st.rerun()

st.subheader("3. Compartir catálogo")
if st.session_state.products:
    st.metric("Productos", len(st.session_state.products))
    if catalog_url.strip():
        qr_bytes = make_qr(catalog_url.strip())
        st.image(qr_bytes, width=220, caption="QR de tu catálogo")
        st.download_button("⬇️ Descargar QR", qr_bytes, "catalogo-qr.png", "image/png")
    else:
        st.info("Escribe la URL pública del catálogo en la barra lateral para generar el QR.")

    export = json.dumps({"business": business, "catalog_id": st.session_state.catalog_id, "products": st.session_state.products}, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button("⬇️ Descargar productos (JSON)", export, "catalogo-productos.json", "application/json")

st.divider()
st.caption("La IA solo redacta con la información proporcionada y puede cometer errores. Revisa cada descripción antes de publicarla.")
