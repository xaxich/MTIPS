class InferenceEngine:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base

    def check_condition(self, value, condition):
        """
        Проверяет, удовлетворяет ли значение условию
        Поддерживает:
        - Простые числа: value == condition
        - Списки [min, max]: min <= value <= max
        - Словари с min/max и флагами включения границ
        """
        if isinstance(condition, (int, float)):
            return value == condition
        elif isinstance(condition, list) and len(condition) == 2:
            # Закрытый интервал
            return condition[0] <= value <= condition[1]
        elif isinstance(condition, dict):
            # Полуоткрытый интервал
            min_val = condition.get("min")
            max_val = condition.get("max")
            min_inc = condition.get("min_inclusive", True)
            max_inc = condition.get("max_inclusive", True)

            result = True
            if min_val is not None:
                if min_inc:
                    result = result and (value >= min_val)
                else:
                    result = result and (value > min_val)
            if max_val is not None:
                if max_inc:
                    result = result and (value <= max_val)
                else:
                    result = result and (value < max_val)
            return result
        else:
            return False

    def format_condition(self, condition):
        """Форматирует условие для вывода в тексте объяснения"""
        if isinstance(condition, (int, float)):
            return f"= {condition}"
        elif isinstance(condition, list) and len(condition) == 2:
            return f"[{condition[0]}, {condition[1]}]"
        elif isinstance(condition, dict):
            min_val = condition.get("min")
            max_val = condition.get("max")
            min_inc = condition.get("min_inclusive", True)
            max_inc = condition.get("max_inclusive", True)

            left = "[" if min_inc else "("
            right = "]" if max_inc else ")"

            if min_val is not None and max_val is not None:
                return f"{left}{min_val}, {max_val}{right}"
            elif min_val is not None:
                return f"{left}{min_val}, ∞)"
            else:
                return f"(-∞, {max_val}{right}"
        return str(condition)

    def diagnose(self, input_data):
        """
        Определяет диагноз на основе входных данных
        Возвращает: (диагноз, ремонт, действия, отклонённые_гипотезы)
        """
        diagnoses = self.kb.get_diagnoses()

        best_match = None
        match_score = -1
        all_candidates = []

        # Первый проход: сбор всех кандидатов
        for diagnosis_name, diagnosis_info in diagnoses.items():
            conditions = diagnosis_info.get("conditions", {})
            matched = True
            matched_properties = 0
            total_checked = 0
            missing_properties = []

            for prop, condition in conditions.items():
                if prop in input_data:
                    total_checked += 1
                    if self.check_condition(input_data[prop], condition):
                        matched_properties += 1
                    else:
                        matched = False
                else:
                    missing_properties.append(prop)

            # Если все проверенные свойства подошли, диагноз — кандидат
            if total_checked > 0 and matched:
                # Приоритет: больше совпавших свойств, меньше пропущенных
                score = matched_properties * 2 - len(missing_properties)
                all_candidates.append({
                    "name": diagnosis_name,
                    "score": score,
                    "matched_properties": matched_properties,
                    "missing_properties": missing_properties,
                    "conditions": conditions
                })
                if score > match_score:
                    match_score = score
                    best_match = diagnosis_name

        # Определяем отклонённые гипотезы
        rejected = self.get_rejected_hypotheses(input_data, best_match, all_candidates)

        if best_match:
            repair_name = diagnoses[best_match].get("repair")
            repairs = self.kb.get_repairs()

            if repair_name in repairs:
                actions = repairs[repair_name].get("actions", [])
                return best_match, repair_name, actions, rejected

        # Если диагноз не найден, возвращаем все отклонённые гипотезы как объяснение
        return "неизвестно", "диагностика_невозможна", [], rejected

    def get_rejected_hypotheses(self, input_data, selected_diagnosis, all_candidates):
        """
        Возвращает список отклонённых гипотез с причинами
        Отклоняются только диагнозы из той же группы, что и выбранный
        """
        if selected_diagnosis is None:
            # Если диагноз не выбран, показываем все рассмотренные
            rejected = []
            for candidate in all_candidates:
                reasons = []
                conditions = candidate.get("conditions", {})
                for prop, condition in conditions.items():
                    if prop in input_data:
                        if not self.check_condition(input_data[prop], condition):
                            reasons.append({
                                "property": prop,
                                "value": input_data[prop],
                                "expected": self.format_condition(condition)
                            })
                    else:
                        reasons.append({
                            "property": prop,
                            "value": "не измерен",
                            "expected": self.format_condition(condition)
                        })
                if reasons:
                    rejected.append({
                        "diagnosis": candidate["name"],
                        "reasons": reasons
                    })
            return rejected

        # Определяем группу выбранного диагноза
        selected_group = self.kb.get_diagnosis_group_for(selected_diagnosis)

        rejected = []

        for candidate in all_candidates:
            if candidate["name"] == selected_diagnosis:
                continue

            # Проверяем группу кандидата
            candidate_group = self.kb.get_diagnosis_group_for(candidate["name"])

            # Показываем только гипотезы из той же группы
            if selected_group and candidate_group and candidate_group != selected_group:
                continue

            # Собираем причины отклонения
            reasons = []
            conditions = candidate.get("conditions", {})
            for prop, condition in conditions.items():
                if prop in input_data:
                    if not self.check_condition(input_data[prop], condition):
                        reasons.append({
                            "property": prop,
                            "value": input_data[prop],
                            "expected": self.format_condition(condition)
                        })
                else:
                    reasons.append({
                        "property": prop,
                        "value": "не измерен",
                        "expected": self.format_condition(condition)
                    })

            if reasons:
                rejected.append({
                    "diagnosis": candidate["name"],
                    "reasons": reasons,
                    "matched_properties": candidate.get("matched_properties", 0)
                })

        # Сортируем по количеству совпавших свойств (больше совпадений — выше в списке)
        rejected.sort(key=lambda x: x.get("matched_properties", 0), reverse=True)

        return rejected

    def get_action_description(self, action_name):
        """Возвращает описание действия"""
        actions_desc = self.kb.get_actions_description()
        return actions_desc.get(action_name, action_name)