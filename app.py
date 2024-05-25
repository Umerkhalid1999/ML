import smtplib
import random
import string
import streamlit as st
import numpy as np
import pickle
import pandas as pd

# Function to generate OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Function to send OTP via email
def send_otp(sender_email, recipient_email):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'ummeronatis7890@gmail.com'
    smtp_password = 'udrv urcr kkrs zzti'

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

# Load ML models
with open('BAI_score.pkl', 'rb') as file:
    anxiety_model = pickle.load(file)
with open('standard_score.pkl', 'rb') as file:
    anxiety_standard = pickle.load(file)
with open('ridge.pkl', 'rb') as file:
    depression_model = pickle.load(file)

# Predict anxiety level
def predict_anxiety(responses):
    new_individual = np.array([responses])
    new_individual_scaled = anxiety_standard.transform(new_individual)
    predicted_score = anxiety_model.predict(new_individual_scaled)[0]
    return predicted_score

# Categorize anxiety level
def categorize_anxiety(predicted_score):
    if predicted_score <= 21:
        return 'Low Anxiety', [
            'https://www.youtube.com/watch?v=ZidGozDhOjg',
            'https://www.youtube.com/watch?v=VRxOmosteCc',
            'https://www.youtube.com/watch?v=8vfLmShk7MM'
        ]
    elif 22 <= predicted_score <= 35:
        return 'Moderate Anxiety', [
            'https://www.youtube.com/watch?v=_eWEGVE8f4w',
            'https://www.youtube.com/watch?v=HRkGYNZdlDw',
            'https://www.youtube.com/watch?v=JA86YOd4zx4'
        ]
    else:
        return 'Potentially Concerning Levels of Anxiety', [
            'https://www.youtube.com/watch?v=QLjPrNe63kk',
            'https://www.youtube.com/watch?v=MdHXlAgUe9Y'
        ]

# Predict depression level
def predict_depression(depression_responses):
    response_values = [response for response in depression_responses.values()]
    new_individual = np.array([response_values])
    predicted_score = depression_model.predict(new_individual)[0]
    return predicted_score

# Categorize depression level
def categorize_depression(predicted_score):
    if predicted_score <= 1 or predicted_score <= 10:
        return 'Normal or no depression', [
            'https://www.youtube.com/watch?v=Bk0lzv8hEU8',
            'https://www.youtube.com/watch?v=TEwoWxLwCfA',
            'https://www.youtube.com/watch?v=OVJL850rAD8'
        ]
    elif predicted_score <= 11 or predicted_score <= 16:
        return 'Mild depression', [
            'https://www.youtube.com/watch?v=Y8qJ_0J2qKo',
            'https://www.youtube.com/watch?v=7sTWbgcuP2w',
            'https://www.youtube.com/watch?v=7DoQMnmo0v8'
        ]
    elif predicted_score <= 17 or predicted_score <= 20:
        return 'Borderline clinical depression', [
            'https://www.youtube.com/watch?v=qzTbEraKIOI',
            'https://www.youtube.com/watch?v=KSClXw4Wfxs'
        ]
    elif predicted_score <= 21 or predicted_score <= 30:
        return 'Moderate depression', [
            'https://www.youtube.com/watch?v=KSClXw4Wfxs',
            'https://www.youtube.com/watch?v=KSClXw4Wfxs'
        ]
    elif predicted_score <= 31 or predicted_score <= 40:
        return 'Severe depression', [
            'https://www.youtube.com/watch?v=KSClXw4Wfxs',
            'https://www.youtube.com/watch?v=KSClXw4Wfxs'
        ]
    else:
        return 'Extreme depression', [
            'https://www.youtube.com/watch?v=KSClXw4Wfxs',
            'https://www.youtube.com/watch?v=KSClXw4Wfxs'
        ]

