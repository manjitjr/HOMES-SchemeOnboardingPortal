# Onboarding Slot Booking Feature - Implementation Summary

## Overview
Implemented an integrated onboarding slot booking feature where scheme users select a quarterly slot (Jan/Apr/Jul/Nov) as part of scheme submission. Approvers can approve or reject slots with feedback, and users can modify rejected slots and resubmit.

## Architecture

### Database Model Changes

**OnboardingSlot** (Redesigned)
- `scheme_submission_id` (FK) - Links slot to specific scheme submission
- `year` (int) - Year of slot (2026+)
- `slot_month` (int) - Month: 1=Jan, 4=Apr, 7=Jul, 11=Nov
- `slot_month_name` (str) - "January", "April", "July", "November"
- `is_additional` (bool) - False for primary, True for additional slots
- `justification` (text) - Required for multiple slots per scheme
- `technical_go_live` (date) - Technical go-live date
- `business_go_live` (date) - Business go-live date  
- `booked_by_id` (FK) - User who booked the slot
- `approval_status` (str) - pending/approved/rejected
- `approver_comment` (str) - Feedback from approver (e.g., "Please pick July instead")

### API Endpoints

**Scheme Slot Management** (`/api/schemes/{id}/slot`)
- `PUT /api/schemes/{id}/slot` - Create/update primary slot for a submission
  - Validates: no backdating, valid months (1,4,7,11), go-live dates ≥ slot month
  - Sets status to "pending" when created/updated
  - Only works for draft/rejected submissions
  
- `GET /api/schemes/{id}/slot` - Retrieve all slots for a submission
  - Returns primary + additional slots with approval status and feedback
  
- `DELETE /api/schemes/{id}/slot/{slot_id}` - Remove additional slot
  - Cannot delete primary slot (use PUT to update)

**Slot Approval** (`/api/schemes/{id}/slot/approve`)
- `POST /api/schemes/{id}/slot/approve` - Approve or reject primary slot
  - Approver can provide feedback (e.g., "Please pick Jul instead")
  - Updates approval_status and approver_comment
  - Sets submission status based on approval workflow

**Scheduling Overview** (`/api/scheduling/`)
- `GET /api/scheduling/overview/{year}` - Calendar view of all approved slots
  - Grouped by quarter (Jan, Apr, Jul, Nov)
  - Non-admin users see only their agency's bookings
  - Shows scheme name, agency, booker, and go-live dates
  
- `GET /api/scheduling/my-bookings` - Current user's agency bookings
  - Returns all slots (pending, approved, rejected) for user's agency
  - Sorted by year and month

### Business Rules Implemented

1. **No Backdating**: Cannot select a quarter in the past
   - If today is 2026-04-15, cannot select Jan/Feb/Mar 2026
   
2. **Go-Live Date Validation**: Cannot set go-live before selected slot month
   - If selecting April 2026 slot, go-live dates must be ≥ 2026-04-01
   
3. **One Slot Per Scheme**: Each submission selects one primary slot
   - Additional slots require justification text explaining why
   
4. **Approval Workflow**: Approvers review and can:
   - **Approve**: Slot is confirmed
   - **Reject with Feedback**: E.g., "Slot not feasible, please pick July instead"
   
5. **Resubmission**: If rejected, scheme users can:
   - Click "Edit Slot" button (appears only after rejection)
   - Select new slot and go-live dates
   - Resubmit for approval

6. **Agency Visibility**:
   - Users see only their agency's bookings
   - Admin sees all agencies
   - Scheme users cannot see other agencies' bookings

## Frontend Components

### Scheme Detail View - Slot Panel

**For Scheme Users (Draft/Rejected Status)**:
1. **Year Selector**: Dropdown (current year + next 2 years)
2. **Quarter Cards**: 4 buttons (January, April, July, November)
   - Disabled for past quarters
   - Highlighted when selected
3. **Go-Live Date Pickers**: Technical & Business dates (HTML5 date input)
   - Min date: First day of selected quarter
4. **Save Slot Button**: Commits selection with validation
5. **Edit Slot Button**: Appears when slot is rejected with feedback

**For Approvers (Pending/Draft Status)**:
- View selected slot with all details
- **Approve Button**: Approves without comment
- **Reject Button**: Opens modal to provide feedback

**Slot Display Card**:
- Month & Year
- Technical and Business go-live dates
- Approval status (pending/approved/rejected)
- Approver feedback if rejected (e.g., "Please pick July instead")

### Scheduling Overview Page

**New Navigation**: Added "Scheduling" tab in header

**Calendar View**:
- Year tabs (current + next 2 years)
- 4 quarter columns (Jan, Apr, Jul, Nov)
- Each shows booked schemes in that slot
- Color-coded by quarter (blue=Jan, purple=Apr, green=Jul, orange=Nov)
- Agency-scoped: users see their agency only, admin sees all

**Booking Card** (per slot):
- Scheme name
- Agency
- Technical & Business go-live dates

## Validation Rules (Backend)

```python
# Prevent backdating
if slot_quarter_start < today:
    raise 400 "Cannot select a slot in the past"

# Prevent go-live before slot month
if tech_date < slot_month_date or biz_date < slot_month_date:
    raise 400 "Go-live dates cannot be before {month} {year}"

# Validate slot month
if slot_month not in [1, 4, 7, 11]:
    raise 400 "Invalid slot month. Must be Jan(1), Apr(4), Jul(7), or Nov(11)"

# Only editable in draft/rejected state
if submission.status not in [draft, rejected]:
    raise 400 "Can only edit slot for draft or rejected submissions"
```

