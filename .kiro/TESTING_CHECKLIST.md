# Testing Checklist - JobSpy Web Application

## Pre-Testing Setup

### ✅ Backend Startup
- [ ] Navigate to Backend folder: `cd Backend`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create .env file: `cp .env.example .env`
- [ ] Start server: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- [ ] Verify startup message: "Uvicorn running on http://0.0.0.0:8000"

### ✅ Frontend Status
- [ ] Frontend already running on http://localhost:5173/
- [ ] No build errors in terminal
- [ ] Browser console shows no critical errors

---

## Phase 1: Backend Health Checks

### Health Endpoint
- [ ] Test: `curl http://localhost:8000/health`
- [ ] Expected: `{"status": "healthy", "app": "JobSpy Web Application", ...}`
- [ ] Status Code: 200

### Root Endpoint
- [ ] Test: `curl http://localhost:8000/`
- [ ] Expected: JSON response with app info
- [ ] Status Code: 200

### API Documentation
- [ ] Open http://localhost:8000/api/docs (Swagger UI)
- [ ] Verify all endpoints are listed
- [ ] Open http://localhost:8000/api/redoc (ReDoc)
- [ ] Verify documentation is readable

---

## Phase 2: Frontend Connection

### API Client Configuration
- [ ] Check `Frontend/src/services/api.ts`
- [ ] Verify baseURL: `http://localhost:8000/api`
- [ ] Verify interceptors are configured

### CORS Verification
- [ ] Open browser DevTools (F12)
- [ ] Go to Network tab
- [ ] Perform any API call from frontend
- [ ] Check response headers for CORS headers:
  - [ ] `Access-Control-Allow-Origin: http://localhost:5173`
  - [ ] `Access-Control-Allow-Credentials: true`
- [ ] No CORS errors in console

### Connection Test
- [ ] Open http://localhost:5173/ in browser
- [ ] Check browser console (F12 → Console tab)
- [ ] Should NOT see "net::ERR_CONNECTION_REFUSED"
- [ ] Should NOT see CORS errors

---

## Phase 3: Authentication Flow

### Registration
- [ ] Navigate to http://localhost:5173/auth/register
- [ ] Fill in form:
  - [ ] Email: `test@example.com`
  - [ ] Password: `TestPassword123!`
  - [ ] Confirm Password: `TestPassword123!`
- [ ] Click Register button
- [ ] Expected outcomes:
  - [ ] Success toast message appears
  - [ ] Redirected to login page OR dashboard
  - [ ] No error messages in console

### Login
- [ ] Navigate to http://localhost:5173/auth/login
- [ ] Fill in form:
  - [ ] Email: `test@example.com`
  - [ ] Password: `TestPassword123!`
- [ ] Click Login button
- [ ] Expected outcomes:
  - [ ] Success toast message appears
  - [ ] Redirected to home page or dashboard
  - [ ] User name appears in header
  - [ ] Token stored in localStorage

### Token Verification
- [ ] Open DevTools → Application → Local Storage
- [ ] Verify `token` key exists
- [ ] Verify `token` value is a JWT (format: `xxx.yyy.zzz`)

### Logout
- [ ] Click logout button in header
- [ ] Expected outcomes:
  - [ ] Redirected to login page
  - [ ] Token removed from localStorage
  - [ ] User info cleared from header

---

## Phase 4: Job Search Functionality

### Search Page Load
- [ ] Navigate to http://localhost:5173/jobs
- [ ] Page loads without errors
- [ ] Search bar is visible
- [ ] Filter panel is visible (if implemented)

### Search Jobs
- [ ] Enter search term: `developer`
- [ ] Click Search button
- [ ] Expected outcomes:
  - [ ] Loading spinner appears
  - [ ] Results load (or "No results" message)
  - [ ] Job cards display with:
    - [ ] Job title
    - [ ] Company name
    - [ ] Location
    - [ ] Job type
    - [ ] Salary (if available)

### Job Details
- [ ] Click on a job card
- [ ] Navigate to job details page
- [ ] Expected outcomes:
  - [ ] Full job description displays
  - [ ] "Save Job" button is visible
  - [ ] "Apply" button is visible (if applicable)
  - [ ] Related jobs section (if implemented)

### Save Job
- [ ] Click "Save Job" button
- [ ] Expected outcomes:
  - [ ] Success toast message
  - [ ] Button state changes (e.g., "Saved" or icon changes)
  - [ ] Job added to saved jobs list

---

## Phase 5: Saved Jobs

### View Saved Jobs
- [ ] Navigate to http://localhost:5173/saved-jobs
- [ ] Expected outcomes:
  - [ ] List of saved jobs displays
  - [ ] Each job shows save/unsave button
  - [ ] Empty state message if no saved jobs

