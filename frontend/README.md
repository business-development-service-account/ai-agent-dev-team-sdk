# AI Agent SDK Frontend Dashboard

A comprehensive React-based dashboard for monitoring and managing AI agent development teams, built with TypeScript, Ant Design, and modern web technologies.

## Features

### 🎯 Core Functionality
- **Real-time Agent Monitoring**: Live status updates and performance metrics for all AI agents
- **Task Management**: Create, assign, and track tasks across your agent team
- **System Configuration**: Manage system prompts, MCP servers, and global settings
- **Interactive Dashboard**: Comprehensive overview with real-time statistics and visualizations

### 🛠 Technical Stack
- **Framework**: React 18 + TypeScript
- **UI Library**: Ant Design 5.x with custom components
- **Build Tools**: Vite 4.x with hot module replacement
- **State Management**: Zustand with DevTools
- **Styling**: Tailwind CSS 3.x with custom design system
- **Testing**: Vitest + React Testing Library
- **Package Manager**: pnpm 8.x

### 🚀 Performance Features
- **Real-time Updates**: WebSocket integration for live data
- **Code Splitting**: Optimized bundle loading
- **PWA Support**: Progressive Web App capabilities
- **Responsive Design**: Mobile-friendly interface

## Quick Start

### Prerequisites
- Node.js >= 18.0.0
- pnpm >= 8.0.0

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-agent-sdk/frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

### Environment Setup

Create environment files:

**Development (.env.development)**
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8080
VITE_AUTH_URL=http://localhost:8000/auth
VITE_APP_NAME=AI Agent SDK - Development
VITE_ENABLE_PWA=false
VITE_ENABLE_DEBUG_TOOLS=true
```

**Production (.env.production)**
```env
VITE_API_URL=https://api.ai-agent-sdk.com
VITE_WS_URL=wss://ws.ai-agent-sdk.com
VITE_AUTH_URL=https://auth.ai-agent-sdk.com
VITE_APP_NAME=AI Agent SDK
VITE_ENABLE_PWA=true
VITE_ENABLE_DEBUG_TOOLS=false
```

## Development

### Available Scripts

```bash
# Development
pnpm dev              # Start development server
pnpm build            # Build for production
pnpm preview          # Preview production build

# Testing
pnpm test             # Run tests
pnpm test:ui          # Run tests with UI
pnpm test:coverage    # Run tests with coverage

# Code Quality
pnpm lint             # Run ESLint
pnpm lint:fix         # Fix ESLint issues
pnpm type-check       # Run TypeScript type checking
```

### Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── common/          # Generic components
│   ├── layout/          # Layout components
│   └── index.ts
├── pages/               # Page-level components
│   ├── Dashboard.tsx
│   ├── AgentMonitor.tsx
│   ├── TaskManager.tsx
│   ├── SystemConfig.tsx
│   └── Login.tsx
├── hooks/               # Custom React hooks
├── services/            # API and external services
│   ├── agentService.ts
│   ├── taskService.ts
│   ├── systemService.ts
│   └── index.ts
├── stores/              # Zustand state management
│   ├── useAuthStore.ts
│   ├── useAgentStore.ts
│   ├── useTaskStore.ts
│   ├── useSystemStore.ts
│   └── index.ts
├── types/               # TypeScript type definitions
│   ├── agent.ts
│   ├── api.ts
│   ├── ui.ts
│   └── index.ts
├── utils/               # Utility functions
│   ├── apiClient.ts
│   ├── websocket.ts
│   ├── tokenStorage.ts
│   ├── constants.ts
│   └── index.ts
├── styles/              # Global styles and themes
│   └── globals.css
└── test/                # Test utilities and mocks
    ├── setup.ts
    └── mocks/
```

## Architecture

### State Management
The application uses Zustand for state management with separate stores for different domains:

- **useAuthStore**: Authentication and user management
- **useAgentStore**: Agent status and management
- **useTaskStore**: Task creation and tracking
- **useSystemStore**: System configuration and settings

