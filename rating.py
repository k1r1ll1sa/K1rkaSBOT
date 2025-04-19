"""Модуль для работы с rating.json для отслеживания количества сообщений и наказаний у зрителя"""
import json

class Rating:
    def __init__(self, file_path="rating.json"):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def save_data(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=2)

    def add_msg(self, nickname):
        if nickname not in self.data["rating"]:
            self.data["rating"][nickname] = {"message_count": 0, "timeout_count": 0}
        self.data["rating"][nickname]["message_count"] += 1
        self.save_data()

    def add_timeout(self, nickname):
        if nickname not in self.data["rating"]:
            self.data["rating"][nickname] = {"message_count": 0, "timeout_count": 0}
        self.data["rating"][nickname]["timeout_count"] += 1
        self.save_data()

    def get_msg(self, nickname):
        if nickname not in self.data["rating"]:
            self.data["rating"][nickname] = {"message_count": 0, "timeout_count": 0}
        else:
            return self.data["rating"][nickname]["message_count"]
        self.save_data()

    def get_timeout(self, nickname):
        if nickname not in self.data["rating"]:
            self.data["rating"][nickname] = {"message_count": 0, "timeout_count": 0}
        else:
            return self.data["rating"][nickname]["timeout_count"]
        self.save_data()

    def get_top_users(self, top_n=5):
        users = self.data["rating"].items()
        sorted_users = sorted(
            users,
            key=lambda x: x[1]["message_count"],
            reverse=True
        )
        return sorted_users[:top_n]