# Main function for Streamlit app
def main():
    st.title("Mental Health Assessment")

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
                4: 'Continuous feelings of inner tension or intermittent panic which the patient can only master with difficulty',
                6: 'Unrelenting dread or anguish. Overwhelming panic'
            },
            "Q4 Reduced Sleep": {
                0: 'Sleeps as usual',
                1: 'Slight difficulty in falling asleep or slightly reduced sleep',
                2: 'Sleep reduced or broken by at least two hours',
                3: 'Less than two or three hours of sleep'
            },
            "Q5 Reduced Appetite": {
                0: 'Normal or increased appetite',
                1: 'Slightly reduced appetite',
                2: 'No appetite. Food is tasteless',
                3: 'Needs persuasion to eat at all'
            },
            "Q6 Concentration Difficulties": {
                0: 'No difficulties in concentrating',
                2: 'Occasional difficulties in collecting one’s thoughts',
                4: 'Difficulties in concentrating and sustaining thought which reduces ability to read or hold a conversation',
                6: 'Unable to read or converse without great difficulty'
            },
            "Q7 Lassitude": {
                0: 'Hardly any difficulties in getting started. No sluggishness',
                2: 'Difficulties in starting activities',
                4: 'Difficulties in starting simple routine activities which are carried out with effort',
                6: 'Complete lassitude. Unable to do anything without help'
            },
            "Q8 Inability to Feel": {
                0: 'Normal interest in the surroundings and other people',
                2: 'Reduced ability to enjoy usual interests',
                4: 'Loss of interest in the surroundings. Loss of feelings for friends and acquaintances',
                6: 'The experience of being emotionally paralyzed, inability to feel anger, grief, or pleasure and a complete or even painful failure to feel for close relatives and friends'
            },
            "Q9 Pessimistic Thoughts": {
                0: 'No pessimistic thoughts',
                1: 'Fluctuating ideas of failure, self-reproach, or self-depreciation',
                2: 'Persistent self-accusations, or definite but still rational ideas of guilt or sin. Increasingly pessimistic about the future',
                3: 'Delusions of ruin, remorse, or unredeemable sin. Self-accusations which are absurd and unshakable'
            },
            "Q10 Suicidal Thoughts": {
                0: 'Dismisses thoughts of suicide',
                1: 'Occasional thoughts of suicide',
                2: 'Suicidal thoughts are common, and the patient finds them difficult to control',
                3: 'Explicit plans for suicide when there is an opportunity'
            }
        }
        
        depression_responses = {}
        for question, options in depression_questions.items():
            st.markdown(f"**<span style='font-size:20px'>{question}</span>**", unsafe_allow_html=True)
            response = st.radio(f"Select the severity for '{question}'", list(options.keys()), format_func=lambda x: options[x])
            depression_responses[question] = response

        if st.button('Submit'):
            if len(depression_responses) == 10:
                st.session_state.depression_responses = depression_responses
                st.session_state.step = 6
                st.experimental_rerun()
            else:
                st.error("Please answer all questions before submitting.")

    elif st.session_state.step == 6:
        st.write("### Results")

        # Anxiety results
        anxiety_score = predict_anxiety(st.session_state.anxiety_responses)
        anxiety_level, anxiety_links = categorize_anxiety(anxiety_score)
        st.subheader("Anxiety Level:")
        st.write(f"**Your Anxiety Level:** {anxiety_level}")
        st.write("**Recommended Videos:**")
        for link in anxiety_links:
            st.write(f"- [Video]({link})")

        # Depression results
        depression_score = predict_depression(st.session_state.depression_responses)
        depression_level, depression_links = categorize_depression(depression_score)
        st.subheader("Depression Level:")
        st.write(f"**Your Depression Level:** {depression_level}")
        st.write("**Recommended Videos:**")
        for link in depression_links:
            st.write(f"- [Video]({link})")  
            
        st.write("### Physical Exercises:")
        for url in [
                "https://www.youtube.com/watch?v=fb3lDTS5IS4",
                "https://www.youtube.com/watch?v=6EysBiKaKmk",
                "https://www.youtube.com/watch?v=e9B3QWESkLI",
                "https://www.youtube.com/watch?v=LHLVgNBnFso",
                "https://www.youtube.com/watch?v=QevFo8wsXZ4"
            ]:
            st.write(f"- [{url}]({url})")

        st.write("### Reading Articles:")
        for url in [
                "https://communitymindset.org/",
                "https://peoplehouse.org/",
                "https://www.medicalnewstoday.com/articles/8933",
                "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3181767/",
                "https://www.healthline.com/health/can-you-cure-depression",
                "https://emedicine.medscape.com/article/286759-treatment?form=fpf",
                "https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2022.988648/full",
                "https://www.thelancet.com/journals/lanpsy/article/PIIS2215-0366(20)30036-5/fulltext"
            ]:
            st.write(f"- [{url}]({url})")

# Run the Streamlit app
if __name__ == "__main__":
    main()
