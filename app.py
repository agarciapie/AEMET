import streamlit as st
import datetime

def main():
    st.title("Aplicació de l'Hora")

    # Inicialitzar l'hora actual
    now = datetime.datetime.now()
    hora = now.hour
    minuts = now.minute
    segons = now.second

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("+ Hora"):
            hora = (hora + 1) % 24
        if st.button("- Hora"):
            hora = (hora - 1) % 24
    with col2:
        if st.button("+ Minuts"):
            minuts = (minuts + 1) % 60
        if st.button("- Minuts"):
            minuts = (minuts - 1) % 60
    with col3:
        if st.button("+ Segons"):
            segons = (segons + 1) % 60
        if st.button("- Segons"):
            segons = (segons - 1) % 60

    # Mostrar l'hora actualitzada
    hora_actualitzada = now.replace(hour=hora, minute=minuts, second=segons, microsecond=0)
    st.markdown(f"<h1 style='text-align: center;'>{hora_actualitzada.strftime('%H:%M:%S')}</h1>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
