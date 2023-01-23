buttons = ['Новый вопрос', 'Сдаться', 'Мой Счёт']
rows = 2
keyboard = [buttons[i:i+rows] for i in range(0, len(buttons), rows)]

print(keyboard)