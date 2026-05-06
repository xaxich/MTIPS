import streamlit as st
from user_mode import run_user_mode
from expert_mode import run_expert_mode


def main():
    st.set_page_config(
        page_title="Экспертная система по ремонту электрогитар",
        page_icon="🎸",
        layout="wide"
    )

    st.sidebar.title("🎸 Режим работы")

    mode = st.sidebar.radio(
        "Выберите режим:",
        ["🔧 Пользователь (диагностика)", "👨‍🔬 Эксперт (редактирование БЗ)"]
    )

    if mode == "🔧 Пользователь (диагностика)":
        run_user_mode()
    else:
        run_expert_mode()


if __name__ == "__main__":
    main()