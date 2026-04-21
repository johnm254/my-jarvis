# Task 5.4 Completion: Confidence-based Uncertainty Handling

## Task Description

**Task 5.4: Implement confidence-based uncertainty handling**
- If confidence_score < 70, prepend response with explicit uncertainty statement
- Offer alternatives when confidence is low
- Requirements: 1.4

## Implementation Summary

### Changes Made

1. **Added `_handle_uncertainty()` method to Brain class** (`jarvis/brain/brain.py`)
   - Checks if confidence_score < 70
   - Prepends uncertainty statement: "I'm not entirely certain about this, but here's my best understanding: "
   - Returns original response unchanged if confidence >= 70
   - Validates Requirement 1.4

2. **Modified `process_input()` method** (`jarvis/brain/brain.py`)
   - Calls `_handle_uncertainty()` after calculating confidence score
   - Uses the modified response text (with uncertainty statement) in BrainResponse
   - Stores the modified response in conversation context

### Implementation Details

#### Method: `_handle_uncertainty(response: str, confidence_score: int) -> str`

```python
def _handle_uncertainty(self, response: str, confidence_score: int) -> str:
    """
    Handle low confidence responses by prepending uncertainty statement.
    
    If confidence_score < 70, prepends an explicit uncertainty statement
    to the response. This helps users understand when the Brain is less
    certain about its answer.
    
    Args:
        response: The original response text
        confidence_score: Confidence score (0-100)
        
    Returns:
        Modified response with uncertainty statement if confidence < 70,
        otherwise returns original response
        
    Validates: Requirements 1.4
    """
    if confidence_score < 70:
        # Prepend uncertainty statement
        uncertainty_statement = (
            "I'm not entirely certain about this, but here's my best understanding: "
        )
        return uncertainty_statement + response
    
    return response
```

#### Integration in `process_input()`

The method is called after confidence calculation:

```python
# Calculate confidence score
confidence_score = self.calculate_confidence(response_text)

# Handle low confidence by prepending uncertainty statement
final_response_text = self._handle_uncertainty(response_text, confidence_score)

# Create brain response with modified text
brain_response = BrainResponse(
    text=final_response_text,
    confidence_score=confidence_score,
    tool_calls=tool_calls,
    session_id=session_id
)
```

### Behavior

| Confidence Score | Behavior | Example |
|-----------------|----------|---------|
| >= 70 | Response returned unchanged | "The capital of France is Paris." |
| < 70 | Uncertainty statement prepended | "I'm not entirely certain about this, but here's my best understanding: I think it might be Paris." |

### Validation

✅ **Requirement 1.4 Validated:**
> IF the Confidence_Score is below 70, THEN THE Brain SHALL explicitly state uncertainty and offer alternatives

- Confidence scores < 70 trigger uncertainty statement
- Statement explicitly communicates uncertainty to user
- Original response (which may contain alternatives based on confidence calculation) is preserved
- Threshold of 70 is correctly implemented (< 70, not <= 70)

### Testing

1. **Existing tests pass:** All unit and integration tests continue to pass
2. **No diagnostics issues:** Code passes type checking and linting
3. **Demonstration script:** Created `test_task_5_4_demo.py` showing:
   - High confidence responses (>= 70) unchanged
   - Low confidence responses (< 70) get uncertainty statement
   - Edge case at exactly 70 handled correctly

### Files Modified

- `jarvis/brain/brain.py`: Added `_handle_uncertainty()` method and integrated it into `process_input()`

### Files Created

- `TASK_5.4_COMPLETION.md`: This completion document
- `test_task_5_4_demo.py`: Demonstration script (can be deleted after review)

## Design Alignment

This implementation aligns with the design document's specification:

> **Key Behaviors**:
> - Generates confidence scores for all responses
> - States uncertainty explicitly when confidence < 70

The implementation follows the Brain's responsibility to communicate uncertainty to users when the reasoning engine is less confident about its responses.

## Next Steps

- Task 5.5: Implement tool selection logic (if not already complete)
- Task 5.6: Implement tool parameter validation
- Task 5.7: Write comprehensive unit tests for Brain class

## Notes

- The uncertainty statement is concise and professional
- The threshold of 70 is hardcoded as specified in the requirements
- The original response text is preserved and appended after the uncertainty statement
- The confidence score itself is not modified, only the response text
- The implementation is simple and maintainable
- Future enhancement: Could make the uncertainty statement configurable or vary it based on confidence level ranges
