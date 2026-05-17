import streamlit as st
from knowledge_base import KnowledgeBase
from inference import InferenceEngine


def run_user_mode():
    st.title("🎸 Диагностика и ремонт электрогитары")
    st.write("Введите диагностические параметры вашей гитары:")

    kb = KnowledgeBase()
    engine = InferenceEngine(kb)

    properties = kb.get_properties()

    # Инициализация состояния для хранения введённых данных
    if "input_data" not in st.session_state:
        st.session_state.input_data = {}

    # Создаём форму ввода
    with st.form("diagnostic_form"):
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get("type")
            unit = prop_info.get("unit", "")
            default_value = prop_info.get("default", 0)

            if prop_type == "float":
                range_vals = prop_info.get("range", [0, 100])
                value = st.number_input(
                    f"{prop_name} ({unit})",
                    min_value=float(range_vals[0]),
                    max_value=float(range_vals[1]),
                    value=float(st.session_state.input_data.get(prop_name, range_vals[0])),
                    step=0.1,
                    key=f"input_{prop_name}"
                )
                st.session_state.input_data[prop_name] = value

            elif prop_type == "bool":
                current_val = st.session_state.input_data.get(prop_name, 1)
                value = st.selectbox(
                    f"{prop_name}",
                    options=[1, 0],
                    index=0 if current_val == 1 else 1,
                    format_func=lambda x: "норма (1)" if x == 1 else "неисправен (0)",
                    key=f"select_{prop_name}"
                )
                st.session_state.input_data[prop_name] = value

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("🔍 Поставить диагноз", use_container_width=True)
        with col2:
            clear = st.form_submit_button("🗑 Очистить форму", use_container_width=True)

        if clear:
            st.session_state.input_data = {}
            st.rerun()

    if submitted:
        with st.spinner("Анализируем параметры..."):
            diagnosis, repair, actions, rejected = engine.diagnose(st.session_state.input_data)

        st.divider()

        # ===== БЛОК 1: ИТОГОВЫЙ ДИАГНОЗ =====
        st.header("📋 РЕЗУЛЬТАТ ДИАГНОСТИКИ")

        if diagnosis == "неизвестно":
            st.error("❌ Не удалось определить диагноз.")

            if rejected:
                st.subheader("Возможные причины:")
                for item in rejected[:3]:  # Показываем первые 3
                    st.write(f"- {item['diagnosis']}:")
                    for reason in item['reasons'][:2]:
                        st.write(f"  • {reason['property']} = {reason['value']} (ожидалось {reason['expected']})")
        else:
            # Отображаем диагноз цветным баннером
            if diagnosis == "исправна":
                st.success(f"**Диагноз:** {diagnosis}")
            else:
                st.warning(f"**Диагноз:** {diagnosis}")

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

        st.divider()

        # ===== БЛОК 2: ОТКЛОНЁННЫЕ ГИПОТЕЗЫ =====
        if rejected and diagnosis != "неизвестно":
            st.header("🔍 ПРОВЕРЕННЫЕ АЛЬТЕРНАТИВЫ")
            st.caption("Ниже перечислены диагнозы, которые были рассмотрены, но не подтвердились:")

            for item in rejected:
                with st.expander(f"❌ {item['diagnosis']}"):
                    st.write("**Причины отклонения:**")
                    for reason in item['reasons']:
                        st.write(f"- **{reason['property']}** = {reason['value']} (ожидалось {reason['expected']})")

        # ===== БЛОК 3: ОБОСНОВАНИЕ ВЫБРАННОГО ДИАГНОЗА =====
        if diagnosis not in ["неизвестно", "исправна"]:
            st.divider()
            st.header("💡 Почему выбран этот диагноз?")

            diagnoses = kb.get_diagnoses()
            if diagnosis in diagnoses:
                conditions = diagnoses[diagnosis].get("conditions", {})
                st.write("Следующие признаки соответствуют диагнозу:")
                for prop, condition in conditions.items():
                    if prop in st.session_state.input_data:
                        expected = engine.format_condition(condition)
                        st.write(f"- **{prop}** = {st.session_state.input_data[prop]} ∈ {expected}")

        # ===== БЛОК 4: ЭКСПОРТ РЕЗУЛЬТАТА =====
        if diagnosis != "неизвестно":
            st.divider()

            # Формируем текст для экспорта
            result_text = f"""
ДИАГНОСТИКА ЭЛЕКТРОГИТАРЫ
========================
Дата: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ВХОДНЫЕ ДАННЫЕ:
{chr(10).join([f"  {k}: {v}" for k, v in st.session_state.input_data.items()])}

РЕЗУЛЬТАТ:
  Диагноз: {diagnosis}
  Ремонт: {repair}

ДЕЙСТВИЯ:
{chr(10).join([f"  {i + 1}. {a}" for i, a in enumerate(actions)]) if actions else "  Ремонт не требуется"}

ОТКЛОНЁННЫЕ ГИПОТЕЗЫ:
{chr(10).join([f"  - {item['diagnosis']}: " + "; ".join([f"{r['property']}={r['value']} (ожидалось {r['expected']})" for r in item['reasons']]) for item in rejected[:5]]) if rejected else "  Нет"}
"""

            st.download_button(
                label="📥 Сохранить результат диагностики",
                data=result_text,
                file_name=f"diagnosis_{diagnosis}_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )