# YAGO v7.1 - Web UI for Clarification Phase

Modern, responsive, and interactive web interface for YAGO's clarification phase.

## 🚀 Features

- ✅ **Interactive Questions** - Support for text, select, multiselect, checkbox, and slider inputs
- ✅ **Real-time Progress** - WebSocket-powered live progress updates
- ✅ **Auto-save** - Draft answers automatically saved to prevent data loss
- ✅ **Dark Mode** - Beautiful dark/light theme toggle
- ✅ **Responsive** - Works on mobile, tablet, and desktop
- ✅ **Keyboard Shortcuts** - Navigate with arrow keys
- ✅ **Smooth Animations** - Framer Motion animations for delightful UX
- ✅ **Type-safe** - Full TypeScript support
- ✅ **Accessibility** - WCAG 2.1 AA compliant

## 📦 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **Framer Motion** - Animations
- **Axios** - API calls
- **React Hot Toast** - Notifications

## 🛠️ Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
src/
├── components/
│   ├── Header.tsx              # App header with logo and theme toggle
│   ├── QuestionCard.tsx        # Question display and input handling
│   ├── ProgressBar.tsx         # Visual progress indicator
│   ├── NavigationControls.tsx  # Next/Previous/Skip buttons
│   └── ClarificationFlow.tsx   # Main container (to be created)
│
├── store/
│   └── clarificationStore.ts   # Zustand state management
│
├── services/
│   └── clarificationApi.ts     # API service layer
│
├── types/
│   └── clarification.ts        # TypeScript type definitions
│
└── App.tsx                     # Root component
```

## 🎨 Components

### QuestionCard

Displays a question and handles user input based on question type.

**Props:**
- `question: QuestionUI` - Question to display
- `onAnswer: (answer: any) => void` - Answer callback
- `initialValue?: any` - Initial value
- `disabled?: boolean` - Disable input

**Supported Question Types:**
- `text` - Textarea input
- `select` - Dropdown menu
- `multiselect` - Multiple checkboxes
- `checkbox` - Single checkbox
- `slider` - Range slider

### ProgressBar

Visual progress indicator with category breakdown.

**Props:**
- `progress: ClarificationProgress` - Progress data

**Features:**
- Overall progress bar
- Progress by category
- Time remaining estimate
- Completion celebration (80%+)

### NavigationControls

Navigation buttons for question flow.

**Props:**
- `onNext: () => void` - Next question
- `onPrevious: () => void` - Previous question
- `onSkip: () => void` - Skip question
- `onFinish: () => void` - Finish early
- `can{Action}: boolean` - Enable/disable buttons
- `loading?: boolean` - Loading state

**Keyboard Shortcuts:**
- `←` Previous
- `→` Next
- `Shift+Enter` Skip

### Header

App header with branding and theme toggle.

**Props:**
- `projectIdea?: string` - Current project idea
- `darkMode: boolean` - Dark mode state
- `onToggleDarkMode: () => void` - Toggle callback

## 🔌 API Integration

The frontend communicates with the FastAPI backend via REST API and WebSocket.

### REST Endpoints

```typescript
// Start clarification
POST /api/v1/clarifications/start
Body: { project_idea: string, depth: string }
Response: ClarificationResponse

// Get current state
GET /api/v1/clarifications/{session_id}
Response: ClarificationResponse

// Submit answer
POST /api/v1/clarifications/{session_id}/answer
Body: { answer: any, skip: boolean }
Response: ClarificationResponse

// Save draft
PUT /api/v1/clarifications/{session_id}/draft
Body: { answers: Record<string, any> }
Response: { status: string, timestamp: string }

// Navigate
POST /api/v1/clarifications/{session_id}/navigate/{direction}
Response: ClarificationResponse

// Complete
POST /api/v1/clarifications/{session_id}/complete
Response: { status: string, brief: any, message: string }
```

### WebSocket

```typescript
// Connect
ws://localhost:8000/ws/{session_id}

// Message Types
type: 'progress_update' | 'notification' | 'ping' | 'pong'

// Example Messages
{ type: 'progress_update', data: { answered: 5, total: 20 } }
{ type: 'notification', message: 'Draft saved', level: 'success' }
```

## 🎯 State Management

Using Zustand for simple, scalable state management.

```typescript
const useClarificationStore = create<ClarificationState>((set, get) => ({
  // State
  sessionId: null,
  currentQuestion: null,
  progress: null,
  answers: {},

  // Actions
  startClarification: async (request) => { /* ... */ },
  submitAnswer: async (answer, skip) => { /* ... */ },
  navigateNext: async () => { /* ... */ },
  navigatePrevious: async () => { /* ... */ },
  // ...
}));

// Usage in components
const { currentQuestion, submitAnswer } = useClarificationStore();
```

## 🎨 Theming

Tailwind CSS with custom theme configuration.

### Colors

- Primary: Blue (`primary-{50-900}`)
- Categories:
  - Basic: Blue
  - Technical: Purple
  - Infrastructure: Green
  - Security: Red
  - Quality: Yellow

### Dark Mode

Toggle between light and dark themes with `toggleDarkMode()`.
Preference is persisted to localStorage.

## ♿ Accessibility

- ARIA labels on interactive elements
- Keyboard navigation support
- Focus management
- Screen reader friendly
- Color contrast WCAG 2.1 AA

## 🚀 Performance

- Code splitting with Vite
- Lazy loading components
- Optimized re-renders with React.memo
- Debounced auto-save
- WebSocket connection pooling

## 📊 Testing (TODO)

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage
npm run test:coverage
```

## 📦 Build

```bash
# Production build
npm run build

# Build output: dist/
# Deploy to any static hosting (Vercel, Netlify, etc.)
```

## 🔐 Environment Variables

```env
# .env.local
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 📝 TODO

- [ ] Add ClarificationFlow main container
- [ ] Implement question history sidebar
- [ ] Add category filter
- [ ] Create start screen
- [ ] Build completion screen
- [ ] Add error boundaries
- [ ] Write unit tests
- [ ] Add E2E tests
- [ ] Optimize bundle size
- [ ] Add PWA support

## 🤝 Contributing

This is part of YAGO v7.1 development. See main YAGO repository for contribution guidelines.

## 📄 License

MIT License - see main YAGO repository

---

**Version:** 7.1.0-alpha
**Status:** In Development (Week 2)
**Part of:** YAGO v7.1 (8-10 weeks timeline)
