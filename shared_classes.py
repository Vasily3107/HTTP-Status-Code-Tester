from uuid import UUID

class Test:
    def __init__(self, uuid:UUID, name:str, description:str):
        self.uuid = uuid
        self.name = name
        self.desc = description

    def __repr__(self):
        return self.name

    def __iter__(self):
        yield self.uuid
        yield self.name
        yield self.desc

    def __eq__(self, other):
        return self.uuid == other.uuid

class Question:
    def __init__(self, uuid:UUID, test_uuid:UUID, text:str):
        self.uuid      = uuid
        self.test_uuid = test_uuid
        self.text      = text

    def __repr__(self):
        return f'{self.text} {self.uuid}'

    def __iter__(self):
        yield self.uuid
        yield self.test_uuid
        yield self.text

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __hash__(self):
        return hash(self.uuid)

class Answer:
    def __init__(self, uuid:UUID, question_uuid:UUID, text:str, is_correct:bool):
        self.uuid          = uuid
        self.question_uuid = question_uuid
        self.text          = text
        self.is_correct    = is_correct

    def __repr__(self):
        return f'{self.text} {self.is_correct} {self.question_uuid}'

    def __iter__(self):
        yield self.uuid
        yield self.question_uuid
        yield self.text
        yield self.is_correct

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __hash__(self):
        return hash(self.uuid)