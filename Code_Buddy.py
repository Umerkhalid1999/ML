import streamlit as st
import streamlit.components.v1 as components
from streamlit_ace import st_ace
import json
import time

# Configure page settings
st.set_page_config(layout="wide", page_title="PythonPractice")

# Custom CSS for LeetCode-like styling
st.markdown("""
<style>
    .problem-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .difficulty-easy {
        color: #00b8a3;
        font-weight: bold;
    }
    .difficulty-medium {
        color: #ffc01e;
        font-weight: bold;
    }
    .difficulty-hard {
        color: #ff375f;
        font-weight: bold;
    }
    .success-text {
        color: #00b8a3;
    }
    .failed-text {
        color: #ff375f;
    }
    .stats-box {
        background-color: #f7f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 5px;
    }
    .example-box {
        background-color: #f7f9fa;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .markdown-text {
        font-size: 16px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Problem database
PROBLEMS = {
    "arrays": [
        {
            "id": 1,
            "title": "Two Sum",
            "difficulty": "Easy",
            "category": "Arrays & Hashing",
            "acceptance_rate": "49.2%",
            "description": """Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.""",
            "examples": [
                {
                    "input": "nums = [2,7,11,15], target = 9",
                    "output": "[0,1]",
                    "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
                }
            ],
            "template": """def twoSum(nums, target):
    # Write your code here
    pass""",
            "test_cases": [
                {"input": {"nums": [2,7,11,15], "target": 9}, "output": [0,1]},
                {"input": {"nums": [3,2,4], "target": 6}, "output": [1,2]}
            ],
            "hint": "Try using a hash map to store the complement of each number."
        },
        # More problems here...
    ]
}

# Level tracker (store progress)
LEVEL_PROGRESS = {
    "user_level": 1,
    "completed_levels": [False, False, False],  # Track completion of levels (Level 1, Level 2, etc.)
}

def run_test_cases(code, test_cases):
    """Execute test cases and return results"""
    results = []
    namespace = {}
    
    try:
        # Execute the code in a new namespace
        exec(code, namespace)
        
        # Get function name from the code
        func_name = code.split('def ')[1].split('(')[0]
        
        # Run each test case
        for test in test_cases:
            start_time = time.time()
            try:
                result = namespace[func_name](**test['input'])
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                
                passed = result == test['output']
                results.append({
                    'passed': passed,
                    'input': test['input'],
                    'expected': test['output'],
                    'result': result,
                    'execution_time': execution_time
                })
            except Exception as e:
                results.append({
                    'passed': False,
                    'input': test['input'],
                    'expected': test['output'],
                    'result': f"Error: {str(e)}",
                    'execution_time': 0
                })
    except Exception as e:
        results.append({
            'passed': False,
            'input': "Code compilation",
            'expected': "Valid Python code",
            'result': f"Error: {str(e)}",
            'execution_time': 0
        })
    
    return results

def main():
    # Level progress handling
    st.sidebar.title("LeetCode Levels")
    user_level = LEVEL_PROGRESS["user_level"]
    completed_levels = LEVEL_PROGRESS["completed_levels"]

    # Sidebar to display current level
    st.sidebar.write(f"Current Level: {user_level}")
    if user_level < len(completed_levels) and completed_levels[user_level - 1]:
        st.sidebar.markdown("### 🎉 Level Unlocked!")
        LEVEL_PROGRESS["user_level"] += 1  # Unlock next level

    # Category selection and problem handling
    category = st.sidebar.selectbox("Select Category", ["Arrays & Hashing", "Strings", "Two Pointers", "Stack", "Binary Search"])

    if category == "Arrays & Hashing":
        problems = PROBLEMS["arrays"]
    else:
        st.info("More problems coming soon!")
        return
    
    problem = problems[0]  # Use first problem for simplicity
    
    # Display problem details
    st.markdown(f"<h1 class='problem-title'>{problem['id']}. {problem['title']}</h1>", unsafe_allow_html=True)
    difficulty_class = f"difficulty-{problem['difficulty'].lower()}"
    st.markdown(f"<span class='{difficulty_class}'>{problem['difficulty']}</span> · Acceptance Rate: {problem['acceptance_rate']}", unsafe_allow_html=True)
    
    # Problem description
    st.markdown("### Description")
    st.markdown(f"<div class='markdown-text'>{problem['description']}</div>", unsafe_allow_html=True)
    
    # Example cases
    st.markdown("### Examples")
    for i, example in enumerate(problem['examples'], 1):
        st.markdown(f"""<div class='example-box'>
        <strong>Example {i}:</strong><br>
        <strong>Input:</strong> {example['input']}<br>
        <strong>Output:</strong> {example['output']}<br>
        <strong>Explanation:</strong> {example['explanation']}
        </div>""", unsafe_allow_html=True)
    
    # Code editor
    st.markdown("### Solution")
    code = st_ace(value=problem['template'], language="python", theme="monokai", height=300, font_size=14, key="solution_editor")
    
    # Submit button to test code
    if st.button("Submit", key="submit_solution"):
        with st.spinner("Running tests..."):
            results = run_test_cases(code, problem['test_cases'])
            
            # Display results
            all_passed = all(r['passed'] for r in results)
            total_time = sum(r['execution_time'] for r in results)
            
            if all_passed:
                st.success(f"✅ All test cases passed! ({total_time:.1f}ms)")
                completed_levels[user_level - 1] = True  # Mark current level as completed
            else:
                st.error("❌ Some test cases failed")
            
            # Display detailed results
            for i, result in enumerate(results, 1):
                with st.expander(f"Test Case {i}", expanded=not all_passed):
                    st.markdown(f"""```python
Input: {result['input']}
Expected: {result['expected']}
Output: {result['result']}
Time: {result['execution_time']:.1f}ms
```""")
    
    # Hint for the problem
    with st.expander("Hint"):
        st.write(problem['hint'])

if __name__ == "__main__":
    main()
