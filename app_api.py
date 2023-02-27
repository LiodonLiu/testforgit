import streamlit as st
from location import locate
from PIL import Image

input_text = st.text_input('input text:', 'A sentence of story')

locate(input_text)

image = Image.open('final_canvas.jpg')
st.image(image, caption='final_canvas')