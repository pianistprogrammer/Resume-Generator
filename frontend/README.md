# JobAlert AI - Frontend

Nuxt 3 frontend for JobAlert AI job matching platform.

## Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
API_BASE_URL=http://localhost:8000/api
```

3. Run development server:
```bash
npm run dev
```

Visit http://localhost:3000

## Project Structure

```
frontend/
├── assets/
│   └── css/
│       └── main.css          # Tailwind styles + design system
├── components/               # Vue components
├── composables/
│   └── useJobs.ts           # Job API composable
├── layouts/
│   └── app.vue              # Main app layout with sidebar
├── pages/
│   ├── index.vue            # Root redirect
│   ├── login.vue            # Login/register page
│   ├── dashboard.vue        # Main dashboard
│   └── ...                  # Other pages
├── stores/
│   └── auth.ts              # Pinia auth store
├── nuxt.config.ts           # Nuxt configuration
├── tailwind.config.js       # Tailwind theme
└── package.json
```

## Design System

### Colors
- **Navy** (#0F172A) - Primary background
- **Emerald** (#059669) - Accent color
- **White/10** - Glass-morphism overlays

### Typography
- **Display**: Syne (headings)
- **Body**: DM Sans (text)
- **Mono**: JetBrains Mono (code)

### Components
- `.glass-card` - Glass-morphism card
- `.btn-primary` - Primary button (emerald)
- `.btn-secondary` - Secondary button (glass)
- `.input-field` - Form input with dark theme
- `.stat-card` - Dashboard stat card
- `.badge` - Status badge

## Key Features

### Auth Store (Pinia)
```ts
import { useAuthStore } from '~/stores/auth'

const authStore = useAuthStore()

// Login
await authStore.login(email, password)

// Register
await authStore.register(email, password, full_name, location)

// Logout
authStore.logout()

// Check auth
authStore.isAuthenticated
authStore.needsOnboarding
```

### Jobs Composable
```ts
const {
  fetchMatches,
  getMatch,
  updateMatchStatus,
  getDashboardStats,
  ingestUrl,
  generateResume,
  getResume,
  scoreColor,
  timeAgo,
  formatSalary
} = useJobs()

// Fetch matches
const matches = await fetchMatches({
  limit: 20,
  status_filter: 'new'
})

// Generate resume
await generateResume(matchId)
```

## Pages

### Implemented
- ✅ `/login` - Login/register with split layout
- ✅ `/dashboard` - Stats grid + recent matches
- ✅ `/` - Root redirect based on auth status

### To Implement
- ⏳ `/onboarding` - 4-step wizard
- ⏳ `/matches` - Full match list with filters
- ⏳ `/job/[id]` - Job detail with resume generation
- ⏳ `/profile` - Profile editor
- ⏳ `/preferences` - Job preferences
- ⏳ `/settings` - Settings and billing

## Build & Deploy

### Production Build
```bash
npm run build
```

### Preview Build
```bash
npm run preview
```

### Deploy to Vercel
```bash
vercel deploy
```

Set environment variable in Vercel:
- `API_BASE_URL` = `https://your-api-url.com/api`

## Development

### Hot Module Replacement
Changes to Vue files automatically reload

### Type Safety
TypeScript enabled for all `.ts` and `.vue` files

### Auto Imports
- Vue composables (ref, computed, etc.)
- Nuxt composables (useRouter, navigateTo, etc.)
- Components (auto-imported from /components)

## Testing

### Manual Testing Flow
1. Open http://localhost:3000
2. Register new account
3. Should redirect to onboarding (when implemented)
4. Complete onboarding
5. View dashboard with stats
6. Browse matches
7. Generate resume for a match
8. Download PDF

## API Integration

All API calls use the `useJobs` composable which:
- Automatically adds auth headers
- Handles errors
- Uses configured API base URL from runtime config

Example:
```ts
const config = useRuntimeConfig()
// config.public.apiBase = 'http://localhost:8000/api'
```
