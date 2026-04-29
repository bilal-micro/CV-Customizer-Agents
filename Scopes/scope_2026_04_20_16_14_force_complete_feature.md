# Scope: Force Process Complete Feature

**Date**: April 20, 2026 - 16:14
**Status**: Ready for Planning
**Priority**: Medium

---

## 📋 Feature Overview

Add functionality to force a process run to 'completed' status without running any agents. This allows users to:
- Complete processes when agents are failing
- Preserve manual LaTeX input work
- Handle edge cases where the system is stuck
- Maintain flexibility in workflows

---

## 🎯 User Story

As a user, I want to force a process to complete without running agents, so that I can:
- Save my manual work when agents are failing
- Complete a process I'm satisfied with
- Bypass stuck or problematic stages
- Preserve my manual LaTeX input in the job

---

## ✅ Functional Requirements

### Backend Requirements

#### 1. New API Endpoint
**File**: `backend/ats_app/views.py`

**New Action**: `force_complete` in `ProcessRunViewSet`
- **Method**: POST
- **URL**: `/api/process-runs/{id}/force_complete/`
- **Purpose**: Update process status to 'completed' without running agents
- **Allowed from any state**: pending, running, awaiting_manual_input, failed
- **No orchestrator execution**: Direct DB update only

**Behavior**:
1. Get ProcessRun by ID
2. If `manual_latex_input` exists, update `job.latex_cv` with this value
3. Update `ProcessRun.status` to 'completed'
4. Log action: "Process {id} force-completed by user (agent execution bypassed)"
5. Return success message with updated process data

**Error Handling**:
- 400 if ProcessRun doesn't exist
- 500 if database update fails

#### 2. Update API Client
**File**: `frontend/src/api/index.ts`

**New Function**: `forceComplete(processId: string)`
- **Method**: POST
- **Endpoint**: `/api/process-runs/${processId}/force_complete/`
- **Returns**: Promise with success message and updated process data
- **Error Handling**: Throw errors for failed requests

### Frontend Requirements

#### 1. Add Force Complete Button
**File**: `frontend/src/pages/ProcessDetail.tsx`

**Button Placement**:
- For `failed` processes: Show next to existing "Retry Process" button
- For `running`, `awaiting_manual_input`, `pending`: Show in dedicated section
- For `completed` processes: Do not show (already completed)

**Button Styling**:
- Distinct from "Retry Process" button
- Use warning color to indicate bypass action
- Icon: ⚡ (lightning bolt) to indicate force action
- Text: "⚡ Force Complete"

#### 2. Confirmation Dialog
**Implementation**: Native browser `confirm()` dialog

**Dialog Message**:
```
Are you sure you want to force complete this process?

This will:
- Mark the process as completed
- Save your manual LaTeX input (if available)
- Bypass all remaining agent executions
- You will not be able to resume or continue iterating

This action cannot be undone.

Proceed with force completion?
```

**Options**:
- OK: Proceed with force completion
- Cancel: Do nothing

#### 3. State Management
**New State Variable**: `forceCompleting` (boolean)
- Set to `true` when API call is in progress
- Set to `false` when API call completes (success or error)
- Disable button when `forceCompleting` is `true`

**Error Handling**:
- Display error message if API call fails
- Do not update process state on error
- Keep user on current page

---

## 🚫 Non-Functional Requirements

### Constraints
1. **No agent execution**: This feature must not trigger any orchestrator agents
2. **Direct DB update**: Must update database directly, not through orchestrator
3. **Backward compatible**: Must not break existing functionality
4. **No migrations**: Do not require database schema changes

### Performance
1. **Fast response**: API call should complete within 1-2 seconds
2. **No blocking**: Use async/await in frontend, do not block UI

### Security
1. **Authentication**: Respects existing authentication (same as other endpoints)
2. **Authorization**: Only process owner can force complete (inherited from viewset)

---

## 📝 Technical Details

### Backend Implementation

**Location**: `backend/ats_app/views.py` - `ProcessRunViewSet` class