### API Integration
- **RESTful APIs**: Using Axios with automatic token management
- **WebSocket**: Real-time updates for agent status and task progress
- **Error Handling**: Comprehensive error handling with user feedback

### Component Design
- **Component-First**: Reusable, typed components
- **Composition**: Flexible component composition patterns
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance**: Optimized rendering and memoization

## Configuration

### API Configuration
The application connects to backend services via environment variables:

```typescript
// Development
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8080

// Production
VITE_API_URL=https://api.ai-agent-sdk.com
VITE_WS_URL=wss://ws.ai-agent-sdk.com
```

### WebSocket Configuration
Real-time updates are handled through WebSocket connections:

```typescript
const wsConfig: WebSocketConfig = {
  url: import.meta.env.VITE_WS_URL,
  protocols: ['agent-protocol-v1'],
  reconnectInterval: 5000,
  maxReconnectAttempts: 10,
  heartbeatInterval: 30000
};
```

## Authentication

The application uses OAuth2 for authentication with automatic token refresh:

```typescript
// Login
const login = async (username: string, password: string) => {
  const response = await authService.login(username, password);
  // Token automatically stored and managed
};

// API calls automatically include authentication headers
const agents = await agentService.getAgents();
```

## Testing

### Unit Testing
```bash
# Run all tests
pnpm test

# Run tests with coverage
pnpm test:coverage

# Run tests in watch mode
pnpm test --watch
```

### Component Testing Example
```typescript
import { render, screen } from '@test-utils';
import { AgentStatus } from '@/components/common/AgentStatus';

describe('AgentStatus', () => {
  it('displays agent status correctly', () => {
    const mockAgent = {
      status: 'busy',
      agentType: 'research',
      lastActivity: new Date().toISOString()
    };

    render(<AgentStatus {...mockAgent} />);
    expect(screen.getByText('Busy')).toBeInTheDocument();
  });
});
```

## Deployment

### Build Process
```bash
# Build for production
pnpm build

# Preview production build
pnpm preview
```

### Environment Variables
Ensure all required environment variables are set for production:

```bash
# API Configuration
VITE_API_URL=https://your-api-url.com
VITE_WS_URL=wss://your-websocket-url.com
VITE_AUTH_URL=https://your-auth-url.com

# Feature Flags
VITE_ENABLE_PWA=true
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DEBUG_TOOLS=false
```

### Docker Deployment
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Performance

### Optimization Features
- **Code Splitting**: Automatic route-based code splitting
- **Tree Shaking**: Dead code elimination
- **Bundle Analysis**: Built-in bundle analyzer
- **Caching**: Service worker for offline support
- **Compression**: Gzip compression for production

### Monitoring
- **Bundle Size**: Automated bundle size monitoring
- **Performance Metrics**: Core Web Vitals tracking
- **Error Tracking**: Comprehensive error logging
- **Resource Loading**: Optimized resource loading strategies

## Contributing

### Code Style
```bash
# Lint code
pnpm lint

# Fix linting issues
pnpm lint:fix

# Type checking
pnpm type-check
```

### Development Workflow
1. Create feature branch from main
2. Implement changes with tests
3. Run linting and type checking
4. Submit pull request with description

### Guidelines
- Use TypeScript for all new code
- Follow existing component patterns
- Write tests for new features
- Maintain documentation

## Support

### Common Issues

**WebSocket Connection Failed**
- Check WebSocket URL in environment variables
- Ensure backend server is running
- Verify firewall settings

**Authentication Issues**
- Clear browser localStorage
- Check API URL configuration
- Verify OAuth2 provider settings

**Build Errors**
- Ensure all dependencies are installed
- Check Node.js version compatibility
- Verify environment variables

### Getting Help
- Check the documentation
- Review existing issues
- Create new issue with detailed description

## License

MIT License - see LICENSE file for details.

## Changelog

### v1.0.0 (Current)
- Initial release with core functionality
- Real-time agent monitoring
- Task management system
- System configuration interface
- Responsive design
- PWA support