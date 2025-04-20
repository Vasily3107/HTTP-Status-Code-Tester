from tkinter     import Label, Button, Listbox
from tkinter.ttk import Notebook, Frame

from db_handler import DBHandler

from shared_classes import Test, Question, Answer

def get_stats_frame(tab_switch:Notebook) -> Frame:
    stats_frame = Frame(tab_switch)
    stats_tabs = Notebook(stats_frame)

    # - - - ANSWERS - - - - - - - - - - - - - - - - - - - - - - - - - - -
    answers_tab = Frame(stats_tabs)

    # - - - tests - - -
    Label(answers_tab, text='Tests:', bg='light grey').pack(fill='x')
    a_tests_lb = Listbox(answers_tab, width=50, height=4, selectmode='single', exportselection=False, justify='center')

    a_tests: list[Test] = []
    def update_a_tests_lb():
        a_users_lb.delete(0, 'end')
        a_answers_lb.delete(0, 'end')

        nonlocal a_tests
        a_tests = DBHandler.get_tests()

        a_tests_lb.delete(0, 'end')
        for t in a_tests:
            a_tests_lb.insert('end', t.name)

    Button(answers_tab, text='Refresh test list', command=update_a_tests_lb).pack(fill='x')
    a_tests_lb.pack(fill='x')

    def on_a_test_select(): update_a_users_lb(); a_answers_lb.delete(0, 'end')
    a_tests_lb.bind('<<ListboxSelect>>', lambda _: on_a_test_select())

    # - - - users - - -
    Label(answers_tab, text='User : Best attempt : Last attempt', bg='light grey').pack(fill='x')
    a_users_lb = Listbox(answers_tab, width=50, height=5, selectmode='single', exportselection=False, justify='center')
    a_users_lb.pack(fill='x')

    def update_a_users_lb():
        if not a_tests_lb.curselection(): return
        nonlocal a_tests

        test_name = a_tests_lb.get(a_tests_lb.curselection()[0])
        test_uuid = next(t.uuid for t in a_tests if t.name == test_name)

        user_scores = DBHandler.get_users_test_results(test_uuid)

        if not len(user_scores):
            a_users_lb.delete(0, 'end')
            a_users_lb.insert('end', 'Looks like no one has taken this test yet')
            a_users_lb.itemconfig(0, {'fg': 'red'})
        else:
            a_users_lb.delete(0, 'end')
            for i in user_scores:
                a_users_lb.insert('end', i)

    a_users_lb.bind('<<ListboxSelect>>', lambda _: update_a_answers_lb())

    # - - - answers - - -
    Label(answers_tab, text='Question : Answer (of last attempt)', bg='light grey').pack(fill='x')
    a_answers_lb = Listbox(answers_tab, width=50, height=6, selectmode='single', exportselection=False, justify='center')
    a_answers_lb.pack(fill='x')

    def update_a_answers_lb():
        if (not a_tests_lb.curselection() or
            not a_users_lb.curselection()): return

        test_name = a_tests_lb.get(a_tests_lb.curselection()[0])
        test_uuid = next(t.uuid for t in a_tests if t.name == test_name)

        user_name = a_users_lb.get(a_users_lb.curselection()[0])

        if ' : ' not in user_name: return

        user_name = user_name.split(' :')[0]

        user_answers = DBHandler.get_user_answers(test_uuid, user_name)

        a_answers_lb.delete(0, 'end')
        for i, a in enumerate(user_answers):
            is_correct = int(a.split(':')[0])
            a_answers_lb.insert('end', a.split(':', 1)[1])
            a_answers_lb.itemconfig(i, {'fg': ('green' if is_correct else 'red')})

    update_a_tests_lb()

    # - - - QUESTIONS - - - - - - - - - - - - - - - - - - - - - - - - - - -
    questions_tab = Frame(stats_tabs)

    # - - - tests - - -
    Label(questions_tab, text='Tests:', bg='light grey').pack(fill='x')
    q_tests_lb = Listbox(questions_tab, width=50, height=5, selectmode='single', exportselection=False, justify='center')

    q_tests: list[Test] = []
    def update_q_tests_lb():
        q_questions_lb.delete(0, 'end')

        nonlocal q_tests
        q_tests = DBHandler.get_tests()

        q_tests_lb.delete(0, 'end')
        for t in q_tests:
            q_tests_lb.insert('end', t.name)

    Button(questions_tab, text='Refresh test list', command=update_q_tests_lb).pack(fill='x')
    q_tests_lb.pack(fill='x')

    q_tests_lb.bind('<<ListboxSelect>>', lambda _: update_q_questions_lb())

    # - - - questions - - -
    Label(questions_tab, text='Question : Percent of correct answers of all users', bg='light grey').pack(fill='x')
    q_questions_lb = Listbox(questions_tab, width=50, height=12, selectmode='single', exportselection=False, justify='center')
    q_questions_lb.pack(fill='x')

    def update_q_questions_lb():
        if not q_tests_lb.curselection(): return
        nonlocal q_tests

        test_name = q_tests_lb.get(q_tests_lb.curselection()[0])
        test_uuid = next(t.uuid for t in q_tests if t.name == test_name)

        questions = DBHandler.get_questions_percents(test_uuid)
        
        if not len(questions):
            q_questions_lb.delete(0, 'end')
            q_questions_lb.insert('end', 'Looks like no one has taken this test yet')
            q_questions_lb.itemconfig(0, {'fg': 'red'})
        else:
            q_questions_lb.delete(0, 'end')
            for i in questions:
                q_questions_lb.insert('end', i)

    update_q_tests_lb()

    # - - - USERS - - - - - - - - - - - - - - - - - - - - - - - - - - -
    users_tab = Frame(stats_tabs)

    Label(users_tab, text='Users : Percent of correct answers from all tests', bg='light grey').pack(fill='x')
    users_lb = Listbox(users_tab, width=50, height=19, selectmode='single', exportselection=False, justify='center')

    def update_users_lb():
        users = DBHandler.get_users_percents()

        users_lb.delete(0, 'end')
        for i in users:
            users_lb.insert('end', i)

    Button(users_tab, text='Refresh users list', command=update_users_lb).pack(fill='x')

    users_lb.pack(fill='x')
    update_users_lb()



    stats_tabs.add(questions_tab, text='Questions')
    stats_tabs.add(answers_tab  , text='Answers')
    stats_tabs.add(users_tab    , text='Users')

    stats_tabs.pack(expand=1, fill='both')
    return stats_frame