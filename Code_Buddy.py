import streamlit as st
from streamlit_ace import st_ace

# Python Basic Questions
PYTHON_BASIC = [
    {
        "title": "1. Two Sum",
        "difficulty": "Easy",
        "question": """Given an array of integers nums and a target, return indices of two numbers that add up to target.

Example 1:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1]

Example 2:
Input: nums = [3,2,4], target = 6
Output: [1,2]

Constraints:
• 2 <= nums.length <= 10^4
• -10^9 <= nums[i] <= 10^9
• -10^9 <= target <= 10^9
""",
        "template": """def twoSum(nums, target):
    # Your code here
    pass""",
        "test_cases": [
            {
                "input": "nums = [2,7,11,15], target = 9",
                "output": "[0,1]"
            },
            {
                "input": "nums = [3,2,4], target = 6",
                "output": "[1,2]"
            },
            {
                "input": "nums = [3,3], target = 6",
                "output": "[0,1]"
            }
        ]
    },
    {
        "title": "2. Palindrome Number",
        "difficulty": "Easy",
        "question": """Given an integer x, return true if x is a palindrome, and false otherwise.

Example 1:
Input: x = 121
Output: true
Explanation: 121 reads as 121 from left to right and from right to left.

Example 2:
Input: x = -121
Output: false
Explanation: From left to right, it reads -121. From right to left, it reads 121-. Therefore it is not a palindrome.

Constraints:
• -2^31 <= x <= 2^31 - 1
""",
        "template": """def isPalindrome(x):
    # Your code here
    pass""",
        "test_cases": [
            {
                "input": "x = 121",
                "output": "true"
            },
            {
                "input": "x = -121",
                "output": "false"
            },
            {
                "input": "x = 10",
                "output": "false"
            }
        ]
    }
]

# Python Intermediate Questions
PYTHON_INTERMEDIATE = [
    {
        "title": "1. Longest Substring Without Repeating Characters",
        "difficulty": "Medium",
        "question": """Given a string s, find the length of the longest substring without repeating characters.

Example 1:
Input: s = "abcabcbb"
Output: 3
Explanation: The answer is "abc", with the length of 3.

Example 2:
Input: s = "bbbbb"
Output: 1
Explanation: The answer is "b", with the length of 1.

Constraints:
• 0 <= s.length <= 5 * 10^4
• s consists of English letters, digits, symbols and spaces.
""",
        "template": """def lengthOfLongestSubstring(s):
    # Your code here
    pass""",
        "test_cases": [
            {
                "input": 's = "abcabcbb"',
                "output": "3"
            },
            {
                "input": 's = "bbbbb"',
                "output": "1"
            },
            {
                "input": 's = "pwwkew"',
                "output": "3"
            }
        ]
    }
]

# Python Advanced Questions
PYTHON_ADVANCED = [
    {
        "title": "1. Median of Two Sorted Arrays",
        "difficulty": "Hard",
        "question": """Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.

Example 1:
Input: nums1 = [1,3], nums2 = [2]
Output: 2.00000
Explanation: merged array = [1,2,3] and median is 2.0

Example 2:
Input: nums1 = [1,2], nums2 = [3,4]
Output: 2.50000
Explanation: merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5

Constraints:
• nums1.length == m
• nums2.length == n
• 0 <= m <= 1000
• 0 <= n <= 1000
• 1 <= m + n <= 2000
""",
        "template": """def findMedianSortedArrays(nums1, nums2):
    # Your code here
    pass""",
        "test_cases": [
            {
                "input": "nums1 = [1,3], nums2 = [2]",
                "output": "2.0"
            },
            {
                "input": "nums1 = [1,2], nums2 = [3,4]",
                "output": "2.5"
            }
        ]
    }
]

def run_tests(code, test_cases):
    """Simple test runner that returns results for each test case"""
    results = []
    try:
        # Create namespace for code execution
        namespace = {}
        exec(code, namespace)
        
        # Get the function name
        function_name = code.split('def ')[1].split('(')[0]
        
        # Run each test case
        for test in test_cases:
            try:
                # Create a new namespace for each test
                test_namespace = dict(namespace)
                # Execute the test input
                exec(f"result = {function_name}({test['input'].split('=')[1].strip()})", test_namespace)
                # Convert result to string for comparison
                result = str(test_namespace['result']).lower()
                # Compare with expected output
                passed = result == test['output'].lower()
                results.append({
                    'input': test['input'],
                    'expected': test['output'],
                    'got': result,
                    'passed': passed
                })
            except Exception as e:
                results.append({
                    'input': test['input'],
                    'expected': test['output'],
                    'got': f"Error: {str(e)}",
                    'passed': False
                })
    except Exception as e:
        results.append({
            'input': 'Code compilation',
            'expected': 'Valid Python code',
            'got': f"Error: {str(e)}",
            'passed': False
        })
    return results

def main():
    st.title("LeetCode-Style Python Practice")
    
    # Level selection
    level = st.selectbox(
        "Select difficulty:",
        ["Easy", "Medium", "Hard"]
    )
    
    # Get questions based on level
    if level == "Easy":
        questions = PYTHON_BASIC
    elif level == "Medium":
        questions = PYTHON_INTERMEDIATE
    else:
        questions = PYTHON_ADVANCED
    
    # Question selection
    question = st.selectbox(
        "Select question:",
        range(len(questions)),
        format_func=lambda x: questions[x]["title"]
    )
    
    current_question = questions[question]
    
    # Display question difficulty
    st.markdown(f"**Difficulty:** {current_question['difficulty']}")
    
    # Display question
    st.markdown("### Problem Description")
    st.markdown(current_question["question"])
    
    # Display example test cases
    st.markdown("### Example Test Cases")
    for i, test in enumerate(current_question["test_cases"], 1):
        st.markdown(f"""**Test Case {i}:**
```
Input: {test['input']}
Output: {test['output']}
```""")
    
    # Code editor
    st.markdown("### Code Editor")
    code = st_ace(
        value=current_question["template"],
        language="python",
        theme="monokai",
        height=200,
        font_size=14
    )
    
    # Run tests button
    if st.button("Submit Solution"):
        results = run_tests(code, current_question["test_cases"])
        
        # Display results
        st.markdown("### Test Results")
        all_passed = True
        
        for i, result in enumerate(results, 1):
            if result['passed']:
                st.success(f"""✅ Test Case {i} Passed
```
Input: {result['input']}
Expected: {result['expected']}
Output: {result['got']}
```""")
            else:
                all_passed = False
                st.error(f"""❌ Test Case {i} Failed
```
Input: {result['input']}
Expected: {result['expected']}
Got: {result['got']}
```""")
        
        if all_passed:
            st.success("🎉 Congratulations! All test cases passed!")

if __name__ == "__main__":
    main()
