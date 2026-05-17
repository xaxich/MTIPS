import streamlit as st
from knowledge_base import KnowledgeBase


def run_expert_mode():
    st.title("👨‍🔧 Редактор базы знаний")
    st.write("Режим эксперта: добавление, изменение и удаление знаний")

    kb = KnowledgeBase()

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Диагнозы", "🔧 Ремонты", "📊 Свойства", "🏷 Группы диагнозов"])

    with tab1:
        st.header("Управление диагнозами")

        diagnoses = kb.get_diagnoses()
        properties = kb.get_properties()
        repairs = kb.get_repairs()

        # Просмотр существующих
        with st.expander("📋 Существующие диагнозы", expanded=False):
            for name, info in diagnoses.items():
                st.subheader(name)
                st.write("**Условия:**")
                for prop, condition in info.get("conditions", {}).items():
                    if isinstance(condition, dict):
                        cond_str = f"{condition.get('min', '-∞')} - {condition.get('max', '∞')}"
                        if not condition.get("min_inclusive", True):
                            cond_str = f"({cond_str}"
                        if not condition.get("max_inclusive", True):
                            cond_str = f"{cond_str})"
                        st.write(f"  - {prop}: ∈ {cond_str}")
                    elif isinstance(condition, list):
                        st.write(f"  - {prop}: ∈ [{condition[0]}, {condition[1]}]")
                    else:
                        st.write(f"  - {prop}: = {condition}")
                st.write(f"**Ремонт:** {info.get('repair')}")
                st.divider()

        # Добавление нового диагноза
        with st.expander("➕ Добавить диагноз", expanded=False):
            new_name = st.text_input("Название диагноза", key="new_diag_name")

            conditions = {}

            st.write("**Условия диагностики:**")

            # Выбор свойств и задание условий
            for prop_name, prop_info in properties.items():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    use = st.checkbox(f"Использовать {prop_name}", key=f"use_{prop_name}")
                if use:
                    prop_type = prop_info.get("type")
                    if prop_type == "float":
                        with col2:
                            min_val = st.number_input(f"min", value=0.0, key=f"min_{prop_name}", step=0.1)
                        with col3:
                            max_val = st.number_input(f"max", value=100.0, key=f"max_{prop_name}", step=0.1)
                        with col4:
                            min_inc = st.checkbox("вкл. min", value=True, key=f"min_inc_{prop_name}")
                            max_inc = st.checkbox("вкл. max", value=True, key=f"max_inc_{prop_name}")
                        conditions[prop_name] = {
                            "min": min_val,
                            "max": max_val,
                            "min_inclusive": min_inc,
                            "max_inclusive": max_inc
                        }
                    elif prop_type == "bool":
                        with col2:
                            bool_val = st.selectbox("значение", [0, 1], key=f"bool_{prop_name}")
                        conditions[prop_name] = bool_val

            repair_select = st.selectbox("Ремонт", list(repairs.keys()) if repairs else ["Нет ремонтов"])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Сохранить диагноз", key="save_diagnosis"):
                    if new_name and conditions:
                        if new_name in diagnoses:
                            st.warning(f"Диагноз '{new_name}' уже существует!")
                        else:
                            kb.add_diagnosis(new_name, conditions, repair_select)
                            st.success(f"Диагноз '{new_name}' добавлен!")
                            st.rerun()
                    else:
                        st.error("Введите название диагноза и хотя бы одно условие!")

    with tab2:
        st.header("Управление ремонтами")

        repairs = kb.get_repairs()

        for repair_name, repair_info in repairs.items():
            with st.expander(f"🔧 {repair_name}", expanded=False):
                st.write(f"**Описание:** {repair_info.get('description', '')}")

                actions = repair_info.get("actions", [])
                actions_str = ", ".join(actions)
                new_actions = st.text_input(
                    "Действия (через запятую)",
                    value=actions_str,
                    key=f"actions_{repair_name}"
                )

                if st.button(f"Обновить", key=f"update_{repair_name}"):
                    new_actions_list = [a.strip() for a in new_actions.split(",") if a.strip()]
                    kb.update_repair_actions(repair_name, new_actions_list)
                    st.success(f"Ремонт '{repair_name}' обновлён!")
                    st.rerun()

    with tab3:
        st.header("Просмотр свойств")

        properties = kb.get_properties()

        st.json(properties)

        st.info("Для добавления/изменения свойств отредактируйте файл knowledge_base.json")

    with tab4:
        st.header("Группы диагнозов")

        groups = kb.get_diagnosis_groups()

        for group_name, group_info in groups.items():
            with st.expander(f"📁 {group_info.get('name', group_name)}", expanded=False):
                st.write(f"**Члены группы:**")
                for member in group_info.get("members", []):
                    st.write(f"- {member}")

        st.info(
            "Группы используются для фильтрации отклонённых гипотез — показываются только диагнозы из той же группы")