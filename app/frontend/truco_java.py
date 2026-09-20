import streamlit as st

def configurar_puente_html():
    """
    Inyecta un script de JavaScript limpio para interceptar los clics de tus botones HTML
    y comunicarlos con el estado de Streamlit a través de la URL.
    """
    # 1. Detectar si la URL trae el parámetro de redirección
    if "acc" in st.query_params:
        accion = st.query_params["acc"]
        if accion == "cliente":
            st.session_state.menu_acceso = "Acceso Cliente"
        elif accion == "propietario":
            st.session_state.menu_acceso = "Acceso Propietario"
        
        # Limpiamos los parámetros y recargamos para aplicar el cambio de vista
        st.query_params.clear()
        st.rerun()

    # 2. Inyectar script corregido para capturar los clics de tus clases HTML
    st.markdown("""
        <script>
            const observer = new MutationObserver(() => {
                const btnCliente = document.querySelector('.btn-comensales');
                const btnPropietario = document.querySelector('.btn-propietarios');

                if (btnCliente && !btnCliente.dataset.linked) {
                    btnCliente.dataset.linked = "true";
                    btnCliente.addEventListener('click', (e) => {
                        e.preventDefault();
                        window.location.search = "?acc=cliente";
                    });
                }

                if (btnPropietario && !btnPropietario.dataset.linked) {
                    btnPropietario.dataset.linked = "true";
                    btnPropietario.addEventListener('click', (e) => {
                        e.preventDefault();
                        window.location.search = "?acc=propietario";
                    });
                }
            });
            observer.observe(document.body, { childList: true, subtree: true });
        </script>
    """, unsafe_allow_html=True)