## Testing Checklist

### ✅ Test 1: Create Scheme with Slot Selection
```
1. Login as moh_user (agency=MOH)
2. Create scheme "Test Housing Fund"
3. In scheme detail, slot selection panel appears
4. Select April 2026, set go-live dates (2026-04-15, 2026-05-01)
5. Click "Save Slot"
6. Verify slot appears in approval panel
```

### ✅ Test 2: Submit & Approver Rejects with Feedback
```
1. Click "Submit for Approval" button
2. Status changes to "pending_approval"
3. Login as moh_approver
4. See scheme in list with status badge
5. Click "Reject" button in approval panel
6. Modal appears: "Please select July instead"
7. Confirm rejection
8. Slot status → "rejected" with feedback visible
```

### ✅ Test 3: User Edits & Resubmits After Rejection
```
1. Login back as moh_user
2. Open scheme detail for rejected scheme
3. Slot panel shows feedback: "Please select July instead"
4. "Edit Slot" button appears
5. Click edit, select July 2026, new go-live dates
6. "Save Slot" → status changes back to "pending"
7. Click "Submit for Approval" again
8. Approver sees updated July slot
```

### ✅ Test 4: Prevent Backdating
```
1. Try to select slot month in past (e.g., Jan 2026 if today is 2026-04-15)
2. Button should be disabled with gray color
3. Verify error if manual date entry attempted
```

### ✅ Test 5: Prevent Go-Live Before Slot Month
```
1. Select April 2026 slot
2. Try to set go-live date to March 2026 (before slot month)
3. Get error: "Go-live dates cannot be before April 2026"
4. Set to April 15 → works
```

### ✅ Test 6: Admin Scheduling Overview
```
1. Login as admin user
2. Click "Scheduling" nav tab
3. See calendar with approved slots from all agencies
4. Filter by year using dropdown (2026, 2027, etc.)
5. Each quarter column shows all booked schemes
6. Color-coded by agency (visual distinction)
```

### ✅ Test 7: Agency-Scoped Access
```
1. Login as msf_user (agency=MSF)
2. Scheduling overview shows only MSF bookings
3. Cannot see MOH or MOE schemes
4. Admin login shows all agencies
```

## Files Modified/Created

### Backend
- ✅ `app/models.py` - Redesigned OnboardingSlot model with scheme_submission_id FK
- ✅ `app/routers/schemes.py` - Added slot management endpoints (PUT/GET/DELETE)
- ✅ `app/routers/schemes.py` - Added slot approval endpoint (POST approve)
- ✅ `app/routers/scheduling.py` - **NEW** - Calendar overview & my-bookings endpoints
- ✅ `app/main.py` - Registered scheduling router

### Frontend
- ✅ `app/static/index.html` - Added renderSlotPanel() function
- ✅ `app/static/index.html` - Added renderSchedulingPage() function
- ✅ `app/static/index.html` - Added slot management functions (saveSlot, approveSlot, rejectSlotModal)
- ✅ `app/static/index.html` - Added scheduling overview functions (loadSchedulingOverview, renderSchedulingOverview)
- ✅ `app/static/index.html` - Added "Scheduling" nav tab
- ✅ `app/static/index.html` - Updated scheme detail layout to include slot panel above approval panel

## Key Implementation Details

### One Slot Per Submission
Each SchemeSubmission has ONE primary OnboardingSlot (is_additional=False). Additional slots require justification and are rarely used.

### Approval Status Flow
```
Draft → (no slot yet)
   ↓
User selects slot → approval_status="pending"
   ↓
Approver reviews → Can approve or reject
   ↓
If approved: approval_status="approved" (scheme advances)
If rejected: approval_status="rejected" + approver_comment (user can edit & resubmit)
   ↓
User edits rejected slot → approval_status resets to "pending"
   ↓
Resubmit for approval...
```

### Date Validation Strategy
- **Disable past quarters** in UI button grid
- **Prevent go-live before slot month** with validation
- **Show user-friendly error messages** for failures
- **Use HTML5 date inputs** with min attribute for browser-level validation

### Agency Scoping
- All queries filter by `user.agency` unless `user.is_admin()`
- Admin (final_approver) role bypasses agency filtering
- Ensures data isolation between agencies

## Performance Considerations

- Slot selection using simple date objects (no pre-seed required)
- Quarters are calculated on-the-fly (no lookup table needed)
- Approval queries use selectinload for efficient relationship loading
- Calendar view groups approved slots by quarter for efficient rendering

## Future Enhancements

1. **Capacity Limits**: Add `max_schemes_per_slot` field if needed
2. **Conflict Detection**: Warn if too many schemes book same quarter
3. **Email Notifications**: Notify users when slots are approved/rejected
4. **Bulk Operations**: Allow admin to batch-approve slots
5. **Slot History**: Track all slot changes with timestamps
6. **Calendar Conflict**: Check if go-live dates overlap with other scheme deployments

## Known Limitations

- No capacity management (any number of schemes can book same slot)
- Additional slots not fully implemented in UI (model ready, but interface not added)
- No notification emails sent on approval/rejection
- Scheduling view only shows approved slots (not pending)
- No drag-drop to change slots once approved