### Remove Saved Job
- [ ] Click "Remove" or "Unsave" button on a saved job
- [ ] Expected outcomes:
  - [ ] Success toast message
  - [ ] Job removed from list
  - [ ] List updates immediately

---

## Phase 6: Alerts

### Create Alert
- [ ] Navigate to http://localhost:5173/alerts
- [ ] Click "Create Alert" button
- [ ] Fill in alert form:
  - [ ] Keywords: `python developer`
  - [ ] Location: `Remote`
  - [ ] Job Type: `Full-time`
- [ ] Click Create button
- [ ] Expected outcomes:
  - [ ] Success toast message
  - [ ] Alert appears in list
  - [ ] Alert shows all entered criteria

### View Alerts
- [ ] Alerts page displays all created alerts
- [ ] Each alert shows:
  - [ ] Keywords
  - [ ] Location
  - [ ] Job type
  - [ ] Status (Active/Inactive)
  - [ ] Delete button

### Delete Alert
- [ ] Click Delete button on an alert
- [ ] Expected outcomes:
  - [ ] Confirmation dialog (if implemented)
  - [ ] Success toast message
  - [ ] Alert removed from list

---

## Phase 7: User Profile

### View Profile
- [ ] Navigate to http://localhost:5173/profile
- [ ] Expected outcomes:
  - [ ] User information displays:
    - [ ] Email
    - [ ] Full name
    - [ ] Account creation date
  - [ ] Edit button is visible

### Edit Profile
- [ ] Click Edit button
- [ ] Update user information:
  - [ ] Change full name
  - [ ] Update other fields
- [ ] Click Save button
- [ ] Expected outcomes:
  - [ ] Success toast message
  - [ ] Profile updates immediately
  - [ ] Changes persist on page reload

---

## Phase 8: UI/UX Features

### Theme Toggle
- [ ] Click theme toggle button (sun/moon icon)
- [ ] Expected outcomes:
  - [ ] Page switches to dark mode
  - [ ] All components have dark mode styling
  - [ ] Theme preference saved to localStorage
  - [ ] Theme persists on page reload

### Responsive Design
- [ ] Test on different screen sizes:
  - [ ] Desktop (1920x1080)
  - [ ] Tablet (768x1024)
  - [ ] Mobile (375x667)
- [ ] Expected outcomes:
  - [ ] Layout adapts properly
  - [ ] Navigation works on all sizes
  - [ ] Forms are usable on mobile
  - [ ] No horizontal scrolling

### Toast Notifications
- [ ] Perform actions that trigger toasts:
  - [ ] Login success
  - [ ] Save job
  - [ ] Create alert
  - [ ] Delete item
- [ ] Expected outcomes:
  - [ ] Toast appears in bottom-right corner
  - [ ] Toast shows appropriate message
  - [ ] Toast auto-dismisses after 3-5 seconds
  - [ ] Multiple toasts stack properly

### Loading States
- [ ] Perform slow operations:
  - [ ] Search jobs
  - [ ] Load profile
  - [ ] Create alert
- [ ] Expected outcomes:
  - [ ] Loading spinner appears
  - [ ] Buttons are disabled during loading
  - [ ] Loading state clears when complete

### Error Handling
- [ ] Trigger errors:
  - [ ] Invalid login credentials
  - [ ] Network error (disconnect backend)
  - [ ] Invalid form input
- [ ] Expected outcomes:
  - [ ] Error message displays
  - [ ] Error toast appears
  - [ ] User can retry action
  - [ ] No console errors

---

## Phase 9: Browser Console

### No Critical Errors
- [ ] Open DevTools (F12)
- [ ] Go to Console tab
- [ ] Expected outcomes:
  - [ ] No red error messages
  - [ ] No "undefined" errors
  - [ ] No CORS errors
  - [ ] No 404 errors for resources

### Network Requests
- [ ] Go to Network tab
- [ ] Perform various actions
- [ ] Expected outcomes:
  - [ ] All API requests return 200/201 status
  - [ ] No failed requests (red)
  - [ ] Response times are reasonable (<1s)
  - [ ] CORS headers present on responses

---

## Phase 10: Performance

### Page Load Time
- [ ] Measure initial page load time
- [ ] Expected: < 3 seconds
- [ ] Check Network tab for:
  - [ ] HTML loads first
  - [ ] CSS loads
  - [ ] JavaScript loads
  - [ ] Images load

### API Response Time
- [ ] Check Network tab for API calls
- [ ] Expected response times:
  - [ ] Search: < 2 seconds
  - [ ] Login: < 1 second
  - [ ] Save job: < 1 second
  - [ ] Load profile: < 1 second

