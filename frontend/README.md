# SDD Frontend - Phase 1

React + TypeScript frontend for the Spec-Driven Development System Phase 1.

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at [http://localhost:5173](http://localhost:5173)

## Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm test` - Run tests with Vitest
- `npm run lint` - Lint code with ESLint
- `npm run type-check` - Check TypeScript types

## Features

- Intent input form with word count validation (50-500 words)
- Structured specification display
- Error handling with retry capability
- Loading states
- Type-safe API client

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   ├── index.css            # Global styles
│   ├── components/
│   │   ├── IntentInput.tsx  # Intent input form
│   │   ├── SpecOutput.tsx   # Spec display container
│   │   ├── GoalSection.tsx  # Goal display
│   │   ├── EntitiesSection.tsx
│   │   ├── ConstraintsSection.tsx
│   │   ├── AssumptionsSection.tsx
│   │   ├── MetadataSection.tsx
│   │   └── ErrorDisplay.tsx
│   ├── api/
│   │   └── client.ts        # API client
│   ├── types/
│   │   └── spec.ts          # TypeScript interfaces
│   └── hooks/
│       └── useSpecGeneration.ts  # TanStack Query hook
├── tests/
│   ├── setup.ts
│   └── components/
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=5000
```

## Testing

```bash
# Run tests in watch mode
npm test

# Run tests with coverage
npm test -- --coverage
```

## API Integration

The frontend communicates with the backend via:

- `POST /api/v1/spec` - Generate specification from intent
- Proxied through Vite dev server to avoid CORS issues
- Type-safe client using TypeScript interfaces matching OpenAPI schema
