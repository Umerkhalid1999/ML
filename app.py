import smtplib
import random
import string
import streamlit as st
import numpy as np
import pickle
import pandas as pd

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp(sender_email, recipient_email):
    # Replace these values with your SMTP server details
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'ummeronatis7890@gmail.com'
    smtp_password = 'udrv urcr kkrs zzti'  # Add your Gmail password here

    otp = generate_otp()
    message = f'Subject: Your OTP\n\nYour OTP is: {otp}'

    server = None
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, recipient_email, message)
        print('OTP sent successfully!')
        return otp
    except Exception as e:
        print(f'Failed to send OTP: {e}')
        return None
    finally:
        if server is not None:
            server.quit()

# Load your models using pickle
with open('BAI_score.pkl', 'rb') as file:
    anxiety_model = pickle.load(file)
with open('standard_score.pkl', 'rb') as file:
    anxiety_standard = pickle.load(file)
with open('ridge.pkl', 'rb') as file:
    depression_model = pickle.load(file)

def predict_anxiety(responses):
    new_individual = np.array([responses])
    new_individual_scaled = anxiety_standard.transform(new_individual)
    predicted_score = anxiety_model.predict(new_individual_scaled)[0]
    return predicted_score

def categorize_anxiety(predicted_score):
    if predicted_score <= 21:
        return 'Low Anxiety', ['https://www.youtube.com/watch?v=zUx5kLFyx-M', 'https://www.youtube.com/watch?v=L1HCG3BGK8I']
    elif 22 <= predicted_score <= 35:
        return 'Moderate Anxiety', ['https://www.youtube.com/watch?v=zUx5kLFyx-M']
    else:
        return 'Potentially Concerning Levels of Anxiety', ['https://www.youtube.com/watch?v=1XCObQjSHIs']

def predict_depression(depression_responses):
    response_values = [response for response in depression_responses.values()]
    new_individual = np.array([response_values])
    predicted_score = depression_model.predict(new_individual)[0]
    return predicted_score

def categorize_depression(predicted_score):
    if predicted_score <= 1 or predicted_score <= 10:
        return 'Normal or no depression'
    elif predicted_score <= 11 or predicted_score <= 16:
        return 'Mild depression'
    elif predicted_score <= 17 or predicted_score <= 20:
        return 'Borderline clinical depression'
    elif predicted_score <= 21 or predicted_score <= 30:
        return 'Moderate depression'
    elif predicted_score <= 31 or predicted_score <= 40:
        return 'Severe depression'
    else:
        return 'Extreme depression'

