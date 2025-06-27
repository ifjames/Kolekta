# Kolekta - Real-Time Cash Exchange Web Application

## Overview

Kolekta is a modern Flask web application that facilitates real-time peer-to-peer cash denomination exchanges. The app addresses the common problem of exact change availability in cash-driven economies like the Philippines, where commuters and vendors frequently face difficulties with cash transactions.

The application enables users to post exchange requests (e.g., trading large bills for smaller denominations) and find nearby users with complementary needs through a proximity-based matching system with interactive maps and real-time notifications.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating
- **Styling**: Modern liquid glass design with CSS3 and CSS variables
- **JavaScript**: Vanilla JavaScript with modern ES6+ features
- **UI Components**: Custom glass-morphism components with blue GCash-inspired theme
- **Maps**: Leaflet.js with OpenStreetMap for geolocation and mapping
- **Animations**: CSS3 transitions and JavaScript-powered smooth animations
- **Icons**: Font Awesome 6 for comprehensive icon support

### Backend Architecture
- **Framework**: Flask 3.x with SQLAlchemy 2.x for database operations
- **Database**: PostgreSQL with connection pooling and pre-ping health checks
- **Authentication**: Session-based authentication with demo user system
- **API Design**: RESTful endpoints for real-time data exchange
- **Geolocation**: Server-side distance calculation and location tracking

### Design System
- **Theme**: GCash-inspired blue color palette with glass morphism effects
- **Typography**: Inter font family with 300-700 weight variations
- **Components**: Reusable glass-effect cards, buttons, and form elements
- **Responsive**: Mobile-first design with desktop enhancements
- **Accessibility**: Focus states, semantic HTML, and screen reader support

## Key Components

### Core Features (To Be Implemented)
1. **Dual Exchange Posting System**: Users can post both desired and offered denominations
2. **Proximity-Based Matching**: Map and list view of nearby users with filtering options
3. **Smart Matching Algorithm**: Prioritizes closest users with exact matches
4. **User Trust & Verification**: ID verification, SMS/email verification, transaction history
5. **Real-Time Notifications**: Instant matching and transaction updates

### Current Implementation
- **Tab Navigation**: Home and Explore screens with haptic feedback
- **Theming System**: Automatic light/dark mode support
- **Responsive Design**: Cross-platform UI components
- **Testing Setup**: Jest configuration with snapshot testing

### Technology Stack
- **Runtime**: Node.js 20 with Python 3.11 support
- **Package Manager**: npm with lock file for dependency management
- **Development Tools**: TypeScript, ESLint, Jest for testing
- **Build System**: Metro bundler for React Native
- **Platform Integration**: Expo plugins for splash screen, router, and native features

## Data Flow

### Current Structure
1. **Navigation Flow**: File-based routing through app directory structure
2. **Theme Management**: Color scheme detection and theme provider integration
3. **Component Communication**: Props-based data flow with theme context

### Planned Data Flow (For Full Implementation)
1. **User Authentication**: Account creation and verification flow
2. **Exchange Posting**: Create and manage exchange requests
3. **Matching Engine**: Real-time proximity-based user matching
4. **Transaction Management**: Secure exchange confirmation and completion
5. **Notification System**: Push notifications for matches and updates

## External Dependencies

### Core Dependencies
- **Expo SDK**: Complete development platform with native API access
- **React Navigation**: Tab navigation with bottom tabs
- **React Native Reanimated**: High-performance animations
- **React Native Gesture Handler**: Native gesture recognition
- **Expo Vector Icons**: Comprehensive icon library

### Development Dependencies
- **TypeScript**: Type safety and enhanced developer experience
- **Jest**: Unit testing framework with Expo integration
- **Babel**: JavaScript transpilation for React Native

### Future Dependencies (For Full App)
- **Real-time Communication**: WebSocket or Firebase for live matching
- **Geolocation Services**: GPS and mapping functionality
- **Push Notifications**: User engagement and match alerts
- **Authentication**: Secure user verification system
- **Database**: User profiles, transaction history, and matching data

## Deployment Strategy

### Development Environment
- **Platform**: Replit with custom run configuration
- **Hot Reload**: Expo development server with proxy setup
- **Testing**: Development builds and Expo Go for device testing
- **Web Preview**: Metro web support for browser testing

### Production Deployment (Planned)
- **Mobile**: Expo Application Services (EAS) for app store deployment
- **Over-the-Air Updates**: Expo Updates for rapid feature deployment
- **Backend**: Cloud hosting for matching algorithms and user data
- **CDN**: Asset delivery for optimal performance

### Build Configuration
- **iOS**: App Store Connect integration with proper provisioning
- **Android**: Google Play Store with adaptive icons and signing
- **Web**: Static site generation with Metro bundler

## Changelog

- June 27, 2025: Initial Expo React Native setup
- June 27, 2025: Complete transformation to Flask web application with modern liquid glass design
  - Implemented GCash-inspired blue theme with glass morphism effects
  - Added geolocation services and interactive mapping with Leaflet.js
  - Built real-time notification system with JavaScript
  - Created responsive design with mobile-first approach
  - Integrated session-based authentication with demo user system
  - Added PostgreSQL database with SQLAlchemy models
  - Implemented exchange request and matching system
- June 27, 2025: Firebase Authentication Integration
  - Replaced demo authentication with secure Firebase email/password authentication
  - Created comprehensive login/signup page with Firebase integration
  - Added automatic user account creation for new Firebase users
  - Implemented proper logout functionality with Firebase sign-out
  - Updated all login buttons and flows to use Firebase authentication
  - Added context processor for Firebase configuration injection
- June 27, 2025: Complete Firestore Backend Migration
  - Migrated from PostgreSQL to Firebase Cloud Firestore for all data storage
  - Created Firestore models and REST API integration for all app data
  - Implemented real-time data queries and cloud-based user management
  - All users, exchange requests, matches, and notifications now stored in Firestore
  - Enabled cloud-based data management through Firebase Console

## User Preferences

Preferred communication style: Simple, everyday language.