from pyodbc import connect as connect_to_db
server   = 'localhost\SQLEXPRESS'
database = 'test_db'
dsn      =f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

from uuid import UUID, uuid4

from client_server_shared_classes import Test, Question, Answer, Result

class DBHandler:
    '''
    Server database handler
    '''
    
    @staticmethod
    def log_in(login:str, password:str) -> UUID | None:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM Users WHERE [login] = ? AND [password] = ?', (login, password))

        try   : uuid = cursor.fetchone()[0]
        except: uuid = None

        cursor.close()
        conn.close()
        return uuid

    @staticmethod
    def sign_up(login:str, password:str) -> UUID | None:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        uuid = None

        cursor.execute('SELECT id FROM Users WHERE [login] = ?', (login,))
        if not cursor.fetchone():
            uuid = uuid4()
            cursor.execute('INSERT INTO Users VALUES (?, ?, ?)', (uuid, login, password))
            conn.commit()

        cursor.close()
        conn.close()
        return uuid

    @staticmethod
    def get_tests(user_uuid:UUID) -> list[tuple]:
        '''
        list's tuples indices:
        0 - test_name
        1 - test_desc
        2 - user_best_score
        3 - user_last_score
        4 - date_of_user_last_attempt
        5 - number_of_questions

        user_scores and date_of_user_attempt will be None if user didn't take the test yet
        '''
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Tests')
        tests = [Test(*i) for i in cursor.fetchall()]

        cursor.execute('SELECT * FROM Results WHERE [user_id] = ?', (user_uuid,))
        results = [Result(*i) for i in cursor.fetchall()]

        cursor.execute('SELECT * FROM Questions')
        questions = [Question(*i) for i in cursor.fetchall()]

        cursor.close()
        conn.close()

        return_list = []

        for t in tests:
            if t.uuid not in (i.test_uuid for i in results):
                return_list.append((t.name, t.desc, None, None, None,
                                    len([i for i in questions if i.test_uuid == t.uuid])))
                continue

            best_attempt, last_attempt, date = next((str(int(i.best_attempt*100))+'%',
                                                     str(int(i.last_attempt*100))+'%',
                                                     str(i.date).split('.')[0])
                                                     for i in results
                                                     if i.test_uuid == t.uuid)
            return_list.append((t.name, t.desc, best_attempt, last_attempt, date, len([i for i in questions if i.test_uuid == t.uuid])))

        return return_list

    @staticmethod
    def get_questions_answers(test_name:str) -> tuple[list[Question], list[Answer]]:
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM Tests WHERE [name] = ?', (test_name,))
        test_uuid = cursor.fetchone()[0]

        cursor.execute('SELECT * FROM Questions WHERE test_id = ?', (test_uuid,))
        questions = [Question(*i) for i in cursor.fetchall()]

        answers = []
        for q in questions:
            cursor.execute('SELECT * FROM Answers WHERE question_id = ?', (q.uuid,))
            answers += [Answer(*i) for i in cursor.fetchall()]

        cursor.close()
        conn.close()

        return questions, answers

    @staticmethod
    def save_user_results(user_uuid:UUID, test_uuid:UUID, score:float, user_answers:list[Answer]):
        conn = connect_to_db(dsn)
        cursor = conn.cursor()

        cursor.execute('SELECT best_attempt FROM Results WHERE [user_id] = ? AND test_id = ?',
                       (user_uuid, test_uuid))

        row = cursor.fetchone()

        if not row:
            cursor.execute('INSERT INTO Results VALUES (NEWID(), ?, ?, GETDATE(), ?, ?)',
                           (user_uuid, test_uuid, score, score))

            for a in user_answers:
                cursor.execute('INSERT INTO AnswerLogs VALUES (NEWID(), ?, ?, ?, GETDATE(), ?)',
                               (user_uuid, a.question_uuid, a.uuid, a.is_correct))

        else:
            best_score = row[0]

            cursor.execute(f'UPDATE Results SET [date] = GETDATE(), last_attempt = ?{", best_attempt = ? " if score > best_score else ""} WHERE [user_id] = ? AND test_id = ?',
                           ((score, score, user_uuid, test_uuid)
                            if score > best_score else
                            (score, user_uuid, test_uuid)))

            for a in user_answers:
                cursor.execute(' '.join(('UPDATE AnswerLogs SET [date] = GETDATE(), correct_flag = ?, answer_id = ?',
                                         'WHERE [user_id] = ? AND question_id = ?')),
                               (a.is_correct, a.uuid, user_uuid, a.question_uuid))

        conn.commit()
        cursor.close()
        conn.close()