### Memory Usage
- [ ] Open DevTools → Performance
- [ ] Record page interactions for 30 seconds
- [ ] Expected outcomes:
  - [ ] No memory leaks
  - [ ] Memory usage stable
  - [ ] No excessive garbage collection

---

## Phase 11: Data Persistence

### LocalStorage
- [ ] Open DevTools → Application → Local Storage
- [ ] Verify stored data:
  - [ ] `token` - JWT token
  - [ ] `theme` - Theme preference
  - [ ] Any other app data
- [ ] Reload page
- [ ] Verify data persists

### Session Persistence
- [ ] Login to application
- [ ] Reload page (F5)
- [ ] Expected outcomes:
  - [ ] User remains logged in
  - [ ] User info displays
  - [ ] No redirect to login

---

## Phase 12: Accessibility

### Keyboard Navigation
- [ ] Tab through page elements
- [ ] Expected outcomes:
  - [ ] All interactive elements are focusable
  - [ ] Focus indicator is visible
  - [ ] Tab order is logical
  - [ ] Can submit forms with Enter key

### Screen Reader (Optional)
- [ ] Use browser screen reader
- [ ] Expected outcomes:
  - [ ] Page structure is announced
  - [ ] Form labels are associated
  - [ ] Buttons have descriptive text
  - [ ] Images have alt text

### Color Contrast
- [ ] Check text contrast ratios
- [ ] Expected: WCAG AA standard (4.5:1 for normal text)
- [ ] Use browser DevTools or online tools

---

## Phase 13: Security

### Password Security
- [ ] Verify passwords are not logged
- [ ] Check Network tab - password not in requests
- [ ] Verify password hashing on backend

### Token Security
- [ ] Verify JWT token in localStorage
- [ ] Token should not contain sensitive data
- [ ] Token should expire after set time

### HTTPS (Production Only)
- [ ] Verify HTTPS is used
- [ ] Check certificate validity
- [ ] Verify no mixed content warnings

---

## Phase 14: Cross-Browser Testing

### Chrome/Chromium
- [ ] [ ] All tests pass
- [ ] [ ] No console errors

### Firefox
- [ ] [ ] All tests pass
- [ ] [ ] No console errors

### Safari (if available)
- [ ] [ ] All tests pass
- [ ] [ ] No console errors

### Edge (if available)
- [ ] [ ] All tests pass
- [ ] [ ] No console errors

---

## Phase 15: Final Verification

### Build Status
- [ ] Run `npm run build` in Frontend folder
- [ ] Expected: Build succeeds with 0 errors
- [ ] Check output size is reasonable

### Backend Status
- [ ] Backend still running without errors
- [ ] No memory leaks in backend
- [ ] Database connections stable

### Documentation
- [ ] All documentation is up-to-date
- [ ] API documentation is accurate
- [ ] Setup instructions are clear

---

## Test Results Summary

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Backend Health | ⬜ | |
| 2. Frontend Connection | ⬜ | |
| 3. Authentication | ⬜ | |
| 4. Job Search | ⬜ | |
| 5. Saved Jobs | ⬜ | |
| 6. Alerts | ⬜ | |
| 7. User Profile | ⬜ | |
| 8. UI/UX Features | ⬜ | |
| 9. Browser Console | ⬜ | |
| 10. Performance | ⬜ | |
| 11. Data Persistence | ⬜ | |
| 12. Accessibility | ⬜ | |
| 13. Security | ⬜ | |
| 14. Cross-Browser | ⬜ | |
| 15. Final Verification | ⬜ | |

**Legend**: ⬜ = Not Started | 🟨 = In Progress | ✅ = Passed | ❌ = Failed

---

## Known Issues & Workarounds

### Issue: Database Connection Error
**Symptom**: Backend crashes with database connection error
**Workaround**: Skip database setup for MVP. Backend will still serve API endpoints.

### Issue: Port Already in Use
**Symptom**: "Address already in use" error
**Workaround**: Kill existing process or use different port

### Issue: CORS Errors
**Symptom**: "Access to XMLHttpRequest blocked by CORS policy"
**Workaround**: Verify both frontend and backend are running on correct ports

---

## Next Steps After Testing

1. ✅ Document any bugs found
2. ✅ Create GitHub issues for bugs
3. ✅ Plan fixes and improvements
4. ✅ Set up CI/CD pipeline
5. ✅ Deploy to staging environment
6. ✅ Perform user acceptance testing
7. ✅ Deploy to production

---

**Last Updated**: April 24, 2026
**Status**: Ready for testing