def main():
    st.title("Mental Health Assessment")

    # Initialize session state variables
    if 'step' not in st.session_state:
        st.session_state.step = 1

    if st.session_state.step == 1:
        st.write("### Please enter your email address to receive the OTP:")
        recipient_email = st.text_input("Enter your email address")

        if st.button("Send OTP"):
            if recipient_email:
                otp_sent = send_otp('ummeronatis7890@gmail.com', recipient_email)
                if otp_sent:
                    st.session_state.otp = otp_sent
                    st.session_state.recipient_email = recipient_email
                    st.session_state.step = 2
                    st.experimental_rerun()
                else:
                    st.error("Failed to send OTP. Please try again.")
            else:
                st.error("Please enter your email address.")

    elif st.session_state.step == 2:
        st.write("### Enter the OTP sent to your email to continue:")
        entered_otp = st.text_input("Enter OTP")

        if st.button("Continue"):
            if entered_otp == st.session_state.otp:
                st.session_state.step = 3
                st.experimental_rerun()
            else:
                st.error("Incorrect OTP. Please try again.")

    elif st.session_state.step == 3:
        st.write("### Please fill out your information:")
        st.session_state.name = st.text_input("Name")
        st.session_state.age = st.number_input("Age", min_value=1, max_value=120, step=1)
        st.session_state.gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        if st.button("Next"):
            if st.session_state.name and st.session_state.age and st.session_state.gender:
                st.session_state.step = 4
                st.experimental_rerun()
            else:
                st.error("Please fill out all the fields to proceed.")

    elif st.session_state.step == 4:
        st.write("### Anxiety Questionnaire")
        anxiety_questions = [
            "Q1 Numbness or tingling", "Q2 Feeling hot", "Q3 Wobbliness in legs", "Q4 Unable to relax", "Q5 Fear of the worst happening",
            "Q6 Dizzy or lightheaded", "Q7 Heart pounding/racing", "Q8 Unsteady", "Q9 Terrified or afraid", "Q10 Nervous",
            "Q11 Feeling of choking", "Q12 Hands trembling", "Q13 Shaky/unsteady", "Q14 Fear of losing control", "Q15 Difficulty in breathing",
            "Q16 Fear of dying", "Q17 Scared", "Q18 Indigestion", "Q19 Faint/lightheaded", "Q20 Face flushed", "Q21 Hot/cold sweats"
        ]
        anxiety_responses = []
        for question in anxiety_questions:
            st.markdown(f"**<span style='font-size:20px'>{question}</span>**", unsafe_allow_html=True)
            response = st.radio(
                f"Select the severity for '{question}'", [0, 1, 2, 3],
                format_func=lambda x: {0: "Not at all", 1: "Mildly but it didn’t bother me much", 2: "Moderately - it wasn’t pleasant at times", 3: "Severely – it bothered me a lot"}[x]
            )
            anxiety_responses.append(response)

        if st.button('Next'):
            if len(anxiety_responses) == 21:
                st.session_state.anxiety_responses = anxiety_responses
                st.session_state.step = 5
                st.experimental_rerun()
            else:
                st.error("Please answer all questions before submitting.")

    elif st.session_state.step == 5:
        st.write("### Depression Questionnaire")
        depression_questions = {
            "Q1 Apparent Sadness": {
                0: 'No sadness',
                1: 'Looks dispirited but does brighten up without difficulty',
                2: 'Appears sad and ,unhappy most of the time',
                3: 'Looks miserable all the time. Extremely despondent'
            },
            "Q2 Reported Sadness": {
                0: 'Occasional sadness in keeping with the circumstances',
                2: 'Sad or low but brightens up without difficulty',
                4: 'Pervasive feelings of sadness or gloominess. The mood is still influenced by external circumstances.',
                6: 'Continuous or unvarying sadness, misery or despondency'
            },
            "Q3 Inner Tension": {
                0: 'Placid. Only fleeting inner tension',
                2: 'Occasional feelings of edginess and ill-defined discomfort',
                4: 'Continuous feelings of inner tension or intermittent panic which the patient can only master with some difficulty',
                6: 'Unrelenting dread or anguish. Overwhelming panic'
            },
            "Q4 Reduced Sleep": {
                0: 'Sleeps as usual',
                2: 'Slight difficulty dropping off to sleep or slightly reduced, light or fitful sleep',
                4: 'Sleep reduced or broken by at least two hours',
                6: 'Less than two or three hours sleep'
            },
            "Q5 Reduced Appetite": {
                0: 'Normal or increased appetite',
                2: 'Slightly reduced appetite',
                4: 'No appetite. Food is tasteless',
                6: 'Needs persuasion to eat at all'
            },
            "Q6 Concentration Difficulties": {
                0: 'No difficulties in concentrating',
                2: 'Occasional difficulties in collecting one\'s thoughts',
                4: 'Difficulties in concentrating and sustaining thought which reduces ability to read or hold a conversation',
                6: 'Unable to read or converse without great difficulty'
            },
            "Q7 Lassitude": {
                0: 'Hardly any difficulty in getting started. No sluggishness',
                2: 'Difficulties in starting activities',
                4: 'Difficulties in starting simple routine activities which are carried out with effort',
                6: 'Complete lassitude. Unable to do anything without help'
            },
            "Q8 Inability to Feel": {
                0: 'Normal interest in the surroundings and in other people',
                2: 'Reduced ability to enjoy usual interests',
                4: 'Loss of interest in the surroundings. Loss of feelings for friends and acquaintances',
                6: 'The experience of being emotionally paralyzed, inability to feel anger, grief or pleasure and a complete or even painful failure to feel for close relatives and friends'
            },
            "Q9 Pessimistic Thoughts": {
                0: 'No pessimistic thoughts',
                2: 'Fluctuating ideas of failure, self-reproach or self-depreciation',
                4: 'Persistent self-accusations, or definite but still rational ideas of guilt or sin. Increasingly pessimistic about the future',
                6: 'Delusions of ruin, remorse or unredeemable sin. Self-accusations which are absurd and unshakable'
            },
            "Q10 Suicidal Thoughts": {
                0: 'Enjoys life or takes it as it comes',
                2: 'Weary of life. Only fleeting suicidal thoughts',
                4: 'Probably better off dead. Suicidal thoughts are common, and suicide is considered as a possible solution, but without specific plans or intention',
                6: 'Explicit plans for suicide when there is an opportunity. Active preparation for suicide'
            }
        }
        depression_responses = {}
        for question, options in depression_questions.items():
            st.markdown(f"**<span style='font-size:20px'>{question}</span>**", unsafe_allow_html=True)
            response = st.radio(
                f"Select the severity for '{question}'", options.values(),
                format_func=lambda x: x
            )
            depression_responses[question] = {v: k for k, v in options.items()}[response]

        if st.button('Predict Mental Health Levels'):
            if len(depression_responses) == len(depression_questions):
                st.session_state.depression_responses = depression_responses
                st.session_state.step = 6
                st.experimental_rerun()
            else:
                st.error("Please answer all questions before submitting.")

    elif st.session_state.step == 6:
        st.write("### Results")
        st.markdown(f"**Name:** {st.session_state.name}")
        st.markdown(f"**Age:** {st.session_state.age}")
        st.markdown(f"**Gender:** {st.session_state.gender}")

        anxiety_score = predict_anxiety(st.session_state.anxiety_responses)
        anxiety_category, anxiety_videos = categorize_anxiety(anxiety_score)
        st.markdown(f"**Your predicted anxiety level is: <span style='font-size:25px'>{anxiety_category}</span>**", unsafe_allow_html=True)

        depression_score = predict_depression(st.session_state.depression_responses)
        depression_category = categorize_depression(depression_score)
        st.markdown(f"**Your predicted anxiety level is: <span style='font-size:25px'>{depression_category}</span>**", unsafe_allow_html=True)


        for url in anxiety_videos:
            st.video(url)

        result_data = {
            "Name": st.session_state.name,
            "Age": st.session_state.age,
            "Gender": st.session_state.gender,
            "Anxiety Level": anxiety_category,
            "Depression Level": depression_category,
        }
        df = pd.DataFrame([result_data])
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Results",
            data=csv,
            file_name='mental_health_results.csv',
            mime='text/csv'
        )

if __name__ == "__main__":
    main()

