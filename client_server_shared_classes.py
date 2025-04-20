class Test:
    def __init__(self, uuid, name, desc):
        self.uuid = uuid
        self.name = name
        self.desc = desc

class Question:
    def __init__(self, uuid, test_uuid, text):
        self.uuid      = uuid
        self.test_uuid = test_uuid
        self.text      = text

class Answer:
    def __init__(self, uuid, question_uuid, text, is_correct):
        self.uuid          = uuid
        self.question_uuid = question_uuid
        self.text          = text
        self.is_correct    = is_correct

class Result:
    def __init__(self, uuid, user_uuid, test_uuid, date, best_attempt, last_attempt):
        self.uuid = uuid
        self.user_uuid = user_uuid
        self.test_uuid = test_uuid
        self.date = date
        self.best_attempt = best_attempt
        self.last_attempt = last_attempt