class InferenceEngine:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base

    def check_condition(self, value, condition):
        """Проверяет, удовлетворяет ли значение условию"""
        if isinstance(condition, list):
            if len(condition) == 2:
                return condition[0] <= value <= condition[1]
            else:
                return False
        elif isinstance(condition, (int, float)):
            return value == condition
        elif isinstance(condition, bool):
            return value == condition
        else:
            return False

    def diagnose(self, input_data):
        """
        Определяет диагноз на основе входных данных
        input_data: dict {имя_свойства: значение}
        Возвращает: диагноз, ремонт, действия
        """
        diagnoses = self.kb.get_diagnoses()

        best_match = None
        match_count = 0

        for diagnosis_name, diagnosis_info in diagnoses.items():
            conditions = diagnosis_info.get("conditions", {})
            matched = True
            matched_properties = 0
            total_properties = len(conditions)

            for prop, condition in conditions.items():
                if prop in input_data:
                    if not self.check_condition(input_data[prop], condition):
                        matched = False
                        break
                    matched_properties += 1
                else:
                    # Свойство не указано — не считаем за ошибку
                    matched_properties += 0

            if matched and total_properties > 0:
                # Приоритет у диагноза с большим количеством совпавших свойств
                if matched_properties > match_count:
                    match_count = matched_properties
                    best_match = diagnosis_name

        if best_match:
            repair_name = diagnoses[best_match].get("repair")
            repairs = self.kb.get_repairs()

            if repair_name in repairs:
                actions = repairs[repair_name].get("actions", [])
                return best_match, repair_name, actions

        return "неизвестно", "диагностика_невозможна", []

    def get_action_description(self, action_name):
        """Возвращает описание действия"""
        actions_desc = self.kb.get_actions_description()
        return actions_desc.get(action_name, action_name)