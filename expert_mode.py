import streamlit as st
from knowledge_base import KnowledgeBase


def run_expert_mode():
    st.title("👨‍🔧 Редактор базы знаний")
    st.write("Режим эксперта: добавление, изменение и удаление знаний")

    kb = KnowledgeBase()

    tab1, tab2, tab3 = st.tabs(["📋 Диагнозы", "🔧 Ремонты", "📊 Свойства"])

    with tab1:
        st.header("Управление диагнозами")

        diagnoses = kb.get_diagnoses()

        # Просмотр существующих
        with st.expander("Существующие диагнозы"):
            for name, info in diagnoses.items():
                st.subheader(name)
                st.json(info.get("conditions", {}))
                st.write(f"Ремонт: {info.get('repair')}")
                st.divider()

        # Добавление нового диагноза
        with st.expander("➕ Добавить диагноз"):
            new_name = st.text_input("Название диагноза")

            # Выбор свойств
            properties = kb.get_properties()
            conditions = {}

            st.write("Условия диагностики:")
            for prop_name in properties.keys():
                col1, col2 = st.columns(2)
                with col1:
                    use = st.checkbox(f"Использовать {prop_name}", key=f"use_{prop_name}")
                if use:
                    with col2:
                        min_val = st.number_input(f"min {prop_name}", value=0.0, key=f"min_{prop_name}")
                        max_val = st.number_input(f"max {prop_name}", value=100.0, key=f"max_{prop_name}")
                        conditions[prop_name] = [min_val, max_val]

            repairs = kb.get_repairs()
            repair_select = st.selectbox("Ремонт", list(repairs.keys()))

            if st.button("Сохранить диагноз"):
                if new_name and conditions:
                    kb.add_diagnosis(new_name, conditions, repair_select)
                    st.success(f"Диагноз '{new_name}' добавлен!")
                    st.rerun()

    with tab2:
        st.header("Управление ремонтами")

        repairs = kb.get_repairs()

        for repair_name, repair_info in repairs.items():
            with st.expander(repair_name):
                st.write(f"Описание: {repair_info.get('description', '')}")

                actions = repair_info.get("actions", [])
                actions_str = ", ".join(actions)
                new_actions = st.text_input(
                    f"Действия для {repair_name} (через запятую)",
                    value=actions_str,
                    key=f"actions_{repair_name}"
                )

                if st.button(f"Обновить {repair_name}", key=f"update_{repair_name}"):
                    new_actions_list = [a.strip() for a in new_actions.split(",") if a.strip()]
                    kb.update_repair_actions(repair_name, new_actions_list)
                    st.success(f"Ремонт '{repair_name}' обновлён!")
                    st.rerun()

    with tab3:
        st.header("Просмотр свойств")

        properties = kb.get_properties()
        st.json(properties)

        st.info("Для добавления/изменения свойств отредактируйте файл knowledge_base.json")