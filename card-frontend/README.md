# Card Frontend - Card Manager UI

Standalone React application for managing and visualizing cards created from the Onboarding flow.

## 🎯 Features

- **Dashboard**: View all cards organized by type (Product, Persona, Campaign, Topic)
- **Card Details**: View detailed information about each card
- **Card Management**: Create, edit, and delete cards
- **Relationships**: Visualize and manage relationships between cards
- **RAG Context**: Export cards as formatted context for LLM integration

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd card-frontend
npm install
```

### Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Update the API URLs to match your backend:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_CARD_API_URL=http://localhost:8000/api/v1/cards
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
src/
├── components/          # React components
│   ├── CardCard.tsx    # Single card display
│   ├── CardGrid.tsx    # Grid of cards
│   └── Header.tsx      # App header
├── pages/              # Page components
│   ├── Dashboard.tsx   # Main dashboard
│   └── CardDetail.tsx  # Card detail view
├── hooks/              # Custom React hooks
│   ├── useCards.ts     # Fetch all cards
│   ├── useCard.ts      # Fetch single card
│   └── useCardRelationships.ts
├── services/           # API clients
│   └── cardApi.ts      # Card Service API client
├── types/              # TypeScript types
│   └── card.ts         # Card types
├── config/             # Configuration
│   ├── api.ts          # API config
│   └── theme.ts        # Material-UI theme
├── App.tsx             # Main app component
└── main.tsx            # Entry point
```

## 🔌 API Integration

The app communicates with the Card Service API at `/api/v1/cards`:

- `GET /api/v1/cards` - List all cards
- `GET /api/v1/cards/{id}` - Get single card
- `POST /api/v1/cards` - Create card
- `PUT /api/v1/cards/{id}` - Update card
- `DELETE /api/v1/cards/{id}` - Delete card
- `GET /api/v1/cards/context/all` - Get all cards by type
- `GET /api/v1/cards/context/rag-text` - Get RAG context

## 🎨 Styling

Uses Material-UI (MUI) for components and styling. Theme is configured in `src/config/theme.ts`.

## 📦 Dependencies

- **React 18** - UI library
- **React Router** - Client-side routing
- **Material-UI** - Component library
- **React Query** - Data fetching and caching
- **Axios** - HTTP client
- **Zod** - Schema validation
- **React Hot Toast** - Notifications
- **Zustand** - State management (optional)

## 🧪 Testing

```bash
npm run type-check
npm run lint
```

## 📝 TODO

- [ ] Card editor page
- [ ] Relationships visualization
- [ ] Export functionality
- [ ] Unit tests
- [ ] E2E tests
- [ ] Dark mode support
- [ ] Internationalization

## 📄 License

MIT

