from tkinter     import Label, Button, Entry, Listbox, messagebox, Checkbutton, BooleanVar
from tkinter.ttk import Notebook, Frame, Style

from uuid import uuid4

from db_handler import DBHandler

from shared_classes import Question, Answer

def get_creating_frame(tab_switch:Notebook) -> Frame:
    creating_frame = Frame(tab_switch, width=800)

    # - - - HELPER FUNCTIONS - - - - - -
    def strip_entries():
        test_name = test_name_entry    .get().strip()
        test_desc = test_desc_entry    .get().strip()
        ques_text = question_text_entry.get().strip()
        answ_text = answer_text_entry  .get().strip()

        test_name_entry    .delete(0, 'end')
        test_desc_entry    .delete(0, 'end')
        question_text_entry.delete(0, 'end')
        answer_text_entry  .delete(0, 'end')

        test_name_entry    .insert(0, test_name)
        test_desc_entry    .insert(0, test_desc)
        question_text_entry.insert(0, ques_text)
        answer_text_entry  .insert(0, answ_text)

    def tab_reset():
        nonlocal added_questions, added_answers
        added_questions.clear()
        added_answers  .clear()
        test_name_entry     .delete(0, 'end')
        test_desc_entry     .delete(0, 'end')
        question_text_entry .delete(0, 'end')
        answer_text_entry   .delete(0, 'end')
        questions_list      .delete(0, 'end')
        answers_list        .delete(0, 'end')
        nonlocal is_correct_value
        is_correct_value.set(False)
        is_correct_checkbox.config(state='normal')


    # - - - TEST SUBFRAME - - - - - -
    Label(creating_frame, text='Test:', width=120, bg='light grey').pack()
    test_frame = Frame(creating_frame)
    Label(test_frame, text='Name:').grid(row=0, column=0)
    test_name_entry = Entry(test_frame, width=50)
    test_name_entry.grid(row=0, column=1)

    Label(test_frame, text='Description:').grid(row=1, column=0)
    test_desc_entry = Entry(test_frame, width=50)
    test_desc_entry.grid(row=1, column=1)
    test_frame.pack()


    # - - - QUESTION SUBFRAME - - - - - -
    Label(creating_frame, text='Questions:', width=120, bg='light grey').pack()
    question_frame = Frame(creating_frame) 

    added_questions : list[Question] = []

    questions_list = Listbox(question_frame, height=7, selectmode='single', width=50, exportselection=False)
    def update_questions_list():
        questions_list.delete(0, 'end')
        for i in added_questions:
            questions_list.insert('end', i.text)

    questions_list.grid(row=0, column=0, rowspan=2)

    def questions_list_selection(event):
        q_list = event.widget
        try:
            currect_question = added_questions[q_list.curselection()[0]].text
            if len(currect_question) > 30:
                currect_question = currect_question[:30] + '...'
            add_answer_button.config(text=f'Add answer to question: "{currect_question}"')
        except IndexError:
            add_answer_button.config(text='Select question before adding an answer')
        update_answers_list()

    questions_list.bind('<<ListboxSelect>>', questions_list_selection)

    Label(question_frame, text='Question text:').grid(row=0, column=1)
    question_text_entry = Entry(question_frame, width=50)
    question_text_entry.grid(row=0, column=2)

    def add_question():
        text = question_text_entry.get().strip()
        strip_entries()

        if not len(text):
            messagebox.showerror('Question text error', 'Question text can NOT be empty')
            return

        if text in [i.text for i in added_questions]:
            messagebox.showerror('Question text error', 'Question text must be unique')
            return

        question_text_entry.delete(0, 'end')
        added_questions.append(Question(uuid4(), None, text))
        update_questions_list()

    Button(question_frame, text='Add question', command=add_question, fg='green', width=50).grid(row=1, column=1, columnspan=2)
    question_frame.pack()


    # - - - ANSWER SUBFRAME - - - - - -
    Label(creating_frame, text='Answers:', width=120, bg='light grey').pack()
    answer_frame = Frame(creating_frame) 

    added_answers : list[Answer] = []

    answers_list = Listbox(answer_frame, height=7, selectmode='single', width=50, exportselection=False)
    def update_answers_list():
        try:
            answers_list.delete(0, 'end')
            for index, i in enumerate([i for i in added_answers if i.question_uuid == added_questions[questions_list.curselection()[0]].uuid]):
                answers_list.insert('end', i.text)
                answers_list.itemconfig(index, {'fg': ('green' if i.is_correct else 'red')})
            if any([i.is_correct for i in added_answers if i.question_uuid == added_questions[questions_list.curselection()[0]].uuid]):
                is_correct_checkbox.config(state='disabled')
            else:
                is_correct_checkbox.config(state='normal')
        except IndexError:
            ...

    answers_list.grid(row=0, column=0, rowspan=3)

    Label(answer_frame, text='Answer text:').grid(row=0, column=1)
    answer_text_entry = Entry(answer_frame, width=50)
    answer_text_entry.grid(row=0, column=2)

    is_correct_value = BooleanVar(value=False)
    is_correct_checkbox = Checkbutton(answer_frame, text='is correct', variable=is_correct_value, font=10)
    is_correct_checkbox.grid(row=1, column=1, columnspan=2)

    def add_answer():
        nonlocal is_correct_value
        strip_entries()
        text = answer_text_entry.get().strip()

        if not len(text):
            messagebox.showerror('Answer text error', 'Answer text can NOT be empty')
            return

        try:
            question_uuid = added_questions[questions_list.curselection()[0]].uuid
        except IndexError:
            messagebox.showerror('Answer addition error', 'Select a question from list of added questions to add an answer')
            return

        if text in [i.text for i in added_answers if i.question_uuid == question_uuid]:
            messagebox.showerror('Answer text error', 'Answer text must be unique')
            return

        answer_text_entry.delete(0, 'end')
        added_answers.append(Answer(uuid4(), question_uuid, text, is_correct_value.get()))
        update_answers_list()
        is_correct_value.set(False)

    add_answer_button = Button(answer_frame, text='Select question before adding an answer',
                               command=add_answer, fg='green', width=50)
    add_answer_button.grid(row=2, column=1, columnspan=2)
    answer_frame.pack()

    def send_to_db():
        strip_entries()

        if not len(added_questions):
            messagebox.showerror('Questions error', 'You forgot to add questions')
            return

        for uuid in [q.uuid for q in added_questions]:
            a_list = [i.is_correct for i in added_answers if i.question_uuid == uuid]

            if len(a_list) < 2:
                q_text = [q.text for q in added_questions if q.uuid == uuid][0]
                messagebox.showerror('Question answers error', f'Question "{q_text}" has {"only one answer" if len(a_list) else "no answers"}. Each question must have at least 2.')
                return

            if not any(a_list):
                q_text = [q.text for q in added_questions if q.uuid == uuid][0]
                messagebox.showerror('Question answers error', f'Question "{q_text}" has no correct answers')
                return

        name = test_name_entry.get().strip()
        desc = test_desc_entry.get().strip()

        if not len(name) or len(name) > 255:
            messagebox.showerror('Test name error', 'Name cannot be empty nor longer than 255 characters')
            return
        if not len(desc) or len(desc) > 255:
            messagebox.showerror('Test description error', 'Description cannot be empty nor longer than 255 characters')
            return

        if DBHandler.test_name_is_taken(name):
            messagebox.showerror('Test name error', 'Test with such name already exists')
            return

        DBHandler.add_test(name, desc, added_questions, added_answers)
        messagebox.showinfo('You got it!', 'Test was creeated.')

        tab_reset()

    Style().configure('lowest.TFrame', background='light grey')
    lowest_frame = Frame(creating_frame, style='lowest.TFrame', width=800)
    Button(lowest_frame, text='Create test', command=send_to_db, width=30, fg='green').grid(row=0, column=0)

    def delete_question():
        try:
            selected_question = added_questions[questions_list.curselection()[0]]
            added_questions.remove(selected_question)
            for i in [i for i in added_answers if i.question_uuid == selected_question.uuid]:
                added_answers.remove(i)
            update_questions_list()
            update_answers_list()
        except:
            messagebox.showerror('Question deletion error', 'Select to delete.')
            return
    Button(lowest_frame, text='Delete selected question', fg='red', command=delete_question).grid(row=0, column=2)

    def delete_answer():
        try:
            selected_answer = added_answers[answers_list.curselection()[0]]
            added_answers.remove(selected_answer)
            update_answers_list()
        except:
            messagebox.showerror('Answer deletion error', 'Select to delete.')
            return
    Button(lowest_frame, text='Delete selected answer', fg='red', command=delete_answer).grid(row=0, column=3)
    
    lowest_frame.columnconfigure(1, minsize= 33, weight=0)
    lowest_frame.columnconfigure(2, minsize=166, weight=0)
    lowest_frame.columnconfigure(3, minsize= 66, weight=0)
    lowest_frame.pack_propagate(False)
    lowest_frame.columnconfigure(0, weight=1)
    lowest_frame.columnconfigure(4, weight=1)
    lowest_frame.pack(fill='x', anchor='center', expand=True)



    return creating_frame