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
            "description": """Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.""",
            "examples": [
                {
                    "input": "nums = [2,7,11,15], target = 9",
                    "output": "[0,1]",
                    "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
                },
                {
                    "input": "nums = [3,2,4], target = 6",
                    "output": "[1,2]",
                    "explanation": "Because nums[1] + nums[2] == 6, we return [1, 2]."
                }
            ],
            "constraints": [
                "2 <= nums.length <= 104",
                "-109 <= nums[i] <= 109",
                "-109 <= target <= 109",
                "Only one valid answer exists."
            ],
            "template": """def twoSum(nums, target):
    # Write your code here
    pass""",
            "test_cases": [
                {"input": {"nums": [2,7,11,15], "target": 9}, "output": [0,1]},
                {"input": {"nums": [3,2,4], "target": 6}, "output": [1,2]},
                {"input": {"nums": [3,3], "target": 6}, "output": [0,1]}
            ],
            "hint": "Try using a hash map to store the complement of each number."
        },
        # Add more array problems here
    ],
    "strings": [
        {
            "id": 2,
            "title": "Valid Palindrome",
            "difficulty": "Easy",
            "category": "Strings",
            "acceptance_rate": "43.8%",
            "description": """A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward.

Alphanumeric characters include letters and numbers.""",
            "examples": [
                {
                    "input": 's = "A man, a plan, a canal: Panama"',
                    "output": "true",
                    "explanation": '"amanaplanacanalpanama" is a palindrome.'
                },
                {
                    "input": 's = "race a car"',
                    "output": "false",
                    "explanation": '"raceacar" is not a palindrome.'
                }
            ],
            "constraints": [
                "1 <= s.length <= 2 * 105",
                "s consists only of printable ASCII characters"
            ],
            "template": """def isPalindrome(s):
    # Write your code here
    pass""",
            "test_cases": [
                {"input": {"s": "A man, a plan, a canal: Panama"}, "output": True},
                {"input": {"s": "race a car"}, "output": False},
                {"input": {"s": " "}, "output": True}
            ],
            "hint": "Consider using two pointers from the start and end of the string."
        }
        # Add more string problems here
    ]
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
    # Sidebar navigation
    st.sidebar.title("Problem Categories")
    category = st.sidebar.selectbox(
        "Select Category",
        ["Arrays & Hashing", "Strings", "Two Pointers", "Stack", "Binary Search", 
         "Sliding Window", "Trees", "Dynamic Programming"]
    )
    
    difficulty = st.sidebar.selectbox(
        "Difficulty",
        ["All", "Easy", "Medium", "Hard"]
    )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if category == "Arrays & Hashing":
            problems = PROBLEMS["arrays"]
        elif category == "Strings":
            problems = PROBLEMS["strings"]
        else:
            st.info("More problems coming soon!")
            return
        
        # Select problem
        problem = problems[0]  # For demo, using first problem
        
        # Problem header
        st.markdown(f"<h1 class='problem-title'>{problem['id']}. {problem['title']}</h1>", unsafe_allow_html=True)
        
        difficulty_class = f"difficulty-{problem['difficulty'].lower()}"
        st.markdown(f"<span class='{difficulty_class}'>{problem['difficulty']}</span> · Acceptance Rate: {problem['acceptance_rate']}", unsafe_allow_html=True)
        
        # Problem description
        st.markdown("### Description")
        st.markdown(f"<div class='markdown-text'>{problem['description']}</div>", unsafe_allow_html=True)
        
        # Examples
        st.markdown("### Examples")
        for i, example in enumerate(problem['examples'], 1):
            st.markdown(f"""<div class='example-box'>
            <strong>Example {i}:</strong><br>
            <strong>Input:</strong> {example['input']}<br>
            <strong>Output:</strong> {example['output']}<br>
            <strong>Explanation:</strong> {example['explanation']}
            </div>""", unsafe_allow_html=True)
        
        # Constraints
        st.markdown("### Constraints")
        for constraint in problem['constraints']:
            st.markdown(f"• {constraint}")
        
        # Code editor
        st.markdown("### Solution")
        code = st_ace(
            value=problem['template'],
            language="python",
            theme="monokai",
            height=300,
            font_size=14,
            key="solution_editor"
        )
        
        # Submit button and test results
        if st.button("Submit", key="submit_solution"):
            with st.spinner("Running tests..."):
                results = run_test_cases(code, problem['test_cases'])
                
                # Display results
                all_passed = all(r['passed'] for r in results)
                total_time = sum(r['execution_time'] for r in results)
                
                if all_passed:
                    st.success(f"✅ All test cases passed! ({total_time:.1f}ms)")
                else:
                    st.error("❌ Some test cases failed")
                
                # Detailed results
                for i, result in enumerate(results, 1):
                    with st.expander(f"Test Case {i}", expanded=not all_passed):
                        st.markdown(f"""```python
Input: {result['input']}
Expected: {result['expected']}
Output: {result['result']}
Time: {result['execution_time']:.1f}ms
```""")
    
    # Right sidebar for problem stats and hints
    with col2:
        st.markdown("### Problem Stats")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""<div class='stats-box'>
            Acceptance<br>
            <strong>{problem['acceptance_rate']}</strong>
            </div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""<div class='stats-box'>
            Difficulty<br>
            <strong class='{difficulty_class}'>{problem['difficulty']}</strong>
            </div>""", unsafe_allow_html=True)
        
        # Hints
        with st.expander("Hint"):
            st.write(problem['hint'])

if __name__ == "__main__":
    main()
