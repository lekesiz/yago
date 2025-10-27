# YAGO v7.1 - Web UI Testing Guide

## 🚀 Quick Start

### 1. Start Backend API Server
```bash
cd yago/web/backend
python clarification_api.py
```
- Server runs on: **http://localhost:8000**
- Health check: http://localhost:8000/api/v1/health
- API docs: http://localhost:8000/docs

### 2. Start Frontend Dev Server
```bash
cd yago/web/frontend
npm install  # First time only
npm run dev
```
- Server runs on: **http://localhost:3000**
- Open in browser: http://localhost:3000

## 🧪 End-to-End Testing Flow

### Phase 1: Start Screen
1. Open http://localhost:3000
2. **Expected**: Beautiful start screen with YAGO logo animation
3. **Test Cases**:
   - ✅ Enter project idea (min 10 chars)
   - ✅ Try submitting with less than 10 chars → Error message
   - ✅ Select depth: Minimal / Standard / Full
   - ✅ Click example ideas to auto-fill
   - ✅ Toggle dark mode (moon/sun icon)
   - ✅ Click "Start Clarification →" button

### Phase 2: Clarification Flow
4. **Expected**: Navigate to clarification screen with first question
5. **Test Cases**:
   - ✅ See project idea in header
   - ✅ See WebSocket connection status (green dot)
   - ✅ See overall progress bar
   - ✅ See category-based progress breakdown
   - ✅ See current question with category badge

6. **Question Types** (test each):
   - **Text**: Multi-line textarea
   - **Select**: Dropdown menu
   - **Multiselect**: Multiple checkboxes
   - **Checkbox**: Single yes/no checkbox
   - **Slider**: Range input with min/max labels

7. **Navigation**:
   - ✅ Answer question → Click "Next →"
   - ✅ Click "← Previous" to go back
   - ✅ Click "Skip Question" (if not required)
   - ✅ Use keyboard: ← → arrows for navigation
   - ✅ Use keyboard: Shift+Enter to skip
   - ✅ When 80%+ complete → "✅ Finish Early" button appears

8. **Real-time Updates**:
   - ✅ Progress bar updates as you answer
   - ✅ Category progress updates
   - ✅ Time remaining estimate updates
   - ✅ WebSocket connection stays green

### Phase 3: Completion Screen
9. **Expected**: Celebration screen with checkmark animation
10. **Test Cases**:
    - ✅ See summary cards (questions answered, completion rate, time)
    - ✅ See project idea
    - ✅ See first 5 key answers preview
    - ✅ Click "Download Brief" → JSON file downloads
    - ✅ Click "Copy to Clipboard" → Brief copied
    - ✅ Click "Continue to Agent Selection →" (TODO: v7.1 future)
    - ✅ Click "Start a New Project" → Returns to start screen

## 🎨 UI/UX Testing

### Dark Mode
- ✅ Toggle dark mode from any screen
- ✅ Dark mode persists on page reload
- ✅ All components look good in both modes
- ✅ Smooth transition between modes

### Responsive Design
- ✅ Test on mobile viewport (375px)
- ✅ Test on tablet viewport (768px)
- ✅ Test on desktop viewport (1920px)
- ✅ All components adapt correctly

### Animations
- ✅ Smooth page transitions
- ✅ Question card fade-in/slide-in
- ✅ Progress bar fills smoothly
- ✅ Loading overlays appear/disappear smoothly
- ✅ Completion checkmark animation

### Accessibility
- ✅ Tab navigation works correctly
- ✅ Focus states visible on all inputs
- ✅ Enter key submits forms
- ✅ Keyboard shortcuts work
- ✅ Screen reader friendly (test with VoiceOver)

## 🐛 Error Handling Testing

### Network Errors
1. Stop backend API server
2. Try starting clarification → Error alert
3. Try answering question → Error alert
4. **Expected**: Graceful error messages, no crashes

### Validation Errors
1. Submit empty required field → Validation error
2. Submit project idea < 10 chars → Validation error
3. **Expected**: Clear error messages, no form submission

### React Errors (Error Boundary)
1. Intentionally break a component (e.g., throw error in render)
2. **Expected**: Error boundary catches it, shows beautiful error screen
3. Click "Try Again" or "Reload Page"

### WebSocket Errors
1. Close WebSocket connection manually (browser dev tools)
2. **Expected**: Connection status turns yellow "Connecting..."
3. WebSocket auto-reconnects

## 📊 Performance Testing

### Load Time
- ✅ First load < 3 seconds
- ✅ Subsequent page navigation < 500ms
- ✅ Question navigation instant

### Bundle Size
- ✅ Check `npm run build` output
- ✅ Main bundle should be < 500KB gzipped
- ✅ No large unused dependencies

### Memory Leaks
- ✅ Open Chrome DevTools → Memory tab
- ✅ Take heap snapshot before starting
- ✅ Complete full flow
- ✅ Take heap snapshot after
- ✅ Compare: should not grow significantly

## 🔧 API Testing

### Manual API Tests
```bash
# 1. Start clarification
curl -X POST http://localhost:8000/api/v1/clarifications/start \
  -H "Content-Type: application/json" \
  -d '{
    "project_idea": "Build a REST API for task management",
    "depth": "standard",
    "user_id": "test-user"
  }'

# Copy session_id from response

# 2. Submit answer
curl -X POST http://localhost:8000/api/v1/clarifications/{session_id}/answer \
  -H "Content-Type: application/json" \
  -d '{
    "answer": "My answer here",
    "skip": false
  }'

# 3. Navigate
curl -X POST http://localhost:8000/api/v1/clarifications/{session_id}/navigate/next

# 4. Complete
curl -X POST http://localhost:8000/api/v1/clarifications/{session_id}/complete

# 5. WebSocket test
wscat -c ws://localhost:8000/ws/{session_id}
```

## 📝 Test Checklist

### Core Functionality
- [ ] Start clarification with valid input
- [ ] Answer all question types
- [ ] Navigate forward and backward
- [ ] Skip optional questions
- [ ] Complete clarification
- [ ] Download brief JSON
- [ ] Start new project

### Edge Cases
- [ ] Empty/invalid project idea
- [ ] Very long project idea (5000+ chars)
- [ ] Skip all questions (if possible)
- [ ] Answer half, reload page, continue
- [ ] Multiple sessions simultaneously
- [ ] Complete in <80% progress

### Integration
- [ ] Backend + Frontend work together
- [ ] WebSocket real-time updates
- [ ] CORS headers allow cross-origin
- [ ] Auto-save drafts work
- [ ] Progress persistence works

### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)

## 🎯 Success Criteria

✅ All test cases pass
✅ No console errors
✅ No React warnings
✅ No TypeScript errors
✅ Smooth animations
✅ Fast response times
✅ Beautiful UI in both light/dark modes
✅ Works on all screen sizes
✅ Keyboard navigation works
✅ Error handling is graceful

## 🐛 Known Issues

_(None yet - add issues as discovered during testing)_

## 📈 Next Steps After Testing

1. Fix any discovered bugs
2. Add unit tests for components
3. Add E2E tests with Cypress/Playwright
4. Optimize performance bottlenecks
5. Add missing features (toast notifications)
6. Polish UX based on feedback

---

**Last Updated**: 2025-10-27
**Version**: YAGO v7.1 Week 3
**Status**: Ready for Testing ✅
