from tkinter     import Label, Button, Listbox, messagebox, Canvas
from tkinter.ttk import Notebook, Frame

from socket          import socket
from jsonpickle      import (encode as jsonpickle_encode,
                             decode as jsonpickle_decode)

from binary_io_loops import loopsend, looprecv

from client_server_shared_classes import Test, Question, Answer, Result

def get_tests_frame(conn:socket, tab_switch:Notebook, disable_binary_io_loop_info_display: bool):
    tests_frame = Frame(tab_switch, name='test_frame')

    LIST_WIDTH = 100
    LABEL_BUTTON_WIDTH = int(LIST_WIDTH * .8571)

    tests_lb = Listbox(tests_frame, width=LIST_WIDTH, height=14, selectmode='single', exportselection=False, justify='center')

    def on_test_select():
        nonlocal tests

        try   : tests_lb.curselection()[0]
        except: return

        t_name = tests_lb.get(tests_lb.curselection()[0])

        _, desc, best_score, last_score, date, q_of_q = next(i for i in tests if i[0] == t_name)

        test_info_label.config(text='\n'.join((f'DESCRIPTION: {desc}',
                                               f'QUESTIONS: {q_of_q}',
                                               f'BEST SCORE: {best_score if best_score else "You have not taken this test yet"}',
                                               f'LAST SCORE: {last_score if last_score else ""}',
                                               f'LAST ATTEMPTED ON: {date if date else "Never"}')))

    tests_lb.bind('<<ListboxSelect>>', lambda _: on_test_select())

    tests: list[tuple] = []
    # list's tuples indices:
    #   0 - test_name
    #   1 - test_desc
    #   2 - user_best_score
    #   3 - user_last_score
    #   4 - date_of_user_last_attempt
    #   5 - number_of_questions

    def refresh_test_list():
        conn.send(b'get_tests')

        binary_data = looprecv(conn, disable_binary_io_loop_info_display)
        nonlocal tests
        tests = jsonpickle_decode(binary_data)['response']

        test_names = (i[0] for i in tests)

        test_info_label.config(text='Select a test to see its information!')

        tests_lb.delete(0, 'end')
        for i in test_names:
            tests_lb.insert('end', i)

    Button(tests_frame, text='Refresh test list', command=refresh_test_list, width=LABEL_BUTTON_WIDTH).pack(pady=(10, 0))

    tests_lb.pack()

    taking_test = False

    def start_test():
        try   : tests_lb.curselection()[0]
        except: messagebox.showerror('Test selection error', 'Select a test before starting it'); return

        nonlocal taking_test
        if taking_test:
            messagebox.showerror('Test start error', 'You can NOT take more than one test at a time')
            return

        conn.send(b'get_q_and_a')
        test_name = tests_lb.get(tests_lb.curselection()[0])
        conn.send(test_name.encode())

        binary_data = looprecv(conn, disable_binary_io_loop_info_display)

        questions: list[Question] = jsonpickle_decode(binary_data)['response'][0]
        answers  : list[Answer]   = jsonpickle_decode(binary_data)['response'][1]

        selecting_via_code = True

        def disable_tab_change(event):
            tab_switch = event.widget
            nonlocal selecting_via_code
            if selecting_via_code:
                selecting_via_code = False
                return
            selecting_via_code = True
            tab_switch.select(3)
            messagebox.showerror('Changing tab error', 'Can\'t change tabs while taking the test.\n\nFinish the test or cancel it.')

        test_frame = Frame(tab_switch)
        
        user_answers: list[Answer] = []
        question_number = 1

        question_label = Label(test_frame, width=LABEL_BUTTON_WIDTH,
                               text=f'Question {1} / {len(questions)}:\n{questions[0].text}')
        question_label.pack(pady=(30, 0))

        answers_lb = Listbox(test_frame, width=LIST_WIDTH, height=14, selectmode='single', exportselection=False, justify='center')
        answers_lb.pack()

        def update_answers_lb(q_uuid):
            nonlocal answers
            answers_lb.delete(0, 'end')
            for i in (a.text for a in answers if a.question_uuid == q_uuid):
                answers_lb.insert('end', i)
        update_answers_lb(questions[0].uuid)

        def answer():
            if not answers_lb.curselection():
                messagebox.showerror('Answer error', 'Please select an answer from the list')
                return

            nonlocal questions, answers, user_answers, question_number

            picked_answer = answers_lb.get(answers_lb.curselection())

            q_uuid = questions[question_number - 1].uuid
            a_uuid = next(i.uuid for i in answers if (i.text == picked_answer and
                                                      i.question_uuid == q_uuid))

            user_answers.append(Answer(a_uuid, q_uuid, None, None))

            question_number += 1

            if question_number > len(questions):
                binary_data = jsonpickle_encode({
                                'user_answers': user_answers
                            }).encode()
                loopsend(conn, binary_data, disable_binary_io_loop_info_display)

                results = looprecv(conn, disable_binary_io_loop_info_display)
                answer_res, total_score = jsonpickle_decode(results)['results']

                results_frame = Frame(tab_switch)

                img = Canvas(results_frame, width=300, height=160)

                Label(results_frame, text='Results:', bg='#59ff7d', fg='white', font=('Calibri', 33, 'bold')).pack( fill='x')
                
                def score_display(img:Canvas, ratio):
                    img.delete('all')
                
                    img.create_arc((1, 1, 299, 299), extent=180, outline='', fill='light grey')
                    img.create_arc((3, 3, 297, 297), extent=180, outline='', fill='grey')
                
                    def brighten_color(color):
                        factor = 0.5
                
                        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                
                        bright_r = min(255, round(r + (255 - r) * factor))
                        bright_g = min(255, round(g + (255 - g) * factor))
                        bright_b = min(255, round(b + (255 - b) * factor))
                        
                        return f'#{bright_r:02x}{bright_g:02x}{bright_b:02x}'
                
                    def interpolate_color(factor):
                        color_a = '#fc3535'
                        color_b = '#3cfc35'
                
                        a_r, a_g, a_b = int(color_a[1:3], 16), int(color_a[3:5], 16), int(color_a[5:7], 16)
                        b_r, b_g, b_b = int(color_b[1:3], 16), int(color_b[3:5], 16), int(color_b[5:7], 16)
                        
                        result_r = round(a_r + (b_r - a_r) * factor)
                        result_g = round(a_g + (b_g - a_g) * factor)
                        result_b = round(a_b + (b_b - a_b) * factor)
                        
                        return brighten_color(f'#{result_r:02x}{result_g:02x}{result_b:02x}')
                
                    img.create_arc((1, 1, 299, 299), extent=180*ratio, start=180*(1-ratio), outline='', fill=interpolate_color(ratio))
                
                    img.create_arc((50, 50, 250, 250), extent=180, outline='', fill='#F0F0F0')
                
                    img.create_text(153, 115, text=f'{round(ratio*100)}%', font=('Calibri', 50, 'bold'), fill='#2d8af7')
                
                img.pack(pady=(10, 0))
                

                res_lb = Listbox(results_frame, width=LIST_WIDTH, height=7, selectmode='single', justify='center')

                for index, (q_text, a_text, is_correct) in enumerate(answer_res):
                    res_lb.insert('end', f'{q_text} : {a_text}')
                    res_lb.itemconfig(index, {'fg': ('green' if is_correct else 'red')})

                res_lb.pack(fill='x')

                Label(results_frame, text='Select another tab to close test results', width=LABEL_BUTTON_WIDTH).pack()

                def close_results_on_tab_switch(event):
                    notebook = event.widget
                    nonlocal selecting_via_code
                    if selecting_via_code:
                        selecting_via_code -= 1
                        return
                    notebook.forget(3)
                    notebook.unbind('<<NotebookTabChanged>>')

                close_test()
                selecting_via_code = 2
                tab_switch.add(results_frame, text='Test results')
                tab_switch.select(3)

                tab_switch.bind('<<NotebookTabChanged>>', close_results_on_tab_switch)

                ratio = int(total_score[:-1])/100
                for i in range(0, round(1001 * ratio) + 1, 10):
                    score_display(img, i/1000)
                    results_frame.update()
                    __import__('time').sleep(0.01)

                return

            question_label.config(text=f'Question {question_number} / {len(questions)}:\n{questions[question_number - 1].text}')

            update_answers_lb(questions[question_number - 1].uuid)

        Button(test_frame, text='Answer with selected answer', command=answer,
               width=LABEL_BUTTON_WIDTH).pack()

        def cancel_test():
            if not messagebox.askyesno('Canceling test warning!', 'Are you sure you want to cancel the test?\n\nYour results will NOT be saved'):
                return
            loopsend(conn, b'test_cancel', disable_binary_io_loop_info_display)
            close_test()

        Button(test_frame, text='Cancel test', command=cancel_test, fg='red').place(y=3, x=3)

        tab_switch.add(test_frame, text=f'Taking test: "{test_name}"')
        taking_test = True
        tab_switch.select(3)
        tab_switch.bind('<<NotebookTabChanged>>', disable_tab_change)

        def close_test():
            nonlocal taking_test
            taking_test = False
            tab_switch.unbind('<<NotebookTabChanged>>')
            tab_switch.forget(3)
        
    Button(tests_frame, text='Start selected test', command=start_test, width=LABEL_BUTTON_WIDTH).pack()

    test_info_label = Label(tests_frame, text='Select a test to see its information!',
                            bg='light grey', width=LABEL_BUTTON_WIDTH, height=5, justify='left')
    test_info_label.pack()

    refresh_test_list()

    return tests_frame