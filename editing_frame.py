from tkinter     import Label, Button, Entry, Listbox, messagebox
from tkinter.ttk import Notebook, Frame, Style

from uuid import UUID, uuid4

from db_handler import DBHandler

from shared_classes import Test, Question, Answer

debug_mode: bool = False
 # if True: 1. displaying lists in another thread:
 #                added, edited, and deleted questions
 #                added, edited, and deleted answers
 #          2. changes will NOT be saved to database

def get_editing_frame(tab_switch:Notebook) -> Frame:
    edit_frame = Frame(tab_switch)

    # - - - HELPER FUNCTIONS - - - - - - - - - - - - - - - - - - - - - - - -
    def strip_entries():
        edit_frame.focus()

        rename   = rename_entry        .get().strip()
        new_ques = new_ques_text_entry .get().strip()
        edit_que = edit_ques_text_entry.get().strip()
        new_answ = new_answ_text_entry .get().strip()
        edit_ans = edit_answ_text_entry.get().strip()

        rename_entry        .delete(0, 'end')
        new_ques_text_entry .delete(0, 'end')
        edit_ques_text_entry.delete(0, 'end')
        new_answ_text_entry .delete(0, 'end')
        edit_answ_text_entry.delete(0, 'end')

        rename_entry        .insert(0, rename)
        new_ques_text_entry .insert(0, new_ques)
        edit_ques_text_entry.insert(0, edit_que)
        new_answ_text_entry .insert(0, new_answ)
        edit_answ_text_entry.insert(0, edit_ans)

    def clear_placeholder(entry:Entry, placeholder_text:str):
        if entry.get() == placeholder_text:
            entry.delete(0, 'end')
            entry.config(fg='black')

    def restore_placeholder(entry:Entry, placeholder_text:str):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(fg='grey')

    def entry_bind_placeholder(entry:Entry, placeholder_text:str):
        entry.config(exportselection=True)
        entry.bind("<FocusIn>",  lambda _: clear_placeholder(entry, placeholder_text))
        entry.bind("<FocusOut>", lambda _: restore_placeholder(entry, placeholder_text))
        restore_placeholder(entry, placeholder_text)

    def clear_entries():
        rename_entry        .delete(0, 'end')
        new_ques_text_entry .delete(0, 'end')
        edit_ques_text_entry.delete(0, 'end')
        new_answ_text_entry .delete(0, 'end')
        edit_answ_text_entry.delete(0, 'end')
        
        rename_entry        .focus()
        new_ques_text_entry .focus()
        edit_ques_text_entry.focus()
        new_answ_text_entry .focus()
        edit_answ_text_entry.focus()

        edit_frame.focus()

    def get_test_uuid(name:str):
        return next(i.uuid for i in DBHandler.get_tests() if i.name == name)

    def get_question_uuid(test_uuid:UUID, text:str):
        nonlocal added_questions
        nonlocal edited_questions

        return (
        next((i.uuid
              for i in added_questions
              if (i.test_uuid == test_uuid
              and i.text    == text)), None)
        or
        next((i.uuid
              for i in edited_questions
              if (i.test_uuid == test_uuid
              and i.text    == text)), None)
        or
        next(i.uuid
             for i in DBHandler.get_questions(test_uuid)
             if i.text == text)
        )

    def get_answer_uuid(question_uuid:UUID, text:str):
        nonlocal added_answers
        nonlocal edited_answers

        return (
        next((i.uuid
              for i in added_answers
              if (i.question_uuid == question_uuid
              and i.text          == text)), None)
        or
        next((i.uuid
              for i in edited_answers
              if (i.question_uuid == question_uuid
              and i.text          == text)), None)
        or
        next(i.uuid
             for i in DBHandler.get_answers(question_uuid)
             if i.text == text)
        )


    # - - - CONSTANTS - - - - - - - - - - - - - - - - - - - - - - - -
    RENAME_PLACEHOLDER = 'Enter new test name here...'

    NEW_QUES_PLACEHOLDER = 'Enter new question text here...'
    EDIT_QUES_PLACEHOLDER = 'Enter edited question text here...'

    NEW_ANSW_PLACEHOLDER = 'Enter new answer text here...'
    EDIT_ANSW_PLACEHOLDER = 'Enter edited answer text here...'


    # - - - TESTS - - - - - - - - - - - - - - - - - - - - - - - -
    Label(edit_frame, text='Tests:', width=120, bg='light grey').pack()
    test_frame = Frame(edit_frame)

    test_lb = Listbox(test_frame, width=50, height=5, selectmode='single', exportselection=False)
    test_lb.grid(row=0, column=0, rowspan=3)

    def on_test_select(): update_question_lb(); answer_lb.delete(0, 'end')
    test_lb.bind('<<ListboxSelect>>', lambda _: on_test_select())

    rename_entry = Entry(test_frame, width=40)
    rename_entry.grid(row=0, column=1)
    entry_bind_placeholder(rename_entry, RENAME_PLACEHOLDER)

    def update_test_lb():
        test_lb.delete(0, 'end')
        tests = list(map(lambda i: i.name, DBHandler.get_tests()))
        for i in tests:
            test_lb.insert('end', i)
        question_lb.delete(0, 'end')
        answer_lb  .delete(0, 'end')

    def rename_test():
        strip_entries()
        new_name = rename_entry.get()

        try   : test_lb.curselection()[0]
        except: messagebox.showerror('Renaming error', 'Select test from the list to rename it'); return

        nonlocal RENAME_PLACEHOLDER
        if not len(new_name) or new_name == RENAME_PLACEHOLDER:
            messagebox.showerror('Renaming error', 'New test name can\'t be empty')
            return

        if DBHandler.test_name_is_taken(new_name):
            messagebox.showerror('Renaming error', 'New test name must be unique')
            return

        old_name = test_lb.get(test_lb.curselection()[0])

        DBHandler.rename_test(get_test_uuid(old_name), new_name)
        messagebox.showinfo('Notification', f'Test "{old_name}" was renamed as "{new_name}"')

        rename_entry.delete(0, 'end')
        restore_placeholder(rename_entry, RENAME_PLACEHOLDER)

        update_test_lb()
    Button(test_frame, text='Rename test', command=rename_test, width=20, fg='green').grid(row=0, column=2)

    def delete_test():
        try   : name = test_lb.get(test_lb.curselection()[0])
        except: messagebox.showerror('Deleting error', 'Select test from the list to delete it'); return

        if not messagebox.askyesno('Deletion warning', f'Are you sure you want to delete "{name}" test?\n\nCan NOT be restored after deletion!'):
            return

        t_uuid = get_test_uuid(name)

        nonlocal added_questions
        nonlocal edited_questions
        nonlocal deleted_questions

        nonlocal added_answers
        nonlocal edited_answers
        nonlocal deleted_answers

        del_q_uuids: list[UUID] = []
        for q_list in (added_questions,
                      edited_questions,
                     deleted_questions):
            tmp_l = []
            for q in q_list:
                if q.test_uuid == t_uuid:
                    del_q_uuids.append(q.uuid)
                    tmp_l.append(q)
            for i in tmp_l: q_list.remove(i)

        for a_list in (added_answers,
                      edited_answers,
                     deleted_answers):
            tmp_l = []
            for a in a_list:
                if a.question_uuid in del_q_uuids:
                    tmp_l.append(a)
            for i in tmp_l: a_list.remove(i)

        DBHandler.delete_test(t_uuid)
        messagebox.showinfo('Notification', f'Test "{name}" was deleted')

        update_test_lb()

    Button(test_frame, text='Delete test', command=delete_test, width=33, fg='red').grid(row=1, column=1)

    Button(test_frame, text='Refresh test list', command=update_test_lb, width=20).grid(row=1, column=2)

    test_frame.pack()



    # - - - QUESTIONS - - - - - - - - - - - - - - - - - - - - - - - -
    question_sep_label = Label(edit_frame, text='Questions:', width=120, bg='light grey')
    question_sep_label.pack()
    question_frame = Frame(edit_frame)

    added_questions  : list[Question] = []
    edited_questions : list[Question] = []
    deleted_questions: list[Question] = []

    question_lb = Listbox(question_frame, width=50, height=6, selectmode='single', exportselection=False)
    question_lb.grid(row=0, column=0, rowspan=3)

    question_lb.bind('<<ListboxSelect>>', lambda _: update_answer_lb())

    def update_question_lb():
        try   : test_lb.curselection()[0]
        except: return

        nonlocal added_questions
        nonlocal edited_questions
        nonlocal deleted_questions

        test_name = test_lb.get(test_lb.curselection()[0])
        test_uuid = get_test_uuid(test_name)

        db_questions = DBHandler.get_questions(test_uuid)

        display_questions: list[Question] = []

        for db_q in db_questions:
            q = next((i for i in edited_questions if i.uuid == db_q.uuid), None)
            display_questions.append(q if q else db_q)

        display_questions += [i for i in added_questions if i.test_uuid == test_uuid]

        for i in deleted_questions:
            if i in display_questions:
                display_questions.remove(i)

        question_lb.delete(0, 'end')
        answer_lb.delete(0, 'end')
        for i in display_questions:
            question_lb.insert('end', i.text)

        if not len(display_questions):
            question_sep_label.config(text='Selected test has no questions!', fg='red')
        else:
            question_sep_label.config(text='Questions:', fg='black')
        answer_sep_label.config(text='Answers:', fg='black')

    new_ques_text_entry = Entry(question_frame, width=40)
    new_ques_text_entry.grid(row=0, column=1)
    entry_bind_placeholder(new_ques_text_entry, NEW_QUES_PLACEHOLDER)

    def add_new_question():
        strip_entries()

        try   : test_lb.curselection()[0]
        except: messagebox.showerror('Qeustion addition error', 'Select test to add a question to'); return

        new_text = new_ques_text_entry.get()

        if not len(new_text) or new_text == NEW_QUES_PLACEHOLDER:
            messagebox.showerror('Naming error : empty text', 'Question text cannot be emtpy')
            return

        if new_text in question_lb.get(0, 'end'):
            messagebox.showerror('Naming error : repetitive text', 'There is already a question with this text')
            return

        test_name = test_lb.get(test_lb.curselection()[0])
        test_uuid = get_test_uuid(test_name)

        nonlocal added_questions
        added_questions.append(Question(uuid4(), test_uuid, new_text))

        new_ques_text_entry.delete(0, 'end')
        restore_placeholder(new_ques_text_entry, NEW_QUES_PLACEHOLDER)

        update_question_lb()
        nonlocal something_changed
        something_changed()

    Button(question_frame, text='Add new question', width=20, command=add_new_question, fg='green').grid(row=0, column=2)

    edit_ques_text_entry = Entry(question_frame, width=40)
    edit_ques_text_entry.grid(row=1, column=1)
    entry_bind_placeholder(edit_ques_text_entry, EDIT_QUES_PLACEHOLDER)

    def edit_question():
        strip_entries()

        try   : test_lb.curselection()[0]
        except: messagebox.showerror('Qeustion editing error', 'Select test to edit a question of it'); return
        try   : question_lb.curselection()[0]
        except: messagebox.showerror('Qeustion editing error', 'Select question to edit it'); return

        edit_text = edit_ques_text_entry.get()

        if not len(edit_text) or edit_text == EDIT_QUES_PLACEHOLDER:
            messagebox.showerror('Editing error : empty text', 'Question text cannot be emtpy')
            return
        if edit_text in question_lb.get(0, 'end'):
            messagebox.showerror('Editing error : repetitive text', 'There is already a question with this text')
            return

        test_name = test_lb.get(test_lb.curselection()[0])
        test_uuid = get_test_uuid(test_name)

        old_text = question_lb.get(question_lb.curselection()[0])
        q_uuid = get_question_uuid(test_uuid, old_text)

        nonlocal added_questions
        nonlocal edited_questions

        if q_uuid in (q.uuid for q in added_questions):
            for q in added_questions:
                if q.uuid == q_uuid:
                    q.text = edit_text
                    break

        elif q_uuid in (q.uuid for q in edited_questions):
            for q in edited_questions:
                if q.uuid == q_uuid:
                    q.text = edit_text
                    break

        else:
            edited_questions.append(Question(q_uuid, test_uuid, edit_text))

        edit_ques_text_entry.delete(0, 'end')
        restore_placeholder(edit_ques_text_entry, EDIT_QUES_PLACEHOLDER)
        update_question_lb()
        nonlocal something_changed
        something_changed()

    Button(question_frame, text='Edit question', width=20, command=edit_question, fg='green').grid(row=1, column=2)

    def delete_question():
        try   : test_lb.curselection()[0]
        except: messagebox.showerror('Qeustion deletion error', 'Select test to delete a question of it'); return
        try   : question_lb.curselection()[0]
        except: messagebox.showerror('Qeustion deletion error', 'Select question to delete it'); return

        test_name = test_lb.get(test_lb.curselection()[0])
        test_uuid = get_test_uuid(test_name)

        q_text = question_lb.get(question_lb.curselection()[0])
        q_uuid = get_question_uuid(test_uuid, q_text)

        del_q = Question(q_uuid, test_uuid, q_text)

        if del_q in added_questions:
            added_questions.remove(del_q)
        else:
            if del_q in edited_questions:
                edited_questions.remove(del_q)
            deleted_questions.append(del_q)

        nonlocal added_answers
        nonlocal edited_answers
        nonlocal deleted_answers

        f = lambda i: i.question_uuid != q_uuid

        added_answers = list(filter(f, added_answers))
        edited_answers = list(filter(f, edited_answers))
        deleted_answers += DBHandler.get_answers(q_uuid)
        deleted_answers = list(set(deleted_answers))

        update_question_lb()
        nonlocal something_changed
        something_changed()

    Button(question_frame, text='Delete selected question', width=33, command=delete_question, fg='red').grid(row=2, column=1, columnspan=2)

    question_frame.pack()



    # - - - ANSWERS - - - - - - - - - - - - - - - - - - - - - - - -
    answer_sep_label = Label(edit_frame, text='Answers:', width=120, bg='light grey')
    answer_sep_label.pack()
    answer_frame = Frame(edit_frame)

    added_answers  : list[Answer] = []
    edited_answers : list[Answer] = []
    deleted_answers: list[Answer] = []

    answer_lb = Listbox(answer_frame, width=50, height=6, selectmode='single', exportselection=False)
    answer_lb.grid(row=0, column=0, rowspan=4)

    def on_answer_select():
        try   : question_lb.curselection()[0]
        except: return
        try   : answer_lb.curselection()[0]
        except: return
        color = answer_lb.itemcget(answer_lb.curselection()[0], 'fg')
        set_is_correct_button.config(text=('Set as correct' if color == 'red' else 'Set as incorrect'))
    answer_lb.bind('<<ListboxSelect>>', lambda _: on_answer_select())

    def update_answer_lb():
        try   : question_lb.curselection()[0]
        except: return

        nonlocal added_answers  
        nonlocal edited_answers 
        nonlocal deleted_answers

        test_name = test_lb.get(test_lb.curselection()[0])
        test_uuid = get_test_uuid(test_name)

        q_text = question_lb.get(question_lb.curselection()[0])
        q_uuid = get_question_uuid(test_uuid, q_text)

        db_answers = DBHandler.get_answers(q_uuid)

        display_answers: list[Answer] = []

        for db_a in db_answers:
            a = next((i for i in edited_answers if i.uuid == db_a.uuid), None)
            display_answers.append(a if a else db_a)

        display_answers += [i for i in added_answers if i.question_uuid == q_uuid]

        for i in deleted_answers:
            if i in display_answers:
                display_answers.remove(i)

        display_answers.sort(key = lambda i: i.is_correct, reverse = True)

        answer_lb.delete(0, 'end')
        for index, i in enumerate(display_answers):
            answer_lb.insert('end', i.text)
            answer_lb.itemconfig(index, {'fg': ('green' if i.is_correct else 'red')})

        if not len(display_answers):
            answer_sep_label.config(text='Selected question has no answers!', fg='red')

        elif not any(i.is_correct for i in display_answers):
            answer_sep_label.config(text='Selected question has no correct answers!', fg='red')

        elif sum(i.is_correct for i in display_answers) > 1:
            answer_sep_label.config(text='Selected question has more than 1 correct answers!', fg='red')

        else:
            answer_sep_label.config(text='Answers:', fg='black')

    new_answ_text_entry = Entry(answer_frame, width=40)
    new_answ_text_entry.grid(row=0, column=1, columnspan=2)
    entry_bind_placeholder(new_answ_text_entry, NEW_ANSW_PLACEHOLDER)

    def add_new_answer():
        strip_entries()

        try   : test_lb.curselection()[0]
        except: messagebox.showerror('Answer addition error', 'Select test to add an answer to a question of it'); return
        try   : question_lb.curselection()[0]
        except: messagebox.showerror('Answer addition error', 'Select question to add an answer to it'); return

        new_text = new_answ_text_entry.get()

        if not len(new_text) or new_text == NEW_ANSW_PLACEHOLDER:
            messagebox.showerror('Naming error : empty text', 'Answer text cannot be emtpy')
            return

        if new_text in answer_lb.get(0, 'end'):
            messagebox.showerror('Naming error : repetitive text', 'There is already an answers with this text')
            return

        test_name = test_lb.get(test_lb.curselection()[0])
        test_uuid = get_test_uuid(test_name)

        q_text = question_lb.get(question_lb.curselection()[0])
        q_uuid = get_question_uuid(test_uuid, q_text)

        nonlocal added_answers
        added_answers.append(Answer(uuid4(), q_uuid, new_text, False))

        new_answ_text_entry.delete(0, 'end')
        restore_placeholder(new_answ_text_entry, NEW_ANSW_PLACEHOLDER)

        update_answer_lb()
        nonlocal something_changed
        something_changed()

    Button(answer_frame, text='Add new answer', width=20, command=add_new_answer, fg='green').grid(row=0, column=3)

    edit_answ_text_entry = Entry(answer_frame, width=40)
    edit_answ_text_entry.grid(row=1, column=1, columnspan=2)
    entry_bind_placeholder(edit_answ_text_entry, EDIT_ANSW_PLACEHOLDER)

    def edit_answer():
        strip_entries()

        try   : test_lb.curselection()[0]
        except: messagebox.showerror('Answer editing error', 'Select test to edit an answer of a question of it'); return
        try   : question_lb.curselection()[0]
        except: messagebox.showerror('Answer editing error', 'Select question to edit an answer of it'); return
        try   : answer_lb.curselection()[0]
        except: messagebox.showerror('Answer editing error', 'Select answer to edit it'); return

        edit_text = edit_answ_text_entry.get()

        if not len(edit_text) or edit_text == EDIT_ANSW_PLACEHOLDER:
            messagebox.showerror('Naming error : empty text', 'Answer text cannot be emtpy')
            return

        if edit_text in answer_lb.get(0, 'end'):
            messagebox.showerror('Naming error : repetitive text', 'There is already an answers with this text')
            return

        test_name = test_lb.get(test_lb.curselection()[0])
        test_uuid = get_test_uuid(test_name)

        q_text = question_lb.get(question_lb.curselection()[0])
        q_uuid = get_question_uuid(test_uuid, q_text)

        a_text = answer_lb.get(answer_lb.curselection()[0])
        a_uuid = get_answer_uuid(q_uuid, a_text)

        if a_uuid in (i.uuid for i in added_answers):
            for a in added_answers:
                if a.uuid == a_uuid:
                    a.text = edit_text

        elif a_uuid in (i.uuid for i in edited_answers):
            for a in edited_answers:
                if a.uuid == a_uuid:
                    a.text = edit_text

        else:
            is_correct = (answer_lb.itemcget(answer_lb.curselection()[0], 'fg') == 'green')
            edited_answers.append(Answer(a_uuid, q_uuid, edit_text, is_correct))

        edit_answ_text_entry.delete(0, 'end')
        restore_placeholder(edit_answ_text_entry, EDIT_ANSW_PLACEHOLDER)
        update_answer_lb()
        nonlocal something_changed
        something_changed()

    Button(answer_frame, text='Edit answer', width=20, command=edit_answer, fg='green').grid(row=1, column=3)

    def set_is_correct():
        try   : test_lb.curselection()[0]
        except: messagebox.showerror('Answer editing error', 'Select test to edit an answer of a question of it'); return
        try   : question_lb.curselection()[0]
        except: messagebox.showerror('Answer editing error', 'Select question to edit an answer of it'); return
        try   : answer_lb.curselection()[0]
        except: messagebox.showerror('Answer editing error', 'Select answer to edit it'); return

        test_name = test_lb.get(test_lb.curselection()[0])
        test_uuid = get_test_uuid(test_name)

        q_text = question_lb.get(question_lb.curselection()[0])
        q_uuid = get_question_uuid(test_uuid, q_text)

        a_text = answer_lb.get(answer_lb.curselection()[0])
        a_uuid = get_answer_uuid(q_uuid, a_text)

        new_a_is_correct = (answer_lb.itemcget(answer_lb.curselection()[0], 'fg') == 'red')

        if a_text in (i.text for i in added_answers if i.question_uuid == q_uuid):
            added_answers[
            added_answers.index(next(i for i in added_answers
                                     if i.uuid == a_uuid))
            ].is_correct = new_a_is_correct

        elif a_text in (i.text for i in edited_answers if i.question_uuid == q_uuid):
            edited_answers[
            edited_answers.index(next(i for i in edited_answers
                                      if i.uuid == a_uuid))
            ].is_correct = new_a_is_correct

        else:
            edited_answers.append(Answer(a_uuid, q_uuid, a_text, new_a_is_correct))

        update_answer_lb()
        nonlocal something_changed
        something_changed()

    set_is_correct_button = Button(answer_frame, text='Set as correct', command=set_is_correct)
    set_is_correct_button.grid(row=2, column=1, columnspan=2)

    def delete_answer():
        try   : test_lb.curselection()[0]
        except: messagebox.showerror('Answer deletion error', 'Select test to delete an answer of a question of it'); return
        try   : question_lb.curselection()[0]
        except: messagebox.showerror('Answer deletion error', 'Select question to delete an answer of it'); return
        try   : answer_lb.curselection()[0]
        except: messagebox.showerror('Answer deletion error', 'Select answer to delete it'); return

        test_name = test_lb.get(test_lb.curselection()[0])
        test_uuid = get_test_uuid(test_name)

        q_text = question_lb.get(question_lb.curselection()[0])
        q_uuid = get_question_uuid(test_uuid, q_text)

        a_text = answer_lb.get(answer_lb.curselection()[0])
        a_uuid = get_answer_uuid(q_uuid, a_text)

        is_correct = (answer_lb.itemcget(answer_lb.curselection()[0], 'fg') == 'green')

        del_a = Answer(a_uuid, q_uuid, a_text, is_correct)

        nonlocal added_answers
        nonlocal edited_answers
        nonlocal deleted_answers

        if del_a in added_answers:
            added_answers.remove(del_a)
        else:
            if del_a in edited_answers:
                edited_answers.remove(del_a)
            deleted_answers.append(del_a)

        update_answer_lb()
        nonlocal something_changed
        something_changed()

    Button(answer_frame, text='Delete selected answer', width=20, command=delete_answer, fg='red').grid(row=2, column=3)

    answer_frame.pack()

    update_test_lb()



    # - - - SAVE CHANGES - - - - - - - - - - - - - - - - - - - - - - - -
    Style().configure('save_changes.TFrame', background='light grey')
    save_changes_frame = Frame(edit_frame, style='save_changes.TFrame')

    def something_changed():
        changes_notification_label.config(text='Changes are NOT saved', fg='red')

    def save_changes_to_db():
        if changes_notification_label.cget('text') != 'Changes are NOT saved':
            messagebox.showerror('Saving changes error', 'Nothing was changed')
            return

        nonlocal added_questions
        nonlocal edited_questions
        nonlocal deleted_questions
        
        nonlocal added_answers
        nonlocal edited_answers
        nonlocal deleted_answers

        add_q: set[Question] = set(added_questions)
        edi_q: set[Question] = set(edited_questions)
        del_q: set[Question] = set(deleted_questions)

        add_a: set[Answer] = set(added_answers)
        edi_a: set[Answer] = set(edited_answers)
        del_a: set[Answer] = set(deleted_answers)

        # checking: ALL TESTS HAVE AT LEAST 1 QUESTION
        #
        #

        for t_uuid in {i.test_uuid for i in del_q}:

            db__q: set[Question] = set(DBHandler.get_questions(t_uuid))

            db__q -= del_q

            db__q |= {i for i in add_q if i.test_uuid == t_uuid}

            if not len(db__q):
                t_name = DBHandler.get_name_by_uuid(t_uuid)
                messagebox.showerror('Saving tests error | Questions',
                                    f'Test "{t_name}" has no questions. At least 1 is required!')
                return


        # checking: ALL REMAINING QUESTIONS HAVE AT LEAST 2 ANSWERS
        #           ALL REMAINING QUESTIONS HAVE AT LEAST 1 CORRECT ANSWERS
        #

        question_uuids: set[UUID] = ({i.uuid          for i in add_q}|
                                     {i.question_uuid for i in add_a}|
                                     {i.question_uuid for i in edi_a}|
                                     {a.question_uuid for a in del_a if (a.question_uuid not in (q.uuid for q in del_q))})

        for q_uuid in question_uuids:

            db__a: set[Answer] = set(DBHandler.get_answers(q_uuid))

            db__a -= del_a

            db__a -= edi_a
            db__a |= {i for i in edi_a if i.question_uuid == q_uuid}

            db__a |= {i for i in add_a if i.question_uuid == q_uuid}

            try:
                t_name = DBHandler.get_name_by_uuid(next(i.test_uuid for i in
                                                         ({i for i in add_q}|
                                                          {i for i in edi_q})
                                                         if i.uuid == q_uuid))
            except StopIteration:
                t_name = DBHandler.get_test(q_uuid).name

            try:
                q_name = next(i.text for i in
                             ({i for i in add_q}|
                              {i for i in edi_q})
                             if i.uuid == q_uuid)
            except StopIteration:
                q_name = DBHandler.get_name_by_uuid(q_uuid)

            if not len(db__a):
                messagebox.showerror('Saving tests error | Answers',
                                    f'Question "{q_name}" in test "{t_name}" has no answers. At least 2 are required!')
                return
            if 1 == len(db__a):
                messagebox.showerror('Saving tests error | Answers',
                                    f'Question "{q_name}" in test "{t_name}" has only 1 answer. At least 2 are required!')
                return
            if not any(i.is_correct for i in db__a):
                messagebox.showerror('Saving tests error | Answers',
                                    f'Question "{q_name}" in test "{t_name}" has no correct answers. 1 correct answer is required!')
                return
            if 1 < sum(i.is_correct for i in db__a):
                messagebox.showerror('Saving tests error | Answers',
                                    f'Question "{q_name}" in test "{t_name}" has more than 1 correct answers. Each question must have only 1 correct answer!')
                return

        global debug_mode
        if not debug_mode:
            if not messagebox.askyesno('Saving changes', '\n'.join(('Are you sure you want to save the changes?\n',
                                                                    'Can NOT be cancelled after saving!'))):
                return
            DBHandler.save_test_changes(   added_questions,
                                          edited_questions,
                                         deleted_questions,

                                           added_answers,
                                          edited_answers,
                                         deleted_answers )

        added_questions  .clear()
        edited_questions .clear()
        deleted_questions.clear()

        added_answers  .clear()
        edited_answers .clear()
        deleted_answers.clear()

        changes_notification_label.config(text='All changes have been saved', fg='green')

        edit_frame.focus()

        clear_entries()

        update_test_lb()
        messagebox.showinfo('Changes saved', 'All changes have been saved')

    Button(save_changes_frame, text='Save changes', command=save_changes_to_db, fg='green').grid(row=0, column=0, padx=(50, 0))

    def cancel_changes():
        if changes_notification_label.cget('text') == 'All changes have been saved':
            messagebox.showerror('Canceling changes error', 'Saved changes can NOT be reverted')
            return
        if changes_notification_label.cget('text') in ('Waiting for changes...', 'All changes have been cancelled'):
            messagebox.showerror('Canceling changes error', 'No changes were made')
            return
        if not messagebox.askyesno('Canceling changes', '\n'.join(('Are you sure you want to cancel the changes?\n',
                                                                   'Can NOT be restored after canceling!'))):
            return

        nonlocal added_questions
        nonlocal edited_questions
        nonlocal deleted_questions
        
        nonlocal added_answers
        nonlocal edited_answers
        nonlocal deleted_answers

        added_questions  .clear()
        edited_questions .clear()
        deleted_questions.clear()

        added_answers  .clear()
        edited_answers .clear()
        deleted_answers.clear()

        update_test_lb()

        answer_sep_label.config(text='Answers', fg='black')
        question_sep_label.config(text='Questions', fg='black')

        changes_notification_label.config(text='All changes have been cancelled', fg='black')
        messagebox.showinfo('Changes cancelled', 'All changes have been cancelled')

    Button(save_changes_frame, text='Cancel changes', command=cancel_changes, fg='red').grid(row=0, column=1, padx=50)

    changes_notification_label = Label(save_changes_frame, text='Waiting for changes...')
    changes_notification_label.grid(row=0, column=2)

    save_changes_frame.pack(fill='x', anchor='center', expand=True)



    # - - - FOR DEBUGGING - - - - - - - - - - - - - - - - - - - - - - - -
    global debug_mode

    def print_debug_info():
        nonlocal added_questions
        nonlocal edited_questions
        nonlocal deleted_questions
        
        nonlocal added_answers
        nonlocal edited_answers
        nonlocal deleted_answers

        from os import system
        from time import sleep

        while 1:
            system('cls')
            print(f'  {added_questions = }')
            print(f' {edited_questions = }')
            print(f'{deleted_questions = }')
            print()
            print(f'    {added_answers = }')
            print(f'   {edited_answers = }')
            print(f'  {deleted_answers = }')
            sleep(1)

    if debug_mode:
        __import__('threading').Thread(target=print_debug_info, daemon=1).start()

    return edit_frame