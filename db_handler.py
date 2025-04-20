from pyodbc import connect as connect_to_db
server   = 'localhost\SQLEXPRESS'
database = 'test_db'
dsn      =f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

from uuid import UUID, uuid4
from shared_classes import Test, Question, Answer

class DBHandler:
    '''
    Admin Panel database handler
    '''
    current_login = ''

    @staticmethod
    def log_in(login:str, password:str) -> bool:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Administrators WHERE [login] = ? AND [password] = ?', (login, password))
        row = cursor.fetchone()

        cursor.close()
        conn.close()
        return bool(row)

    @classmethod
    def add_test(cls, name:str, description:str, questions:list, answers:list) -> None:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        test_id = uuid4()
        cursor.execute('INSERT INTO Tests VALUES (?, ?, ?)', (test_id, name, description))
        conn.commit()

        questions = ((i.uuid, test_id, i.text) for i in questions)
        cursor.executemany('INSERT INTO Questions VALUES (?, ?, ?)', questions)
        conn.commit()

        answers = ((i.uuid, i.question_uuid, i.text, i.is_correct) for i in answers)
        cursor.executemany('INSERT INTO Answers VALUES (?, ?, ?, ?)', answers)
        conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def save_test_changes( added_questions  : list[Question],
                           edited_questions : list[Question],
                           deleted_questions: list[Question],
                           
                           added_answers  : list[Answer],
                           edited_answers : list[Answer],
                           deleted_answers: list[Answer]
                         ) -> None:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.executemany('DELETE FROM AnswerLogs WHERE question_id = ?',
                           ((i.uuid,) for i in deleted_questions))
        conn.commit()

        cursor.executemany('DELETE FROM Answers WHERE id = ?',
                           ((i.uuid,) for i in deleted_answers))
        conn.commit()

        cursor.executemany('DELETE FROM Questions WHERE id = ?',
                           ((i.uuid,) for i in deleted_questions))
        conn.commit()


        
        cursor.executemany('UPDATE Answers SET [text] = ?, is_correct = ? WHERE id = ?',
                           ((i.text, i.is_correct, i.uuid) for i in edited_answers))

        cursor.executemany('UPDATE Questions SET [text] = ? WHERE id = ?',
                           ((i.text, i.uuid) for i in edited_questions))



        cursor.executemany('INSERT INTO Questions VALUES (?, ?, ?)',
                           ((i.uuid, i.test_uuid, i.text) for i in added_questions))

        cursor.executemany('INSERT INTO Answers VALUES (?, ?, ?, ?)',
                           ((i.uuid, i.question_uuid, i.text, i.is_correct) for i in added_answers))


        conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def test_name_is_taken(name:str) -> bool:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Tests WHERE [name] = ?', (name,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()
        return bool(row)

    @staticmethod
    def rename_test(uuid:UUID, new_name:str) -> None:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('UPDATE Tests SET [name] = ? WHERE id = ?', (new_name, uuid))
        conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def get_test(question_uuid:UUID) -> Test:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT test_id FROM Questions WHERE id = ?', (question_uuid,))
        test_uuid = cursor.fetchone()[0]

        cursor.execute('SELECT * FROM Tests WHERE id = ?', (test_uuid,))
        test = Test(*cursor.fetchone())

        cursor.close()
        conn.close()
        return test

    @classmethod
    def delete_test(cls, test_uuid:UUID) -> None:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        question_uuids: list[UUID] = list(map(lambda i: (i.uuid,), cls.get_questions(test_uuid)))

        cursor.executemany('DELETE FROM AnswerLogs WHERE question_id = ?', question_uuids)
        conn.commit()

        cursor.executemany('DELETE FROM Answers WHERE question_id = ?', question_uuids)
        conn.commit()

        cursor.executemany('DELETE FROM Questions WHERE id = ?', question_uuids)
        cursor.execute('DELETE FROM Results WHERE test_id = ?', test_uuid)
        conn.commit()

        cursor.execute('DELETE FROM Tests WHERE id = ?', (test_uuid,))
        conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def get_tests() -> list[Test]:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Tests')
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return [Test(*i) for i in rows]

    @staticmethod
    def get_questions(test_uuid:UUID) -> list[Question]:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Questions WHERE test_id = ?', (test_uuid,))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return [Question(*i) for i in rows]

    @staticmethod
    def get_answers(question_uuid:UUID) -> list[Answer]:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Answers WHERE question_id = ?', (question_uuid,))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return [Answer(*i) for i in rows]

    @staticmethod
    def get_name_by_uuid(uuid:UUID) -> str:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        sql_lines = ('SELECT id, [name] AS [name] FROM Tests '
                     'UNION '
                     'SELECT id, [text] AS [name] FROM Questions '
                     'UNION '
                     'SELECT id, [text] AS [name] FROM Answers')

        cursor.execute(sql_lines)
        name = next((i[1] for i in cursor.fetchall() if i[0] == uuid), None)

        cursor.close()
        conn.close()
        return name

    @staticmethod
    def get_users_test_results(test_uuid:UUID) -> list[str]:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute(('SELECT [user_id], best_attempt, last_attempt '
                        'FROM Results WHERE test_id = ?'), (test_uuid,))
        
        res = []
        for user_uuid, best, last in cursor.fetchall():
            cursor.execute('SELECT [login] FROM Users WHERE id = ?', user_uuid)
            username = cursor.fetchone()[0]
            res.append(f'{username} : {int(best*100)}% : {int(last*100)}%')

        cursor.close()
        conn.close()
        return res

    @staticmethod
    def get_user_answers(test_uuid:UUID, user_login:str) -> list[str]:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM Users WHERE [login] = ?', user_login)
        user_uuid = cursor.fetchone()[0]

        cursor.execute(('SELECT question_id, answer_id, correct_flag '
                        'FROM AnswerLogs WHERE [user_id] = ?'), (user_uuid,))
        rows = cursor.fetchall()

        def f(row):
            q_uuid = row[0]
            cursor.execute('SELECT test_id FROM Questions WHERE id = ?', (q_uuid,))
            return test_uuid == cursor.fetchone()[0]

        rows = list(filter(f, rows))

        res = []
        for q_uuid, a_uuid, is_correct in rows:
            cursor.execute('SELECT [text] FROM Questions WHERE id = ?', q_uuid)
            q_text = cursor.fetchone()[0]

            cursor.execute('SELECT [text] FROM Answers WHERE id = ?', a_uuid)
            a_text = cursor.fetchone()[0]

            res.append(f'{"1:" if is_correct else "0:"}{q_text} : {a_text}')

        cursor.close()
        conn.close()
        return res

    @staticmethod
    def get_questions_percents(test_uuid:UUID) -> list[str]:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT question_id FROM AnswerLogs')
        q_uuids = [i[0] for i in cursor.fetchall()]

        def f(q_uuid):
            cursor.execute('SELECT test_id FROM Questions WHERE id = ?', (q_uuid,))
            return test_uuid == cursor.fetchone()[0]

        q_uuids = list(set(filter(f, q_uuids)))

        res = []
        for q_uuid in q_uuids:
            cursor.execute('SELECT [text] FROM Questions WHERE id = ?', (q_uuid,))
            q_name = cursor.fetchone()[0]

            cursor.execute('SELECT correct_flag FROM AnswerLogs WHERE question_id = ?', (q_uuid,))
            correct_flags = [i[0] for i in cursor.fetchall()]

            q_ratio = sum(correct_flags) / len(correct_flags)

            res.append(f'{q_name} : {int(q_ratio*100)}%')

        cursor.close()
        conn.close()
        return res

    @staticmethod
    def get_users_percents() -> list[str]:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT [user_id] FROM AnswerLogs')
        u_uuids = list(set([i[0] for i in cursor.fetchall()]))

        res = []
        for u_uuid in u_uuids:
            cursor.execute('SELECT [login] FROM Users WHERE id = ?', u_uuid)
            u_name = cursor.fetchone()[0]

            cursor.execute('SELECT correct_flag FROM AnswerLogs WHERE [user_id] = ?', (u_uuid,))
            correct_flags = [i[0] for i in cursor.fetchall()]

            u_ratio = sum(correct_flags) / len(correct_flags)

            res.append(f'{u_name} : {int(u_ratio*100)}%')

        cursor.close()
        conn.close()
        return res