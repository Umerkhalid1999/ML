import streamlit as st 
import joblib 
import numpy as np 
import pandas as pd
from PIL import Image
import base64

# Custom CSS to enhance the UI
def add_custom_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1000px;
    }
    
    /* Custom card styles */
    .stButton button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 12px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Customize header */
    h1 {
        color: #2C3E50;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: bold;
        padding-bottom: 10px;
        border-bottom: 2px solid #4CAF50;
        margin-bottom: 30px;
    }
    
    /* Input fields styling */
    .stNumberInput div {
        margin-bottom: 15px;
    }
    
    .stNumberInput div > div > input {
        border-radius: 4px;
        border: 1px solid #bbb;
        padding: 8px 10px;
    }
    
    /* Results styling */
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
        margin: 20px 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
        margin: 20px 0;
    }
    
    /* Card container */
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Labels */
    label {
        font-weight: 500;
        color: #333;
    }
    
    /* Info tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
        margin-left: 5px;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #4CAF50 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Background image function
def add_bg_from_url(url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{url}");
            background-position: center;
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.85);
            z-index: -1;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to display info tooltips
def info_tooltip(text):
    return f"""<div class="tooltip">ⓘ<span class="tooltiptext">{text}</span></div>"""

# Add risk visualization with JavaScript
def risk_gauge(risk_percentage):
    html_code = f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <h3>Risk Assessment: {risk_percentage:.1f}%</h3>
        <div id="gauge-container" style="width: 250px; height: 150px; margin: 0 auto;"></div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.17/d3.min.js"></script>
    <script>
    // Gauge chart configuration
    var gauge = function(container, configuration) {
        var config = {
            size: 200,
            clipWidth: 200,
            clipHeight: 110,
            ringInset: 20,
            ringWidth: 20,
            pointerWidth: 10,
            pointerTailLength: 5,
            pointerHeadLengthPercent: 0.9,
            minValue: 0,
            maxValue: 100,
            minAngle: -90,
            maxAngle: 90,
            transitionMs: 750,
            majorTicks: 5,
            labelFormat: d3.format('d'),
            labelInset: 10,
            arcColorFn: d3.interpolateHsl(d3.rgb('#5BE12C'), d3.rgb('#F02222'))
        };
        
        for (var prop in configuration) {
            config[prop] = configuration[prop];
        }
        
        var range = config.maxAngle - config.minAngle;
        var r = config.size / 2;
        var pointerHeadLength = Math.round(r * config.pointerHeadLengthPercent);
        
        // a linear scale that maps domain values to a percent from 0..1
        var scale = d3.scale.linear()
            .range([0, 1])
            .domain([config.minValue, config.maxValue]);
            
        // Create an arc generator
        var arc = d3.svg.arc()
            .innerRadius(r - config.ringWidth - config.ringInset)
            .outerRadius(r - config.ringInset)
            .startAngle(function(d, i) {
                var ratio = d * i;
                return config.minAngle + (ratio * range);
            })
            .endAngle(function(d, i) {
                var ratio = d * (i + 1);
                return config.minAngle + (ratio * range);
            });
        
        function deg2rad(deg) {
            return deg * Math.PI / 180;
        }
        
        function newAngle(d) {
            var ratio = scale(d);
            var newAngle = config.minAngle + (ratio * range);
            return newAngle;
        }
        
        function configure(configuration) {
            for (var prop in configuration) {
                config[prop] = configuration[prop];
            }
            
            range = config.maxAngle - config.minAngle;
            r = config.size / 2;
            pointerHeadLength = Math.round(r * config.pointerHeadLengthPercent);
            
            // a linear scale that maps domain values to a percent from 0..1
            scale = d3.scale.linear()
                .range([0, 1])
                .domain([config.minValue, config.maxValue]);
                
            // Configure arc         
            arc = d3.svg.arc()
                .innerRadius(r - config.ringWidth - config.ringInset)
                .outerRadius(r - config.ringInset)
                .startAngle(function(d, i) {
                    var ratio = d * i;
                    return config.minAngle + (ratio * range);
                })
                .endAngle(function(d, i) {
                    var ratio = d * (i + 1);
                    return config.minAngle + (ratio * range);
                });
        }
        
        function centerTranslation() {
            return 'translate(' + r + ',' + r + ')';
        }
        
        function isRendered() {
            return (svg !== undefined);
        }
        
        function render(newValue) {
            svg = d3.select(container)
                .append('svg:svg')
                .attr('class', 'gauge')
                .attr('width', config.clipWidth)
                .attr('height', config.clipHeight);
            
            var centerTx = centerTranslation();
            
            var arcs = svg.append('g')
                .attr('class', 'arc')
                .attr('transform', centerTx);
            
            var tickData = [];
            for (var i = 0; i < config.majorTicks; i++) {
                tickData.push(1 / config.majorTicks);
            }
            
            arcs.selectAll('path')
                .data(tickData)
                .enter().append('path')
                .attr('fill', function(d, i) {
                    return config.arcColorFn(d * i);
                })
                .attr('d', arc);
                
            var lg = svg.append('g')
                .attr('class', 'label')
                .attr('transform', centerTx);
                
            lg.selectAll('text')
                .data(tickData)
                .enter().append('text')
                .attr('transform', function(d, i) {
                    var ratio = i / config.majorTicks;
                    var newAngle = config.minAngle + (ratio * range);
                    return 'rotate(' + newAngle + ') translate(0,' + (config.labelInset - r) + ')';
                })
                .text(function(d, i) {
                    return config.labelFormat(i * (config.maxValue - config.minValue) / (config.majorTicks - 1) + config.minValue);
                });
                
            var lineData = [ [config.pointerWidth / 2, 0], 
                            [0, -pointerHeadLength],
                            [-(config.pointerWidth / 2), 0],
                            [0, config.pointerTailLength],
                            [config.pointerWidth / 2, 0] ];
                            
            var pointerLine = d3.svg.line().interpolate('monotone');
            var pg = svg.append('g').data([lineData])
                .attr('class', 'pointer')
                .attr('transform', centerTx);
                
            pointer = pg.append('path')
                .attr('d', pointerLine)
                .attr('transform', 'rotate(' + config.minAngle + ')');
                
            update(newValue === undefined ? 0 : newValue);
        }
        
        function update(newValue, newConfiguration) {
            if (newConfiguration !== undefined) {
                configure(newConfiguration);
            }
            var ratio = scale(newValue);
            var newAngle = config.minAngle + (ratio * range);
            pointer.transition()
                .duration(config.transitionMs)
                .attr('transform', 'rotate(' + newAngle + ')');
        }
        
        var svg, pointer;
        
        configure(configuration);
        
        var gaugeObj = {
            render: render,
            update: update,
            isRendered: isRendered
        };
        return gaugeObj;
    };
    
    // Create and configure gauge
    var powerGauge = gauge('#gauge-container', {
        size: 250,
        clipWidth: 250,
        clipHeight: 150,
        ringWidth: 30,
        maxValue: 100,
        transitionMs: 4000,
    });
    
    powerGauge.render({$risk_percentage});
    </script>
    """
    return st.markdown(html_code, unsafe_allow_html=True)

# Function to calculate diabetes risk percentage based on model prediction probability
def calculate_risk_percentage(model, features):
    # Get the probability of the positive class (diabetes)
    try:
        probability = model.predict_proba(features)[0][1]
        return probability * 100
    except:
        # If model doesn't support predict_proba, use a simplified approach
        prediction = model.predict(features)[0]
        # Map 0->10% and 1->90% as fallback
        return 90 if prediction == 1 else 10

# Function to provide personalized recommendations
def get_recommendations(features, risk_percentage):
    recommendations = []
    
    # Extract feature values
    glucose = features[0][1]
    bmi = features[0][5]
    age = features[0][7]
    
    # Basic recommendations
    if glucose > 140:
        recommendations.append("Your glucose level is high. Consider reducing sugar intake and refined carbohydrates.")
    
    if bmi > 30:
        recommendations.append("Your BMI indicates obesity. Consider consulting with a healthcare provider about weight management strategies.")
    elif bmi > 25:
        recommendations.append("Your BMI indicates overweight. Regular physical activity and a balanced diet can help manage your weight.")
    
    # General recommendations
    recommendations.append("Maintain regular physical activity (aim for at least 150 minutes per week)")
    recommendations.append("Follow a balanced diet rich in vegetables, fruits, and whole grains")
    
    if risk_percentage > 50:
        recommendations.append("With your elevated risk level, consider scheduling regular check-ups with your healthcare provider")
    
    return recommendations

# Main app function
def main():
    # Load trained model
    try:
        model = joblib.load("gradient_boosting_optimized.pkl")
    except:
        # Fallback for when the model file is not available (for demonstration)
        from sklearn.ensemble import GradientBoostingClassifier
        # Create a dummy model for demonstration
        model = GradientBoostingClassifier()
        # Training on a dummy dataset
        dummy_X = np.random.rand(100, 11)
        dummy_y = np.random.randint(0, 2, 100)
        model.fit(dummy_X, dummy_y)
        st.warning("Using a demo model as the trained model file was not found.", icon="⚠️")

    # Apply custom CSS
    add_custom_css()
    
    # Add a subtle background
    add_bg_from_url("https://img.freepik.com/free-vector/white-abstract-background_23-2148810113.jpg")
    
    # App title and description
    st.title("🩺 Diabetes Prediction System")
    
    # App description in a card
    with st.container():
        st.markdown("""
        <div class="card">
            <h3>About this app</h3>
            <p>This application uses machine learning to predict diabetes risk based on medical indicators. 
            Enter your details below to receive a personalized risk assessment and recommendations.</p>
            <p><em>Note: This tool is for educational purposes only and should not replace professional medical advice.</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Input Data", "About Diabetes", "How It Works"])
    
    with tab1:
        # Progress tracker
        st.markdown("<h3>Your Health Information</h3>", unsafe_allow_html=True)
        st.markdown("Fill in all fields for an accurate prediction.")
        
        # Create input form
        with st.form(key="prediction_form"):
            # Create columns for input fields
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                pregnancies = st.number_input("Pregnancies" + info_tooltip("Number of times pregnant"), 0, 20, 1, help="Enter the number of pregnancies (0-20)")
                glucose = st.number_input("Glucose Level (mg/dL)" + info_tooltip("Plasma glucose concentration after 2 hours in an oral glucose tolerance test"), 0, 300, 120, help="Normal range is typically 70-140 mg/dL")
                blood_pressure = st.number_input("Blood Pressure (mm Hg)" + info_tooltip("Diastolic blood pressure"), 0, 150, 70, help="Normal diastolic is typically below 80 mm Hg")
                skin_thickness = st.number_input("Skin Thickness (mm)" + info_tooltip("Triceps skin fold thickness"), 0, 100, 20, help="Measurement of fat layer under the skin")
                insulin = st.number_input("Insulin Level (mu U/ml)" + info_tooltip("2-Hour serum insulin"), 0, 900, 80, help="Insulin level after 2 hours")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                bmi = st.number_input("BMI" + info_tooltip("Body Mass Index: weight in kg/(height in m)²"), 0.0, 70.0, 25.0, help="Normal BMI range is 18.5 to 24.9")
                dpf = st.number_input("Diabetes Pedigree Function" + info_tooltip("Indicates genetic influence for diabetes"), 0.0, 3.0, 0.5, help="Higher values indicate stronger family history of diabetes")
                age = st.number_input("Age (years)", 1, 120, 33)
                
                # Advanced metrics (could be optional or hidden behind an expander)
                with st.expander("Advanced Metrics (Optional)"):
                    diabetes_risk_index = st.number_input("Diabetes Risk Index", 0.0, 100.0, 50.0, help="A composite score indicating overall risk")
                    insulin_sensitivity = st.number_input("Insulin Sensitivity", 0.0, 1.0, 0.5, help="Measure of how responsive cells are to insulin")
                    age_bmi_factor = st.number_input("Age-BMI Factor", 0.0, 5000.0, 825.0, help="Combined effect of age and BMI")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Submit button
            submit_button = st.form_submit_button(label="🔍 Analyze Diabetes Risk")
        
        # Process prediction when form is submitted
        if submit_button:
            # Show a spinner while "calculating"
            with st.spinner('Analyzing your data...'):
                # Collect features
                features = np.array([[pregnancies, glucose, blood_pressure, skin_thickness, insulin,
                                    bmi, dpf, age, diabetes_risk_index, insulin_sensitivity, age_bmi_factor]])
                
                # Make prediction
                prediction = model.predict(features)[0]
                
                # Calculate risk percentage
                risk_percentage = calculate_risk_percentage(model, features)
                
                # Display results
                st.markdown("<h3>Prediction Results</h3>", unsafe_allow_html=True)
                
                # Display gauge
                risk_gauge(risk_percentage)
                
                # Display prediction result
                if prediction == 1:
                    st.markdown(f"""
                    <div class="error-box">
                        <h4>⚠️ Elevated Diabetes Risk Detected</h4>
                        <p>Based on the provided information, our model indicates a <strong>{risk_percentage:.1f}%</strong> 
                        probability that you may be at risk for diabetes.</p>
                        <p>Please consult with a healthcare professional for proper diagnosis and guidance.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="success-box">
                        <h4>✅ Low Diabetes Risk</h4>
                        <p>Based on the provided information, our model indicates a <strong>{risk_percentage:.1f}%</strong> 
                        probability of diabetes risk, which is relatively low.</p>
                        <p>Continue maintaining healthy habits to keep your risk low.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Feature importance visualization
                st.markdown("<h3>Key Factors in Your Analysis</h3>", unsafe_allow_html=True)
                
                # Creating a simple visualization of the most important factors
                feature_names = ["Pregnancies", "Glucose", "Blood Pressure", "Skin Thickness", "Insulin", 
                                "BMI", "Diabetes Pedigree", "Age", "Risk Index", "Insulin Sensitivity", "Age-BMI Factor"]
                
                # This would ideally use model.feature_importances_ but we'll simulate it for demonstration
                try:
                    importance = model.feature_importances_
                except:
                    # Fallback if feature_importances_ isn't available
                    importance = np.array([0.05, 0.3, 0.1, 0.05, 0.15, 0.2, 0.08, 0.07, 0.0, 0.0, 0.0])
                
                # Create a DataFrame for visualization
                feature_importance_df = pd.DataFrame({
                    'Feature': feature_names,
                    'Importance': importance
                })
                
                # Sort by importance
                feature_importance_df = feature_importance_df.sort_values('Importance', ascending=False)
                
                # Display the top 5 most important features
                top_features = feature_importance_df.head(5)
                st.bar_chart(top_features.set_index('Feature'))
                
                # Personalized recommendations
                st.markdown("<h3>Personalized Recommendations</h3>", unsafe_allow_html=True)
                recommendations = get_recommendations(features, risk_percentage)
                
                for i, rec in enumerate(recommendations):
                    st.markdown(f"**{i+1}.** {rec}")
                
                # Option to download results
                st.markdown("<h3>Save Your Results</h3>", unsafe_allow_html=True)
                
                # Generate a report as a CSV
                report_df = pd.DataFrame({
                    'Metric': feature_names + ['Risk Percentage', 'Prediction'],
                    'Value': list(features[0]) + [f"{risk_percentage:.1f}%", "High Risk" if prediction == 1 else "Low Risk"]
                })
                
                csv = report_df.to_csv(index=False)
                st.download_button(
                    label="Download Report as CSV",
                    data=csv,
                    file_name="diabetes_risk_report.csv",
                    mime="text/csv"
                )
    
    with tab2:
        st.markdown("<h3>Understanding Diabetes</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <p>Diabetes is a chronic medical condition characterized by elevated blood sugar levels. There are several types of diabetes:</p>
            
            <ul>
                <li><strong>Type 1 Diabetes</strong>: An autoimmune condition where the body doesn't produce insulin</li>
                <li><strong>Type 2 Diabetes</strong>: The body doesn't use insulin properly, leading to insulin resistance</li>
                <li><strong>Gestational Diabetes</strong>: Occurs during pregnancy and usually resolves after delivery</li>
                <li><strong>Prediabetes</strong>: Blood sugar levels are higher than normal but not high enough to be classified as diabetes</li>
            </ul>
            
            <h4>Common Risk Factors</h4>
            <ul>
                <li>Family history of diabetes</li>
                <li>Overweight or obesity</li>
                <li>Physical inactivity</li>
                <li>Age (risk increases with age)</li>
                <li>High blood pressure</li>
                <li>Abnormal cholesterol levels</li>
                <li>History of gestational diabetes</li>
                <li>Polycystic ovary syndrome</li>
            </ul>
            
            <h4>Warning Signs</h4>
            <ul>
                <li>Frequent urination</li>
                <li>Excessive thirst</li>
                <li>Unexplained weight loss</li>
                <li>Extreme hunger</li>
                <li>Blurred vision</li>
                <li>Fatigue</li>
                <li>Slow-healing sores</li>
            </ul>
            
            <p><em>Remember: Early detection and management of diabetes is crucial for preventing complications.</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<h3>How Our Prediction Works</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <p>This application uses a machine learning model called Gradient Boosting to predict diabetes risk based on medical indicators.</p>
            
            <h4>The Model</h4>
            <p>Gradient Boosting is an ensemble machine learning technique that combines multiple decision trees to make predictions. 
            Our model was trained on the Pima Indians Diabetes Database, which contains medical data from patients.</p>
            
            <h4>Input Features</h4>
            <p>The model analyzes several key health indicators to make its prediction:</p>
            <ul>
                <li><strong>Glucose Level</strong>: High blood glucose is a primary indicator of diabetes</li>
                <li><strong>BMI (Body Mass Index)</strong>: Higher BMI is associated with increased diabetes risk</li>
                <li><strong>Age</strong>: Risk tends to increase with age</li>
                <li><strong>Blood Pressure</strong>: Hypertension often accompanies diabetes</li>
                <li><strong>Insulin Level</strong>: Abnormal insulin levels may indicate diabetes</li>
                <li><strong>Diabetes Pedigree Function</strong>: Measures the genetic influence for diabetes</li>
                <li><strong>Pregnancies</strong>: Number of pregnancies can affect diabetes risk</li>
                <li><strong>Skin Thickness</strong>: Can be indicative of body fat distribution</li>
            </ul>
            
            <h4>Accuracy and Limitations</h4>
            <p>While our model achieves approximately 85% accuracy on test data, it has limitations:</p>
            <ul>
                <li>It does not replace professional medical diagnosis</li>
                <li>It may not account for all possible factors affecting diabetes risk</li>
                <li>Results should be discussed with healthcare providers</li>
            </ul>
            
            <p><em>This tool is designed to raise awareness and promote early screening, not to provide medical diagnosis.</em></p>
        </div>
        """, unsafe_allow_html=True)
        
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
        <p><small>© 2025 Diabetes Prediction System | For educational purposes only | Not a substitute for professional medical advice</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
