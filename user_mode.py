import streamlit as st
from knowledge_base import KnowledgeBase
from inference import InferenceEngine


def run_user_mode():
    st.title("🎸 Диагностика и ремонт электрогитары")
    st.write("Введите диагностические параметры вашей гитары:")

    kb = KnowledgeBase()
    engine = InferenceEngine(kb)

    properties = kb.get_properties()

    input_data = {}

    # Создаём форму ввода
    with st.form("diagnostic_form"):
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get("type")
            unit = prop_info.get("unit", "")

            if prop_type == "float":
                range_vals = prop_info.get("range", [0, 100])
                value = st.number_input(
                    f"{prop_name} ({unit})",
                    min_value=float(range_vals[0]),
                    max_value=float(range_vals[1]),
                    value=float(range_vals[0]),
                    step=0.1
                )
                input_data[prop_name] = value

            elif prop_type == "bool":
                value = st.selectbox(
                    f"{prop_name}",
                    options=[0, 1],
                    format_func=lambda x: "норма (1)" if x == 1 else "неисправен (0)"
                )
                input_data[prop_name] = value

        submitted = st.form_submit_button("🔍 Поставить диагноз")

    if submitted:
        with st.spinner("Анализируем параметры..."):
            diagnosis, repair, actions = engine.diagnose(input_data)

        st.divider()

        # Результат диагностики
        if diagnosis == "неизвестно":
            st.error("❌ Не удалось определить диагноз. Обратитесь к мастеру.")
        else:
            st.success(f"**Диагноз:** {diagnosis}")

            # Информация о ремонте
            repairs = kb.get_repairs()
            if repair in repairs:
                st.subheader("🔧 Назначен ремонт")
                st.info(repairs[repair].get("description", repair))

            # Последовательность действий
            if actions:
                st.subheader("📋 Последовательность действий для ремонта")
                for i, action in enumerate(actions, 1):
                    desc = engine.get_action_description(action)
                    st.write(f"{i}. **{action}**")
                    st.caption(f"   {desc}")
            else:
                if diagnosis == "исправна":
                    st.success("✅ Гитара исправна! Ремонт не требуется.")
                else:
                    st.warning("⚠️ Действия для ремонта не найдены.")