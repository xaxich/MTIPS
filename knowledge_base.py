import json
import os


class KnowledgeBase:
    def __init__(self, filename="knowledge_base.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"База знаний {self.filename} не найдена")

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_properties(self):
        return self.data.get("properties", {})

    def get_diagnoses(self):
        return self.data.get("diagnoses", {})

    def get_repairs(self):
        return self.data.get("repairs", {})

    def get_actions_description(self):
        return self.data.get("actions_description", {})

    def add_diagnosis(self, name, conditions, repair):
        self.data["diagnoses"][name] = {
            "conditions": conditions,
            "repair": repair
        }
        self.save()

    def delete_diagnosis(self, name):
        if name in self.data["diagnoses"]:
            del self.data["diagnoses"][name]
            self.save()

    def update_repair_actions(self, repair_name, actions):
        if repair_name in self.data["repairs"]:
            self.data["repairs"][repair_name]["actions"] = actions
            self.save()