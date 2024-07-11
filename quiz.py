import streamlit as st
import time
def implementation():
    start = time.time()
    print(start)
    Q1 = "Question 1: Machine learning is the subset of following"
    ch1 = '''
                       1) Artificial Intelligence
                       2) Deep learning
                       3) Computer vision
                       4) Reinforcement Learning
                       '''
    op1 = 1

    Q2 = "Question 2: Machine learning is a subset of?"
    ch2 = '''
                       1) Intelligence
                       2) Deep
                       3) vision
                       4) Reinforcement
                        '''
    op2 = 2

    Q3 = "Question 3: What is Machine learning a subset of?"
    ch3 = '''
                       1) Artificial Intelligence
                       2) Deep learning 
                       3) Django framework
                       4) Python
                        '''
    op3 = 4

    Q4 = "Question 4: What is used to optimize loss functions in machine learning?"
    ch4 = '''
                           1) Gradient Descent
                           2) Random Forest
                           3) K-means
                           4) Naive Bayes
                            '''
    op4 = 1

    Q5 = "Question 5: What activation function is used in the output layer of a binary classification neural network?"
    ch5 = '''
                           1) ReLU
                           2) Sigmoid
                           3) Tanh
                           4) Softmax
                            '''
    op5 = 2

    Q6 = "Question 6: What algorithm is used for feature extraction in images?"
    ch6 = '''
                           1) PCA
                           2) K-means
                           3) CNN
                           4) SVM
                            '''
    op6 = 3

    Q7 = "Question 7: Which of the following is an ensemble learning method?"
    ch7 = '''
                           1) Decision Tree
                           2) SVM
                           3) Random Forest
                           4) K-nearest Neighbors
                            '''
    op7 = 3

    Q8 = "Question 8: What method is used for imputing missing values in a dataset?"
    ch8 = '''
                           1) Mean Imputation
                           2) Median Imputation
                           3) Mode Imputation
                           4) K-nearest Neighbors Imputation
                            '''
    op8 = 4

    Q9 = "Question 9: What is the metric used to evaluate the performance of a regression model?"
    ch9 = '''
                           1) Accuracy
                           2) F1-score
                           3) Mean Absolute Error
                           4) Area Under the ROC Curve (AUC-ROC)
                            '''
    op9 = 3
    l1 = [Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9]
    l2 = [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9]
    l3 = [op1, op2, op3, op4, op5, op6, op7, op8, op9]
    st.title("Machine Learning Quiz")
    correct = 0
    incorrect = 0
    quiz_completed = False  # Flag to track whether the quiz has been completed



    # Display the questions and options
    for i in range(len(l1)):
        st.write(f"## {l1[i]}")  # Display question heading
        options = l2[i].strip().split('\n')
        choice_text = st.radio(f"Select an option for Question {i + 1}:", options=options,
                               format_func=lambda x: x.split(')')[1].strip(), key=i, index=None)
        if choice_text is not None:  # Check if choice_text is not None
            # Extract the option number from the choice text
            choice_number = int(choice_text.split(")")[0])
            if choice_number == l3[i]:
                correct += 1
            else:
                incorrect += 1

    # Create placeholders for "Finish Quiz" button and quiz result
    finish_button_placeholder = st.empty()
    result_placeholder = st.empty()

    # Display "Finish Quiz" button and quiz result if the quiz is completed
    if not quiz_completed:
        if st.button("Finish Quiz"):
            quiz_completed = True
            # Clear the screen after the quiz is completed
            st.empty()
            # Display the result
            result_placeholder.header("Quiz Result:")
            result_placeholder.write(
                f"<h2>Total Percentage: {(correct / len(l1)) * 100:.2f}%-------Correct = {correct}          Incorrect = {incorrect}</h2>",
                unsafe_allow_html=True)

implementation()

