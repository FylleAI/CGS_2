# Fylle AI Onboarding Frontend

Modern conversational interface for automated client onboarding.

## 🎨 Features

- **Conversational UI** - Chat-like interface with suggestion chips
- **Modern Design** - Glassmorphism effects, smooth animations
- **Type-Safe** - Full TypeScript coverage
- **Modular Architecture** - Clean separation of concerns
- **State Management** - Zustand for predictable state
- **API Integration** - React Query for server state
- **Form Validation** - React Hook Form + Yup schemas
- **Responsive** - Mobile-first design

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Onboarding backend running on `http://localhost:8001`

### Installation

```bash
cd onboarding-frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3001`

### Build

```bash
npm run build
```

## 📁 Project Structure

```
onboarding-frontend/
├── src/
│   ├── components/          # React components
│   │   ├── common/          # Reusable components
│   │   ├── onboarding/      # Onboarding-specific
│   │   └── steps/           # Wizard steps
│   ├── services/            # API services
│   │   └── api/             # API clients
│   ├── store/               # Zustand stores
│   ├── types/               # TypeScript types
│   ├── hooks/               # Custom React hooks
│   ├── utils/               # Utility functions
│   ├── config/              # Configuration
│   ├── pages/               # Page components
│   ├── assets/              # Static assets
│   ├── App.tsx              # Root component
│   └── main.tsx             # Entry point
├── public/                  # Public assets
├── .env                     # Environment variables
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
VITE_ONBOARDING_API_URL=http://localhost:8001
VITE_CGS_API_URL=http://localhost:8000
VITE_ENABLE_DASHBOARD=true
VITE_ENABLE_DEBUG_MODE=true
VITE_POLLING_INTERVAL=3000
VITE_MAX_POLLING_ATTEMPTS=40
VITE_ENV=development
```

## 🎯 Onboarding Flow

1. **Company Input** - User provides company information
2. **Research Progress** - AI researches the company
3. **Snapshot Review** - User reviews company snapshot
4. **Questions** - User answers clarifying questions
5. **Execution** - Content generation in progress
6. **Results** - Generated content displayed

## 🛠️ Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Material-UI** - Component library
- **Zustand** - State management
- **React Query** - Server state
- **React Hook Form** - Form management
- **Yup** - Validation
- **Axios** - HTTP client
- **Framer Motion** - Animations

## 📡 API Integration

The frontend integrates with the onboarding backend API:

- `POST /api/v1/onboarding/start` - Start onboarding
- `POST /api/v1/onboarding/{session_id}/answers` - Submit answers
- `GET /api/v1/onboarding/{session_id}/status` - Get status
- `GET /api/v1/onboarding/{session_id}` - Get details

## 🎨 Design System

### Colors

- **Primary**: `#00D084` (Fylle Green)
- **Secondary**: `#6366F1` (Indigo)
- **Success**: `#10B981`
- **Warning**: `#F59E0B`
- **Error**: `#EF4444`

### Typography

- **Font Family**: Inter
- **Headings**: 700 weight
- **Body**: 400 weight
- **Buttons**: 500 weight

## 🧪 Development

### Code Style

```bash
npm run lint
npm run format
```

### Adding New Steps

1. Create component in `src/components/steps/`
2. Add to `OnboardingPage.tsx` switch statement
3. Update `STEP_LABELS` in `constants.ts`

### Adding New API Endpoints

1. Add endpoint to `src/config/api.ts`
2. Add method to `src/services/api/onboardingApi.ts`
3. Create hook in `src/hooks/` if needed

## 📝 License

Proprietary - Fylle AI

## 🤝 Contributing

This is a private project. Contact the team for contribution guidelines.

