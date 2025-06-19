from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QLineEdit, QPushButton, QVBoxLayout,
                               QComboBox, QHBoxLayout, QTextEdit, 
                               QScrollArea, QLabel)
from PySide6.QtCore import Qt
import sys
import pandas as pd

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.word_bank = pd.read_csv('wordle-answers-alphabetical.csv')
        self.far_bank = self.word_bank.__deepcopy__()

        
        # Set window properties
        self.setWindowTitle("Wordle Helper")
        self.setMinimumSize(1000, 500)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create guess input field
        self.guess = QLineEdit()
        self.guess.setPlaceholderText("Enter your guess...")
        self.guess.setFixedWidth(500)  # Set fixed width
        self.guess.setAlignment(Qt.AlignCenter)  # Center text
        layout.addWidget(self.guess, alignment=Qt.AlignHCenter)

        # Create state input field
        self.state = QLineEdit()
        self.state.setFixedWidth(500)  # Set fixed width
        self.state.setAlignment(Qt.AlignCenter)  # Center text
        self.state.setPlaceholderText("Enter the state...")
        layout.addWidget(self.state, alignment=Qt.AlignHCenter)

        self.guess.returnPressed.connect(self.state.setFocus)

        # Create main horizontal layout for scroll areas
        scroll_layout = QHBoxLayout()
        
        # Create scroll area for close words
        close_scroll = QScrollArea()
        close_scroll.setWidgetResizable(True)
        close_scroll.setMinimumWidth(300)
        close_scroll.setFixedHeight(275)
        
        # Create widget to hold words
        self.close_word_container = QWidget()
        self.close_word_layout = QVBoxLayout(self.close_word_container)
        
        # Style the scroll area
        close_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        
        # Add word container to scroll area
        close_scroll.setWidget(self.close_word_container)
        
        # Add both panels to main layout
        # layout.addWidget(left_panel)
        layout.addWidget(close_scroll)

        # -------------------------------------------------------
        # Create scroll area for words
        far_scroll = QScrollArea()
        far_scroll.setWidgetResizable(True)
        far_scroll.setMinimumWidth(300)
        far_scroll.setFixedHeight(275)
        
        # Create widget to hold words
        self.far_word_container = QWidget()
        self.far_word_layout = QVBoxLayout(self.far_word_container)
        
        # Style the scroll area
        far_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        
        # Add word container to scroll area
        far_scroll.setWidget(self.far_word_container)

         # Add titles above scroll areas
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_title = QLabel("Close Words")
        left_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #90caf9;
                padding: 1px;
            }
        """)
        left_layout.addWidget(left_title, alignment=Qt.AlignHCenter)
        left_layout.addWidget(close_scroll)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_title = QLabel("Far Words")
        right_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #90caf9;
                padding: 1px;
            }
        """)
        right_layout.addWidget(right_title, alignment=Qt.AlignHCenter)
        right_layout.addWidget(far_scroll)

        # Add panels to horizontal layout
        scroll_layout.addWidget(left_panel)
        scroll_layout.addWidget(right_panel)
        
        # Add both panels to main layout
        # layout.addWidget(left_panel)
        layout.addLayout(scroll_layout)

         # Create submit button with modern styling
        self.submit_button = QPushButton("Submit")
        self.submit_button.setFixedWidth(500)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)
        self.submit_button.clicked.connect(self.get_input)
        self.state.returnPressed.connect(self.submit_button.click)
        self.state.returnPressed.connect(self.guess.setFocus)
        layout.addWidget(self.submit_button, alignment=Qt.AlignHCenter)
    
    def update_word_list(self, close_words, far_words):
        # Clear existing close words
        for i in reversed(range(self.close_word_layout.count())): 
            self.close_word_layout.itemAt(i).widget().setParent(None)
        
        # Clear existing far words
        for i in reversed(range(self.far_word_layout.count())): 
            self.far_word_layout.itemAt(i).widget().setParent(None)
        
        
        # Add new close words
        for word in close_words:
            label = QLabel(word)
            label.setStyleSheet("""
                QLabel {
                    padding: 5px;
                    font-size: 14px;
                }
                QLabel:hover {
                    background-color: #000000;
                }
            """)
            self.close_word_layout.addWidget(label)

        # Add new far words
        for word in far_words:
            label = QLabel(word)
            label.setStyleSheet("""
                QLabel {
                    padding: 5px;
                    font-size: 14px;
                }
                QLabel:hover {
                    background-color: #000000;
                }
            """)
            self.far_word_layout.addWidget(label)
        

    def close_mask(self, guess_array, df):
        '''
        Args
            guess_array (list[tuple]) - array of tuples with character and state
            df (pd.DataFrame) - word bank
        Returns
            mask - mask of words which could be the answer
        '''
        mask = pd.Series([True] * len(df))
        j = 0
        for g, i in guess_array:
            # If character is not in the word, removes all
            # words in the word bank with that character
            if i == '0' and (g, '2') not in guess_array:
                mask = mask & (~df['Words'].str.contains(g))
            # If character is yellow, ensure char in the word but
            # not in its current position
            elif i == '1':
                mask = mask & df['Words'].str.contains(g)
                mask = mask & (df['Words'].apply(lambda x: x[j] != g))
            # if char is green, ensure we only have words with that
            # char in that exact position
            elif i == '2':
                mask = mask & df['Words'].apply(lambda x: x[j] == g)
            j += 1
        return mask
    
    def far_mask(self, guess_array, df):
        '''
        Args
            guess_array (list[tuple]) - array of tuples with character and state
            df (pd.DataFrame) - word bank
        Returns
            mask - mask of words that are furthest from the current guess
        '''
        mask = pd.Series([True] * len(df))
        for g, _ in guess_array:
            mask = mask & (~df['Words'].str.contains(g))
        return mask


    def get_input(self):
        guess = self.guess.text()
        state = self.state.text()
        self.guess.clear()
        self.state.clear()
        guess_array = list(zip(guess, state))
        c_mask = self.close_mask(guess_array, self.word_bank)
        f_mask = self.far_mask(guess_array, self.far_bank)
        self.far_bank = self.far_bank[f_mask].reset_index(drop=True)
        self.word_bank = self.word_bank[c_mask].reset_index(drop=True)
        self.update_word_list(self.word_bank['Words'], self.far_bank['Words'])

        print(f'{guess}, {state}')

if __name__ == '__main__':
    app = QApplication(sys.argv)

    word_bank = pd.read_csv('wordle-answers-alphabetical.csv')
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.update_word_list(word_bank['Words'], [])
    window.show()
    sys.exit(app.exec())  # Note: exec() instead of exec_()