**New Method**:
```python
@action(detail=True, methods=['post'])
def force_complete(self, request, pk=None):
    """
    Force complete a process without running any agents.
    Saves manual LaTeX input to job if available.
    """
    process_run = self.get_object()
    
    try:
        # If manual LaTeX input exists, save it to job
        if process_run.manual_latex_input:
            process_run.job.latex_cv = process_run.manual_latex_input
            process_run.job.save(update_fields=['latex_cv'])
        
        # Update status to completed
        process_run.status = 'completed'
        process_run.save(update_fields=['status'])
        
        logger.info(f"Process {pk} force-completed by user (agent execution bypassed)")
        
        serializer = ProcessRunSerializer(process_run)
        return Response({
            'message': 'Process force-completed successfully',
            'process': serializer.data
        })
    
    except Exception as e:
        logger.error(f"Failed to force complete process {pk}: {e}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

### Frontend Implementation

**Location**: `frontend/src/pages/ProcessDetail.tsx`

**New State**:
```typescript
const [forceCompleting, setForceCompleting] = useState(false);
```

**New Handler**:
```typescript
const handleForceComplete = async () => {
  if (!id) return;
  
  // Confirmation dialog
  const confirmed = window.confirm(
    `Are you sure you want to force complete this process?\n\n` +
    `This will:\n` +
    `- Mark the process as completed\n` +
    `- Save your manual LaTeX input (if available)\n` +
    `- Bypass all remaining agent executions\n` +
    `- You will not be able to resume or continue iterating\n\n` +
    `This action cannot be undone.\n\n` +
    `Proceed with force completion?`
  );
  
  if (!confirmed) return;
  
  setForceCompleting(true);
  setError('');
  try {
    await forceComplete(id);
    await fetchData();
  } catch (error: any) {
    setError(error.response?.data?.error || 'Failed to force complete process');
    console.error('Failed to force complete process:', error);
  } finally {
    setForceCompleting(false);
  }
};
```

**Button Placement** (next to Restart button):
```tsx
{/* Force Complete Button for Failed Processes */}
{processRun.status === 'failed' && (
  <div style={{ marginTop: '24px', textAlign: 'center' }}>
    {/* Existing Restart button */}
    {/* New Force Complete button */}
    <button
      className="btn-primary"
      onClick={handleForceComplete}
      disabled={forceCompleting}
      style={{
        padding: '12px 24px',
        fontSize: '16px',
        backgroundColor: 'var(--warning)',
        opacity: forceCompleting ? 0.5 : 1
      }}
    >
      {forceCompleting ? '⚡ Completing...' : '⚡ Force Complete'}
    </button>
  </div>
)}
```

---

## 🔍 Affected Files

### Backend (2 files)
1. `backend/ats_app/views.py` - Add `force_complete` action to `ProcessRunViewSet`
2. `backend/ats_app/serializers.py` - No changes needed (use existing `ProcessRunSerializer`)

### Frontend (2 files)
1. `frontend/src/api/index.ts` - Add `forceComplete()` function
2. `frontend/src/pages/ProcessDetail.tsx` - Add button, handler, and state

---

## 📊 Success Criteria

### Backend
- ✅ New API endpoint `/api/process-runs/{id}/force_complete/` works
- ✅ Process status changes to 'completed'
- ✅ Manual LaTeX input saved to job if available
- ✅ Action logged properly
- ✅ Error handling works correctly
- ✅ Returns proper response format

### Frontend
- ✅ Force Complete button appears in appropriate states
- ✅ Confirmation dialog shown before action
- ✅ API call completes successfully
- ✅ Process data refreshes after completion
- ✅ Error handling displays user-friendly messages
- ✅ UI remains responsive during API call

### Integration
- ✅ Feature works with existing restart functionality
- ✅ No conflicts with continue_iterating
- ✅ Process can still be viewed after force completion
- ✅ Job's latex_cv updated if manual input existed

---

## ⚠️ Risks and Mitigations

### Risk 1: Accidental Force Completion
**Mitigation**: Confirmation dialog with clear warnings about irreversibility

### Risk 2: Lost Progress
**Mitigation**: Always save manual_latex_input to job.latex_cv before completing

### Risk 3: Database Lock Issues
**Mitigation**: Use simple `update_fields` parameter to minimize lock time

### Risk 4: Confusion with Existing Buttons
**Mitigation**: Distinct styling and clear button text differentiate force complete from restart

---

## 🎨 UI/UX Considerations

### Button Styling
- Use warning color (orange/yellow) to indicate caution
- Lightning bolt icon (⚡) to indicate speed/force action
- Distinct from "Retry Process" (blue) and "Continue Iterating" (primary)

### Placement
- For failed processes: Below existing error message and restart button
- For other states: In dedicated section with explanation

### Feedback
- Show loading state during API call
- Display success/error messages
- Refresh process data automatically on success

---

## 🔄 Workflow Integration

### Before Force Complete
```
Process Status: failed
↓
User sees error message
↓
User has options:
  - Retry Process (run agents from failure point)
  - Force Complete (bypass agents)
```

### After Force Complete
```
User clicks Force Complete
↓
Confirmation dialog
↓
User confirms
↓
API call: POST /api/process-runs/{id}/force_complete/
↓
Backend:
  - Saves manual_latex_input to job (if exists)
  - Updates process status to 'completed'
  - Logs action
↓
Frontend refreshes process data
↓
User sees completed status
↓
User can:
  - View final results
  - Start new analysis
  - View history
  - CANNOT: Continue iterating or restart
```

---

## 📝 Testing Checklist

### Backend Testing
- [ ] Force complete a failed process with manual_latex_input
- [ ] Force complete a failed process without manual_latex_input
- [ ] Force complete a running process
- [ ] Force complete an awaiting_manual_input process
- [ ] Force complete a pending process
- [ ] Attempt to force complete a completed process (should fail)
- [ ] Verify job.latex_cv is updated when manual_latex_input exists
- [ ] Verify job.latex_cv is unchanged when manual_latex_input is empty
- [ ] Test error handling with invalid process ID
- [ ] Verify logging works correctly

### Frontend Testing
- [ ] Force Complete button appears for failed processes
- [ ] Force Complete button appears for other states
- [ ] Confirmation dialog shows correct message
- [ ] Confirming dialog triggers API call
- [ ] Canceling dialog does nothing
- [ ] Button disabled during API call
- [ ] Success message displays after completion
- [ ] Error message displays on failure
- [ ] Process data refreshes after successful completion
- [ ] Process status updates to 'completed' in UI

### Integration Testing
- [ ] Force complete after restarting fails
- [ ] Force complete after multiple failed retries
- [ ] Verify manual_latex_input preserved in job
- [ ] Verify can still view process details
- [ ] Verify cannot continue iterating after force complete
- [ ] Verify cannot restart after force complete

---

**End of Scope Document**