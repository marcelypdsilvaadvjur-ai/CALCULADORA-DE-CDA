
import fitz  # PyMuPDF
import re
import streamlit as st

# Função para extrair os dados do extrato de débitos
def extrair_dados_extrato(pdf_path):
    with fitz.open(pdf_path) as doc:
        texto = "
".join(page.get_text() for page in doc)
    linhas = texto.split("
")
    dados = []
    for i, linha in enumerate(linhas):
        if re.search(r'\d{11}-\d', linha):  # Padrão de Docto.
            partes = linha.split()
            docto = partes[0]
            # Procurar valor atualizado na mesma linha ou próxima
            for j in range(i, min(i+5, len(linhas))):
                match = re.search(r'([\d\.]+,\d{2})$', linhas[j])
                if match:
                    valor = match.group(1).replace('.', '').replace(',', '.')
                    dados.append((docto, float(valor)))
                    break
    return dados

st.set_page_config(page_title="Calculadora de CDAs", layout="centered")
st.title("📄 Calculadora de CDAs e Honorários")

extrato_file = st.file_uploader("Envie o Extrato de Débitos (PDF)", type="pdf")
peticao_file = st.file_uploader("Envie a Petição Inicial (PDF)", type="pdf")

honorarios_percentual = st.number_input("Percentual de Honorários (%)", min_value=0.0, max_value=100.0, value=10.0)

if extrato_file:
    with open("extrato_temp.pdf", "wb") as f:
        f.write(extrato_file.read())
    dados_extrato = extrair_dados_extrato("extrato_temp.pdf")

    st.subheader("Selecione as CDAs para cálculo")
    doctos_selecionados = st.multiselect(
        "Docto. disponíveis:",
        options=[f"{docto} - R$ {valor:,.2f}" for docto, valor in dados_extrato]
    )

    valores_selecionados = [valor for docto, valor in dados_extrato if any(docto in d for d in doctos_selecionados)]
    total_cdas = sum(valores_selecionados)
    honorarios = total_cdas * (honorarios_percentual / 100)

    st.markdown("### Resultado do Cálculo")
    st.write(f"**Total das CDAs selecionadas:** R$ {total_cdas:,.2f}")
    st.write(f"**Honorários ({honorarios_percentual}%):** R$ {honorarios:,.2f}")
